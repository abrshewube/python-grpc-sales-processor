from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import grpc
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proto import sales_pb2, sales_pb2_grpc
from utils.auth import get_auth_manager

app = Flask(__name__)
CORS(app)

GRPC_SERVER = os.getenv('GRPC_SERVER', 'localhost:50051')
PROCESSED_DIR = os.getenv('PROCESSED_DIR', 'storage/processed')

auth_manager = get_auth_manager()


def _get_auth_token() -> str:
    """Extract auth token from request headers or query params."""
    # Check Authorization header first
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Check query parameter
    return request.args.get('token', '')


@app.route('/api/upload', methods=['POST'])
def upload():
    """HTTP endpoint that proxies to gRPC."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get auth token
    auth_token = _get_auth_token()
    
    # Validate authentication
    try:
        auth_manager.require_auth(auth_token)
    except PermissionError as e:
        return jsonify({'error': 'Authentication failed'}), 401
    
    # Connect to gRPC server
    # Note: For production, consider using connection pooling or persistent channels
    channel = grpc.insecure_channel(GRPC_SERVER)
    stub = sales_pb2_grpc.SalesServiceStub(channel)
    
    # Stream file chunks to gRPC
    def generate_chunks():
        chunk_size = 8192  # 8KB chunks seems reasonable
        first_chunk = True
        while True:
            chunk_data = file.read(chunk_size)
            if not chunk_data:
                break
            
            chunk = sales_pb2.UploadChunk(data=chunk_data)
            if first_chunk:
                chunk.filename = file.filename
                chunk.auth_token = auth_token
                first_chunk = False
            
            yield chunk
    
    try:
        response = stub.UploadCSV(generate_chunks())
        
        # Build response with metrics if available
        result = {
            'job_id': response.job_id,
            'status': response.status,
            'message': response.message,
            'download_url': response.download_url if response.download_url else ''
        }
        
        # Add metrics if available
        if response.HasField('metrics'):
            metrics = response.metrics
            result['metrics'] = {
                'processing_time_ms': metrics.processing_time_ms,
                'rows_processed': metrics.rows_processed,
                'rows_skipped': metrics.rows_skipped,
                'departments_count': metrics.departments_count,
                'peak_memory_mb': metrics.peak_memory_mb
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        channel.close()


@app.route('/api/status/<job_id>', methods=['GET'])
def status(job_id):
    """Check job status."""
    auth_token = _get_auth_token()
    
    # Validate authentication
    try:
        auth_manager.require_auth(auth_token)
    except PermissionError as e:
        return jsonify({'error': 'Authentication failed'}), 401
    
    channel = grpc.insecure_channel(GRPC_SERVER)
    stub = sales_pb2_grpc.SalesServiceStub(channel)
    
    try:
        request_msg = sales_pb2.JobStatusRequest(job_id=job_id, auth_token=auth_token)
        response = stub.GetJobStatus(request_msg)
        
        result = {
            'job_id': response.job_id,
            'status': response.status,
            'download_url': response.download_url,
            'error_message': response.error_message
        }
        
        # Add metrics if available
        if response.HasField('metrics'):
            metrics = response.metrics
            result['metrics'] = {
                'processing_time_ms': metrics.processing_time_ms,
                'rows_processed': metrics.rows_processed,
                'rows_skipped': metrics.rows_skipped,
                'departments_count': metrics.departments_count,
                'peak_memory_mb': metrics.peak_memory_mb
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        channel.close()


@app.route('/processed/<filename>')
def download_file(filename):
    """Serve processed CSV files."""
    return send_from_directory(PROCESSED_DIR, filename)


if __name__ == '__main__':
    port = int(os.getenv('HTTP_PORT', '8000'))
    app.run(host='0.0.0.0', port=port, debug=True)

