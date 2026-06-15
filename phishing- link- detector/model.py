# model.py
# Phishing Detector - Pure Python (no scikit-learn needed)

import re
import math
import pickle

def extract_features(url):
    features = {}
    features['url_length'] = len(url)
    features['has_ip'] = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0
    features['has_at_symbol'] = 1 if '@' in url else 0
    features['has_double_slash'] = 1 if '//' in url[7:] else 0
    features['has_dash'] = 1 if '-' in url else 0
    features['num_dots'] = url.count('.')
    features['has_https'] = 1 if url.startswith('https') else 0
    features['num_subdomains'] = len(url.split('.')) - 2
    features['has_suspicious_words'] = 1 if any(word in url.lower() for word in ['login', 'verify', 'secure', 'account', 'update', 'banking', 'confirm', 'signin', 'paypal', 'password']) else 0
    features['url_entropy'] = len(set(url)) / len(url) if len(url) > 0 else 0
    return features

def calculate_risk_score(url):
    features = extract_features(url)
    score = 0
    reasons = []

    if features['has_ip']:
        score += 35
        reasons.append("Uses IP address instead of domain name")
    if features['has_at_symbol']:
        score += 25
        reasons.append("Contains @ symbol — tricks browsers")
    if features['has_double_slash']:
        score += 20
        reasons.append("Contains double slash redirect")
    if features['has_suspicious_words']:
        score += 25
        reasons.append("Contains suspicious keywords (login, verify, banking, etc.)")
    if features['has_dash']:
        score += 10
        reasons.append("Contains dash in domain — common in fake sites")
    if features['num_dots'] > 3:
        score += 15
        reasons.append("Too many dots — likely a subdomain attack")
    if features['url_length'] > 75:
        score += 15
        reasons.append("URL is unusually long")
    if not features['has_https']:
        score += 20
        reasons.append("No HTTPS — connection is not secure")
    if features['num_subdomains'] > 2:
        score += 15
        reasons.append("Too many subdomains")

    score = min(score, 100)

    if score >= 70:
        verdict = "PHISHING"
    elif score >= 40:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    return {
        'score': score,
        'verdict': verdict,
        'reasons': reasons,
        'features': features
    }

def predict_url(url):
    result = calculate_risk_score(url)
    is_phishing = 1 if result['verdict'] == 'PHISHING' else 0
    probability_phishing = result['score'] / 100
    probability_safe = 1 - probability_phishing
    return is_phishing, [probability_safe, probability_phishing]

# Save a dummy model file so app.py doesn't break
with open('phishing_model.pkl', 'wb') as f:
    pickle.dump({'type': 'rule_based', 'version': '1.0'}, f)

print("Phishing Detector model ready!")
print("Testing with sample URLs:")
print()

test_urls = [
    "https://www.google.com",
    "http://192.168.1.1/login/verify",
    "http://paypal-secure-login.xyz/account/confirm"
]

for url in test_urls:
    result = calculate_risk_score(url)
    print(f"URL: {url}")
    print(f"Risk Score: {result['score']}% — {result['verdict']}")
    if result['reasons']:
        print(f"Reasons: {', '.join(result['reasons'])}")
    print()