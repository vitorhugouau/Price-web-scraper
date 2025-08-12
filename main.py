from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_dados():
    conn = sqlite3.connect('historico_precos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT data, produto, caixa, tamanho, pulseira, tamanho_pulseira, preco FROM historico_precos ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados

@app.route('/')
def index():
    dados = get_dados()
    return render_template('index.html', dados=dados)

if __name__ == '__main__':
    app.run(debug=True)
