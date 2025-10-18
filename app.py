from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DATA_FILE = 'grades.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def calc_grade(score):
    score = int(score)
    if score >= 85: return 'A'
    elif score >= 70: return 'B'
    elif score >= 50: return 'C'
    elif score >= 30: return 'D'
    else: return 'E'

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/hitung-grade', methods=['POST'])
def hitung_grade():
    data = request.json
    name = data.get('name', '').strip()
    score = int(data.get('score', -1))
    if not name or not (0 <= score <= 100):
        return jsonify({'error': 'Invalid input'}), 400
    grade = calc_grade(score)
    record = {'id': os.urandom(6).hex(), 'name': name, 'score': score, 'grade': grade}
    hist = load_data()
    hist.append(record)
    save_data(hist)
    return jsonify(record)

@app.route('/api/get-riwayat')
def get_riwayat():
    hist = load_data()
    return jsonify(hist[::-1])

@app.route('/api/hapus-riwayat/<rid>', methods=['DELETE'])
def hapus_riwayat(rid):
    hist = load_data()
    hist = [r for r in hist if r['id'] != rid]
    save_data(hist)
    return jsonify({'success': True})

@app.route('/api/hapus-semua-riwayat', methods=['DELETE'])
def hapus_semua():
    save_data([])
    return jsonify({'success': True})

@app.route('/api/export-riwayat')
def export_riwayat():
    return send_from_directory('.', DATA_FILE, as_attachment=True)

@app.route('/api/statistik')
def statistik():
    hist = load_data()
    stats = {g: 0 for g in 'ABCDE'}
    for r in hist:
        stats[r['grade']] += 1
    return jsonify(stats)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
