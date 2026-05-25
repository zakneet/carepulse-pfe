from app import app

if __name__ == '__main__':
    with app.test_client() as c:
        r = c.get('/medical-staff/planning', query_string={'idPersonnel': 1, 'date': '2026-05-22'})
        print('status:', r.status_code)
        print(r.get_data(as_text=True))
