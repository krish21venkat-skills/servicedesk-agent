from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def reset_password_via_portal(username):
    print("Calling rpa tool..")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            page.goto("http://localhost:8080/admin/reset", timeout=10000)
            page.fill("#username", username, timeout=5000)
            page.click("#reset-btn", timeout=5000)
            result = page.inner_text("#status-message")
            browser.close()
            return result
    except PlaywrightTimeout as e:
        return f"Portal element not found or slow: {e}"
    except Exception as e:
        return f"RPA action failed: {e}"

"""if __name__ == "__main__":
    print(reset_password_via_portal("user_123"))"""