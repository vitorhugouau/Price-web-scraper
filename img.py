import sqlite3

db_file = "historico_precos.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE historico_precos ADD COLUMN imagem TEXT")
    conn.commit()
    print("Coluna 'imagem' adicionada com sucesso!")
except sqlite3.OperationalError as e:
    print("Aviso:", e)

conn.close()
