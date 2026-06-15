# app.py
# This is the SERVER of our project
# It connects the ML model to the webpage and Chrome extension

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from model import predict_url, calculate_risk_score

app = Flask(__name__)
CORS(app)  # This allows the Chrome extension to talk to our Flask server

# ==========================================
# ROUTE 1: Main webpage
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# ROUTE 2: URL Check API
# This is called by BOTH the webpage AND
# the Chrome extension
# ==========================================
@app.route('/check', methods=['POST'])
def check_url():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']

    result = calculate_risk_score(url)
    prediction, probability = predict_url(url)

    response = {
        'url': url,
        'is_phishing': bool(prediction),
        'risk_score': result['score'],
        'verdict': result['verdict'],
        'reasons': result['reasons'],
        'features': {
            'url_length': result['features']['url_length'],
            'has_https': bool(result['features']['has_https']),
            'has_ip_address': bool(result['features']['has_ip']),
            'has_at_symbol': bool(result['features']['has_at_symbol']),
            'has_suspicious_words': bool(result['features']['has_suspicious_words']),
            'num_dots': result['features']['num_dots'],
        }
    }

    return jsonify(response)

# ==========================================
# ROUTE 3: Health check
# ==========================================
@app.route('/health')
def health():
    return jsonify({'status': 'running', 'model': 'rule-based phishing detector'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)