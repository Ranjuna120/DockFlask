from flask import Flask, render_template, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Flask app is running successfully!'
    })

@app.route('/api/info')
def app_info():
    return jsonify({
        'app_name': 'DockFlask',
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'python_version': '3.11'
    })

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
