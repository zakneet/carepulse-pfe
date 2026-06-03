"""OptiClinic — transactional email via Brevo API."""
import os
import json
import urllib.request
import urllib.error

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "noreply@opticlinic.tn")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "OptiClinic")


def _is_configured() -> bool:
    return bool(BREVO_API_KEY and BREVO_SENDER_EMAIL)


def send_transactional_email(to_email: str, subject: str, text_content: str, html_content: str | None = None) -> dict:
    """Send email via Brevo. Returns {success, message, provider, response}."""
    print(f"[brevo] send_transactional_email called with to_email={to_email}, subject={subject}", flush=True)
    
    if not to_email or "@" not in to_email:
        print(f"[brevo] ERROR: Invalid email address: {to_email}", flush=True)
        return {"success": False, "message": "Adresse email invalide", "provider": "brevo"}

    print(f"[brevo] BREVO_API_KEY configured: {bool(BREVO_API_KEY)}", flush=True)
    print(f"[brevo] BREVO_SENDER_EMAIL: {BREVO_SENDER_EMAIL}", flush=True)
    print(f"[brevo] BREVO_SENDER_NAME: {BREVO_SENDER_NAME}", flush=True)
    
    if not _is_configured():
        print("[brevo] ERROR: BREVO_API_KEY not configured — email skipped", flush=True)
        print(f"[brevo] Would send to {to_email}: {subject}", flush=True)
        return {"success": False, "message": "Brevo non configuré", "provider": "brevo", "skipped": True}

    payload = {
        "sender": {"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
        "to": [{"email": to_email.strip()}],
        "subject": subject,
        "textContent": text_content,
    }
    if html_content:
        payload["htmlContent"] = html_content

    print(f"[brevo] Sending request to Brevo API: https://api.brevo.com/v3/smtp/email", flush=True)
    print(f"[brevo] Payload: {json.dumps(payload, indent=2)}", flush=True)
    
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": BREVO_API_KEY,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            print(f"[brevo] SUCCESS: Email sent to {to_email}: {subject}", flush=True)
            print(f"[brevo] Brevo response body: {body}", flush=True)
            return {"success": True, "message": "Email envoyé avec succès", "provider": "brevo", "response": body}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        print(f"[brevo] ERROR: HTTP {exc.code}: {err_body}", flush=True)
        return {"success": False, "message": f"Erreur Brevo HTTP {exc.code}: {err_body}", "provider": "brevo", "error": err_body}
    except Exception as exc:
        print(f"[brevo] ERROR: send failed: {exc}", flush=True)
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Erreur d'envoi: {str(exc)}", "provider": "brevo", "error": str(exc)}


def build_appointment_confirmation_email(
    patient_name: str,
    doctor_name: str,
    speciality: str,
    appointment_date: str,
    appointment_time: str,
    clinic_name: str,
    portal_url: str,
) -> tuple[str, str, str]:
    subject = "Votre rendez-vous OptiClinic est confirmé"
    text = f"""Bonjour {patient_name},

Votre rendez-vous a été confirmé.

Médecin:
{doctor_name}

Spécialité:
{speciality}

Date:
{appointment_date}

Heure:
{appointment_time}

Cabinet:
{clinic_name}

Accéder à votre espace patient sécurisé:
{portal_url}

Depuis cet espace vous pourrez:
• Consulter vos rendez-vous
• Télécharger vos documents
• Voir votre médecin de suivi
• Recevoir des notifications
• Suivre votre parcours médical

L'équipe OptiClinic"""

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Inter,Arial,sans-serif;color:#0f172a;line-height:1.6;max-width:560px;margin:0 auto;padding:24px">
<h2 style="color:#0284c7">Rendez-vous confirmé</h2>
<p>Bonjour <strong>{patient_name}</strong>,</p>
<p>Votre rendez-vous a été confirmé.</p>
<table style="width:100%;border-collapse:collapse;margin:16px 0">
<tr><td style="padding:8px 0;color:#64748b">Médecin</td><td><strong>{doctor_name}</strong></td></tr>
<tr><td style="padding:8px 0;color:#64748b">Spécialité</td><td>{speciality}</td></tr>
<tr><td style="padding:8px 0;color:#64748b">Date</td><td>{appointment_date}</td></tr>
<tr><td style="padding:8px 0;color:#64748b">Heure</td><td>{appointment_time}</td></tr>
<tr><td style="padding:8px 0;color:#64748b">Cabinet</td><td>{clinic_name}</td></tr>
</table>
<p><a href="{portal_url}" style="display:inline-block;background:#0284c7;color:#fff;padding:14px 28px;border-radius:999px;text-decoration:none;font-weight:700">Accéder à mon espace patient</a></p>
<p style="font-size:13px;color:#94a3b8">L'équipe OptiClinic</p>
</body></html>"""
    return subject, text, html  # type: ignore - returns 3 values
