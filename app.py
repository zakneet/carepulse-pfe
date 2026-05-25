from datetime import date, datetime, timedelta

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit

from services.route_service import get_route
from services.optimal_departure_service import get_optimal_departure
from services.traffic_service import get_default_start_coords, get_traffic_notice
from services.weather_service import get_current_weather


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.after_request
def add_cors_headers(response):
    # Allow local Angular dev server to fetch demo data during development
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, X-Requested-With'
    return response

TODAY = date.today().isoformat()

CONFIRMED_APPOINTMENTS = [
    {
        "id": 1,
        "patient_name": "Nadine Dhaou",
        "doctor_name": "Dr. Karim Mansouri",
        "date": TODAY,
        "time": "09:30",
        "location": "Tunis",
        "lat": 36.80,
        "lon": 10.10,
    },
    {
        "id": 2,
        "patient_name": "Sami Trabelsi",
        "doctor_name": "Dr. Leila Haddad",
        "date": "2026-05-20",
        "time": "11:00",
        "location": "Ariana",
        "lat": 36.86,
        "lon": 10.19,
    },
    {
        "id": 3,
        "patient_name": "Meriem Chaibi",
        "doctor_name": "Dr. Youssef Khelifi",
        "date": "2026-05-21",
        "time": "14:15",
        "location": "Tunis",
        "lat": 36.80,
        "lon": 10.10,
    },
]

APPOINTMENTS_FOR_VIEW = sorted(CONFIRMED_APPOINTMENTS, key=lambda item: item["date"] != TODAY)


def _parse_appointment_datetime(appointment_date, appointment_time):
    """Build a datetime for a planned appointment using the current local date/time format."""
    try:
        return datetime.fromisoformat(f"{appointment_date}T{appointment_time}")
    except Exception:
        return None


def _build_cabinet_tracking_payload(appointment, now=None):
    """Return the live cabinet tracking state for a single appointment.

    Tracking is only enabled on the appointment day and in the 2-hour window before the slot.
    """
    now = now or datetime.now()
    appointment_dt = _parse_appointment_datetime(appointment.get("date"), appointment.get("time"))
    if not appointment_dt:
        return {
            "enabled": False,
            "status": "unavailable",
            "message": "Suivi indisponible",
            "minutes_to_appointment": None,
            "appointment_id": appointment.get("id"),
        }

    minutes_to_appointment = int((appointment_dt - now).total_seconds() // 60)
    same_day = now.date() == appointment_dt.date()
    in_tracking_window = same_day and 0 <= minutes_to_appointment <= 120

    if not in_tracking_window:
        return {
            "enabled": False,
            "status": "locked",
            "message": "Disponible le jour du rendez-vous à partir de H-2",
            "minutes_to_appointment": minutes_to_appointment,
            "appointment_id": appointment.get("id"),
        }

    if minutes_to_appointment <= 15:
        state = "Accueil prêt"
        tone = "danger"
        message = "Votre créneau approche, le cabinet prépare l’accueil."
    elif minutes_to_appointment <= 60:
        state = "Cabinet en préparation"
        tone = "warning"
        message = "Le cabinet se prépare pour votre rendez-vous."
    else:
        state = "Suivi actif"
        tone = "normal"
        message = "Le suivi du cabinet est actif avant votre venue."

    return {
        "enabled": True,
        "status": "ok",
        "state": state,
        "tone": tone,
        "message": message,
        "minutes_to_appointment": minutes_to_appointment,
        "appointment_id": appointment.get("id"),
    }


@app.route("/")
def home():
    return render_template("index.html", appointments=APPOINTMENTS_FOR_VIEW, today=TODAY)


@app.route('/manifest.json')
def manifest_route():
    """Serve the PWA manifest from the static folder."""
    return send_from_directory('static', 'manifest.json')


@app.route('/offline')
def offline_page():
    """Offline fallback page used by the service worker."""
    return render_template('offline.html')


@app.route('/sw.js')
@app.route('/service-worker.js')
def service_worker():
    """Expose the service worker at the site root so it can control the full origin scope."""
    return send_from_directory('static/js', 'sw.js')


@app.route("/appointments")
def appointments():
    start_lon = request.args.get("start_lon", type=float)
    start_lat = request.args.get("start_lat", type=float)
    patient_origin = (
        start_lon,
        start_lat,
    ) if None not in (start_lon, start_lat) else get_default_start_coords()

    appointments_with_traffic = []
    for appointment in APPOINTMENTS_FOR_VIEW:
        traffic_notice = get_traffic_notice(patient_origin, (appointment["lon"], appointment["lat"]))
        optimal_departure = get_optimal_departure(
            patient_origin,
            (appointment["lon"], appointment["lat"]),
            appointment.get("location"),
        )
        cabinet_tracking = _build_cabinet_tracking_payload(appointment)
        appointments_with_traffic.append({
            **appointment,
            "traffic_notice": traffic_notice,
            "optimal_departure": optimal_departure,
            "cabinet_tracking": cabinet_tracking,
        })

    return render_template(
        "appointments_tracking.html",
        appointments=appointments_with_traffic,
        today=TODAY,
    )


@app.route('/api/appointments')
def api_appointments():
    return jsonify(APPOINTMENTS_FOR_VIEW)


@app.route("/weather")
def weather():
    lat = request.args.get("lat", default=36.8, type=float)
    lon = request.args.get("lon", default=10.1, type=float)

    result = get_current_weather(lat, lon)
    return jsonify(result), result.get("status_code", 200)


@socketio.on("cabinet_status_request")
def cabinet_status_request(payload):
    """Push the live cabinet status for one appointment over Socket.IO."""
    appointment_id = None
    try:
        appointment_id = int((payload or {}).get("appointment_id"))
    except (TypeError, ValueError):
        appointment_id = None

    appointment = next((item for item in APPOINTMENTS_FOR_VIEW if item.get("id") == appointment_id), None)
    if not appointment:
        emit("cabinet_status", {
            "appointment_id": appointment_id,
            "status": "error",
            "message": "Rendez-vous introuvable",
            "enabled": False,
        })
        return

    emit("cabinet_status", _build_cabinet_tracking_payload(appointment))


@app.route("/route")
def route():
    start_lat = request.args.get("start_lat", type=float)
    start_lon = request.args.get("start_lon", type=float)
    end_lat = request.args.get("end_lat", type=float)
    end_lon = request.args.get("end_lon", type=float)

    if None in (start_lat, start_lon, end_lat, end_lon):
        return jsonify({
            "status": "error",
            "message": "Missing route coordinates",
            "distance_km": None,
            "duration_min": None,
        }), 400

    result = get_route((start_lon, start_lat), (end_lon, end_lat))
    http_status = 200 if result.get("status") == "ok" else 503
    return jsonify(result), http_status


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)