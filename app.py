from flask import Flask, render_template, jsonify
import taquilla
import gimnasio
import panaderia
import tablon
import barrera

app = Flask(__name__)

# ──────────────────────────────────────────────
#  FRONTEND
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ──────────────────────────────────────────────
#  API ENDPOINTS
# ──────────────────────────────────────────────
@app.route('/api/taquilla')
def get_taquilla():
    resultado = taquilla.ejecutar_taquilla()
    return jsonify(resultado)

@app.route('/api/gimnasio')
def get_gimnasio():
    resultado = gimnasio.ejecutar_gimnasio()
    return jsonify(resultado)

@app.route('/api/panaderia')
def get_panaderia():
    resultado = panaderia.ejecutar_panaderia()
    return jsonify(resultado)

@app.route('/api/tablon')
def get_tablon():
    resultado = tablon.ejecutar_tablon()
    return jsonify(resultado)

@app.route('/api/barrera')
def get_barrera():
    resultado = barrera.ejecutar_barrera()
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)