import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pytz

db_file = "historico_precos.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS historico_precos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    produto TEXT NOT NULL,
    preco REAL NOT NULL
)
""")
conn.commit()

url = 'https://www.mercadolivre.com.br/apple-watch-series-10-gps-caixa-preta-brilhante-de-aluminio-42-mm-pulseira-esportiva-preta-pm/p/MLB40694304'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "pt-BR,pt;q=0.9"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'lxml')
nome_tag = soup.find('h1', class_='ui-pdp-title')
nome = nome_tag.get_text(strip=True) if nome_tag else 'Nome não encontrado'
preco_meta = soup.find('meta', itemprop='price')
if preco_meta and preco_meta.get('content'):
    preco = float(preco_meta['content'])
else:
    preco = 0.00

agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
data = agora.strftime('%d/%m/%Y %H:%M:%S')

cursor.execute("INSERT INTO historico_precos (data, produto, preco) VALUES (?, ?, ?)", (data, nome, preco))
conn.commit()

print(f"{data} | {nome} | R$ {preco:.2f}")

preco_alvo = 3500.00
if preco != 0.00 and preco < preco_alvo:
    print("🔔 ALERTA: O preço está abaixo do valor desejado!")
    print(f"➡️ Valor atual: R$ {preco:.2f} | Alvo: R$ {preco_alvo:.2f}")

conn.close()
