"""
services/notifications.py — DOT Notification Service

Sends desktop toast notifications on Windows (via plyer).
Falls back to a console bell + print if plyer is unavailable.
"""

from __future__ import annotations

from core.logger import get_logger

log = get_logger("notifications")

try:
    from plyer import notification as _plyer_notification
    _PLYER_OK = True
except Exception:
    _PLYER_OK = False


def notify(title: str, message: str, timeout: int = 8) -> None:
    """Show a desktop notification.  Falls back to console output."""
    log.info("notify | title=%r message=%r", title, message)

    if _PLYER_OK:
        try:
            _plyer_notification.notify(
                title=title,
                message=message,
                app_name="DOT Assistant",
                timeout=timeout,
            )
            return
        except Exception as exc:
            log.warning("plyer notify failed: %s — using console fallback", exc)

    # Console fallback
    print(f"\a\n[REMINDER] {title}: {message}\n")
