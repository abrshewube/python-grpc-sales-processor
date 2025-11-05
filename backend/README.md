# Sales CSV Processing Backend

gRPC backend service for processing CSV files and aggregating sales by department.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate Python code from proto:
```bash
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto
```

3. Run the server:
```bash
python server.py
```

Or use environment variables:
```bash
GRPC_PORT=50051 OUTPUT_DIR=storage/processed python server.py
```

## Architecture

### Streaming Processing

The service uses client-streaming gRPC to accept CSV file uploads in chunks. This allows handling large files without loading everything into memory.

**Algorithm:**
1. Receive CSV chunks via gRPC stream
2. Combine chunks into byte buffer
3. Decode bytes to text stream
4. Read CSV line-by-line using csv.reader
5. Aggregate department counts using defaultdict
6. Write output CSV to storage/processed/

### Complexity Analysis

- **Time Complexity:** O(n) where n = number of rows
  - Single pass through CSV file
  - Dictionary lookup/update is O(1) average case
  
- **Space Complexity:** O(d) where d = number of unique departments
  - Only stores department counts in memory
  - CSV file itself is not fully loaded (streaming I/O)

### Memory Efficiency

- Uses `csv.reader` for line-by-line processing
- Only accumulates department counts, not full CSV data
- Output written after aggregation completes

## Testing

Run unit tests:
```bash
python -m pytest backend/tests/
# or
python -m unittest backend.tests.test_csv_processor
```

## API Usage

### Upload CSV (Client-Streaming)

```python
import grpc
from backend.proto import sales_pb2, sales_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = sales_pb2_grpc.SalesServiceStub(channel)

def upload_csv(filename):
    def generate_chunks():
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield sales_pb2.UploadChunk(data=chunk, filename=filename)
    
    response = stub.UploadCSV(generate_chunks())
    return response
```

### Check Job Status

```python
request = sales_pb2.JobStatusRequest(job_id="...")
response = stub.GetJobStatus(request)
```

## Output Format

Output CSV files are written to `storage/processed/` with format:

```csv
Department Name,Total Number of Sales
Clothing,5
Electronics,12
```

Files are named using UUID4 hex strings for uniqueness.

