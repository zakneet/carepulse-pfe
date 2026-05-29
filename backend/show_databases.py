import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password=''
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    for db in cursor:
        print(db[0])
except Exception as e:
    print(e)

