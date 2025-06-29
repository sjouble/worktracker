from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'WorkTracker API is running!',
        'status': 'success'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'WorkTracker is running'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working!', 'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 