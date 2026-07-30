# VPN Troubleshooting Guide

If your VPN keeps disconnecting after a few minutes, this is usually caused by
an IPv6 conflict with the VPN client. To fix it:

1. Open Network Adapter settings.
2. Right-click your active network connection and select Properties.
3. Uncheck "Internet Protocol Version 6 (TCP/IPv6)".
4. Restart the VPN client and reconnect.

If the VPN fails to connect at all with error code 809, this usually means UDP
port 500 is blocked by a local firewall or your ISP. Try switching the VPN
protocol from IKEv2 to SSTP in the client settings.