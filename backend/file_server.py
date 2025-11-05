import os

# Simple script to serve processed files via HTTP
from flask import Flask, send_from_directory

app = Flask(__name__)

PROCESSED_DIR = os.getenv('PROCESSED_DIR', 'backend/storage/processed')


@app.route('/processed/<filename>')
def download_file(filename):
    """Serve processed CSV files."""
    return send_from_directory(PROCESSED_DIR, filename)


if __name__ == '__main__':
    port = int(os.getenv('FILE_SERVER_PORT', '8080'))
    app.run(host='0.0.0.0', port=port)

