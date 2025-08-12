from flask import Flask, render_template, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import threading

app = Flask(__name__)
db_file = "historico_precos.db"

def criar_tabela():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_precos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        produto TEXT NOT NULL,
        caixa TEXT,
        tamanho TEXT,
        pulseira TEXT,
        tamanho_pulseira TEXT,
        preco REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def get_dados():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT data, produto, caixa, tamanho, pulseira, tamanho_pulseira, preco FROM historico_precos ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados

def scraper_e_inserir():
    url = 'https://www.mercadolivre.com.br/apple-watch-series-10-gps-caixa-preta-brilhante-de-aluminio-42-mm-pulseira-esportiva-preta-pm/p/MLB40694304'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    nome_tag = soup.find('h1', class_='ui-pdp-title')
    nome_bruto = nome_tag.get_text(strip=True) if nome_tag else 'Nome não encontrado'

    partes = [p.strip() for p in nome_bruto.split("•")]

    produto = partes[0] if len(partes) > 0 else ""
    caixa_info = partes[1] if len(partes) > 1 else ""
    pulseira_info = partes[2] if len(partes) > 2 else ""

    if "–" in caixa_info:
        caixa, tamanho = [x.strip() for x in caixa_info.split("–", 1)]
    else:
        caixa, tamanho = caixa_info, ""

    if "–" in pulseira_info:
        pulseira, tamanho_pulseira = [x.strip() for x in pulseira_info.split("–", 1)]
    else:
        pulseira, tamanho_pulseira = pulseira_info, ""

    preco_meta = soup.find('meta', itemprop='price')
    if preco_meta and preco_meta.get('content'):
        preco = float(preco_meta['content'])
    else:
        preco = 0.00

    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
    data = agora.strftime('%d/%m/%Y %H:%M:%S')

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO historico_precos (data, produto, caixa, tamanho, pulseira, tamanho_pulseira, preco)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data, produto, caixa, tamanho, pulseira, tamanho_pulseira, preco))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    dados = get_dados()
    return render_template('index.html', dados=dados)

@app.route('/atualizar', methods=['POST'])
def atualizar():
    thread = threading.Thread(target=scraper_e_inserir)
    thread.start()
    return jsonify({'mensagem': 'Atualização iniciada! Aguarde alguns segundos.'})

if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True)
