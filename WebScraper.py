import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pytz
import os

arquivo_csv = 'historico_precos_ml.csv'
arquivo_existe = os.path.exists(arquivo_csv)

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
    preco = preco_meta['content']
else:
    preco = '0.00'

agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
data = agora.strftime('%d/%m/%Y %H:%M:%S')

arquivo_csv = 'historico_precos_ml.csv'
with open(arquivo_csv, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    if not arquivo_existe:
        writer.writerow(['Data', 'Produto', 'Preço (R$)'])
    writer.writerow([data, nome, preco])

print(f"{data} | {nome} | R$ {preco}")

# Alerta de preço
preco_alvo = 3500.00
if preco != '0.00' and float(preco) < preco_alvo:
    print("🔔 ALERTA: O preço está abaixo do valor desejado!")
    print(f"➡️ Valor atual: R$ {preco} | Alvo: R$ {preco_alvo}")
