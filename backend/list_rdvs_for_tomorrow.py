from datetime import datetime, timedelta
from app import app
from debug_list_rdvs import list_rdvs

with app.app_context():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Listing RDVs for personnel 1 on {tomorrow}")
    list_rdvs(1, tomorrow)
