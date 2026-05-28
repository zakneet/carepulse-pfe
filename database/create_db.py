import pymysql
conn = pymysql.connect(host='localhost', user='root', password='')
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS `gestion_des_rendez-vous-3`;")
conn.close()
