import pymysql
conn = pymysql.connect(host='localhost', user='root', password='')
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS `gestion_des-rendez-vous5`;")
conn.close()
