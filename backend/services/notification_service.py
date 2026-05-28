import logging
import os
import threading
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_twilio_client = None
_twilio_import_error: Optional[Exception] = None

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PUBLIC_BOOKING_URL_BASE = os.getenv("PUBLIC_BOOKING_URL_BASE", os.getenv("FRONTEND_URL", "http://127.0.0.1:4200")).rstrip("/")


def _get_twilio_client():
    global _twilio_client, _twilio_import_error

    if _twilio_client is not None or _twilio_import_error is not None:
        return _twilio_client

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        _twilio_import_error = RuntimeError("missing Twilio credentials")
        return None

    try:
      from twilio.rest import Client
      _twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as exc:
      _twilio_import_error = exc
      logger.warning("[sms] Twilio client unavailable: %s", exc)
      return None

    return _twilio_client


def build_booking_link(appointment_id: Any) -> str:
    appointment_str = str(appointment_id).strip()
    return f"{PUBLIC_BOOKING_URL_BASE}/booking/{appointment_str}"


def build_confirmation_sms(patient_name: str, booking_link: str) -> str:
    safe_name = (patient_name or "Patient").strip() or "Patient"
    return (
        f"Bonjour {safe_name},\n"
        f"Votre rendez-vous est confirmé.\n"
        f"Accédez à votre espace via ce lien :\n"
        f"{booking_link}"
    )


def send_sms_message(to_phone: str, body: str, context: Optional[Dict[str, Any]] = None) -> bool:
    client = _get_twilio_client()
    if not client or not TWILIO_PHONE_NUMBER:
        logger.info("[sms] SMS skipped (Twilio not configured) context=%s", context or {})
        return False

    phone = (to_phone or "").strip()
    if not phone:
        logger.info("[sms] SMS skipped (missing recipient phone) context=%s", context or {})
        return False

    try:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone,
        )
        logger.info("[sms] SMS sent sid=%s to=%s context=%s", getattr(message, "sid", "unknown"), phone, context or {})
        return True
    except Exception as exc:
        logger.exception("[sms] SMS failed to=%s context=%s error=%s", phone, context or {}, exc)
        return False


def send_booking_confirmation_sms_async(patient_name: str, to_phone: str, appointment_id: Any) -> None:
    booking_link = build_booking_link(appointment_id)
    body = build_confirmation_sms(patient_name, booking_link)

    def _worker():
        send_sms_message(
            to_phone,
            body,
            context={
                "appointmentId": appointment_id,
                "bookingLink": booking_link,
                "purpose": "booking_confirmation",
            },
        )

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
