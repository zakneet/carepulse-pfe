import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='gestion_des-rendez-vous5'
    )
    cursor = conn.cursor()
    
    # Afficher les tables
    cursor.execute('SHOW TABLES;')
    tables = cursor.fetchall()
    
    print('='*60)
    print('TABLES EXISTANTES - Base MySQL: gestion_des-rendez-vous5')
    print('='*60)
    
    for (table,) in tables:
        print(f'\n📋 Table: {table}')
        cursor.execute(f'DESC {table};')
        columns = cursor.fetchall()
        print(f'   Colonnes:')
        for col in columns:
            col_name, col_type, nullable, key, default, extra = col
            null_str = 'nullable' if nullable == 'YES' else 'NOT NULL'
            key_str = f' [{key}]' if key else ''
            default_str = f' DEFAULT {default}' if default else ''
            print(f'     - {col_name} ({col_type}) {null_str}{key_str}{default_str} {extra}')
        
        # Afficher le nombre de lignes
        cursor.execute(f'SELECT COUNT(*) FROM {table};')
        count = cursor.fetchone()[0]
        print(f'   📊 Nombre de lignes: {count}')
    
    cursor.close()
    conn.close()
    
    print('\n' + '='*60)
    
except Exception as e:
    print(f'❌ Erreur: {e}')
