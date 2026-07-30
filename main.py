from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import email_reader, llm_router, rag_pipeline, db_tool, api_tool
import ticket_store, email_sender, escalation, memory_store, rpa_tool


class DeskState(TypedDict):
    email: dict
    intent: Optional[dict]
    rag_answer: Optional[str]
    rpa_result: Optional[str]
    needs_escalation: bool
    escalation_reason: Optional[str]


def should_escalate(intent_result, rag_chunks=None):
    """Deterministic escalation rules. Knowledge-lookup questions (leave, VPN,
    password policy, etc.) are judged primarily by whether RAG found a solid,
    single-topic match — NOT by whether the LLM extracted structured entities,
    since policy questions legitimately have none. Entity/confidence checks
    below apply to action-oriented requests where rag_chunks isn't passed."""

    # Explicit LLM classification always escalates regardless of anything else
    if intent_result["intent"] == "escalation_needed":
        return True, "classified as escalation_needed"

    # Knowledge-base style question — judge by retrieval quality
    if rag_chunks is not None:
        if not rag_chunks:
            return True, "no matching content found in knowledge base"

        policy_types = {meta["policy_type"] for _, meta in rag_chunks}
        if len(policy_types) > 1:
            return True, f"query matched multiple unrelated policy areas: {policy_types}"

        return False, None

    # Action-oriented path (no rag_chunks passed in) — fall back to
    # confidence/entities as the signal.
    if intent_result["confidence"] < 0.6:
        return True, "low LLM-reported confidence"

    if not intent_result.get("entities"):
        return True, "no concrete details extracted from the request"

    return False, None


def classify_node(state: DeskState) -> DeskState:
    e = state["email"]
    intent = llm_router.classify_email(e["subject"], e["body"])
    memory_store.append_turn(e["thread_id"], "user", e["body"])
    # Escalation decided after routing/RAG below — default False for now
    return {**state, "intent": intent, "needs_escalation": False, "escalation_reason": None}


def route_after_classify(state: DeskState) -> str:
    intent_result = state["intent"]

    # Password resets go straight to RPA — no point running RAG retrieval
    if intent_result["intent"] == "password_reset":
        return "rpa"

    # Everything else goes through RAG first
    return "rag"


def rag_node(state: DeskState) -> DeskState:
    e = state["email"]
    chunks = rag_pipeline.retrieve(e["body"])
    needs_escalation, reason = should_escalate(state["intent"], chunks)

    if needs_escalation:
        return {**state, "needs_escalation": True, "escalation_reason": reason}

    answer, _ = rag_pipeline.answer_with_context(e["body"])
    return {**state, "rag_answer": answer, "needs_escalation": False}


def rpa_node(state: DeskState) -> DeskState:
    """Handles action-oriented intents (currently: password_reset)."""
    e = state["email"]
    username = e["from"].split("@")[0]
    result = rpa_tool.reset_password_via_portal(username)

    if result.startswith("Portal element not found") or result.startswith("RPA action failed"):
        return {
            **state,
            "rpa_result": result,
            "needs_escalation": True,
            "escalation_reason": f"RPA password reset failed: {result}"
        }

    return {**state, "rpa_result": result, "needs_escalation": False}


def act_node(state: DeskState) -> DeskState:
    e, intent = state["email"], state["intent"]

    if state["needs_escalation"]:
        status = "escalated"
    elif state.get("rpa_result"):
        status = "resolved_via_rpa"
    else:
        status = "resolved"

    ticket_store.create_or_update_ticket(
        e["thread_id"], e["from"], intent["intent"], intent["summary"], status=status)
    return state


def respond_node(state: DeskState) -> DeskState:
    e = state["email"]

    if state["needs_escalation"]:
        # NEW: use Slack interactive escalation
        escalation.escalate_to_slack_with_buttons(
            summary=state["intent"]["summary"],
            thread_id=e["thread_id"],
            reason=state.get("escalation_reason", "low confidence / complex request"),
            requester_email=e["from"]
        )
        reply_body = ("Thanks for reaching out — I've routed this to a specialist "
                      "who will follow up shortly.")
        email_sender.send_reply(e["from"], e["subject"], reply_body)
        memory_store.append_turn(e["thread_id"], "assistant", "escalated")

    elif state.get("rpa_result"):
        reply_body = f"Your password reset has been processed. {state['rpa_result']}"
        email_sender.send_reply(e["from"], e["subject"], reply_body)
        memory_store.append_turn(e["thread_id"], "assistant", reply_body)

    else:
        reply_body = state["rag_answer"]
        email_sender.send_reply(e["from"], e["subject"], reply_body)
        memory_store.append_turn(e["thread_id"], "assistant", reply_body)

    return state


graph = StateGraph(DeskState)
graph.add_node("classify", classify_node)
graph.add_node("rag", rag_node)
graph.add_node("rpa", rpa_node)
graph.add_node("act", act_node)
graph.add_node("respond", respond_node)

graph.set_entry_point("classify")
graph.add_conditional_edges("classify", route_after_classify, {
    "rag": "rag",
    "rpa": "rpa"
})
graph.add_edge("rag", "act")
graph.add_edge("rpa", "act")
graph.add_edge("act", "respond")
graph.add_edge("respond", END)

app = graph.compile()


if __name__ == "__main__":
    rag_pipeline.index_documents()  # build/refresh KB index once at startup
    for e in email_reader.fetch_unread_emails():
        app.invoke({
            "email": e,
            "intent": None,
            "rag_answer": None,
            "rpa_result": None,
            "needs_escalation": False,
            "escalation_reason": None
        })
