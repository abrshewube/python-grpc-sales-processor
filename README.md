# CSV Sales Processing System

A gRPC-based backend with React frontend for processing CSV files and aggregating sales by department.

## Project Structure

```
project/
 ├── backend/
 │   ├── proto/
 │   │   └── sales.proto
 │   ├── server.py                 # gRPC server
 │   ├── http_proxy.py            # HTTP proxy to gRPC
 │   ├── services/
 │   │   └── sales_service.py     # gRPC service implementation
 │   ├── utils/
 │   │   └── csv_processor.py     # CSV processing utilities
 │   ├── tests/
 │   │   └── test_csv_processor.py
 │   ├── storage/
 │   │   └── processed/           # Output files
 │   ├── Dockerfile
 │   ├── Dockerfile.proxy
 │   └── requirements.txt
 ├── frontend/
 │   ├── app/
 │   │   ├── page.tsx             # Upload form component
 │   │   ├── layout.tsx
 │   │   └── globals.css
 │   ├── Dockerfile
 │   └── package.json
 └── docker-compose.yml
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Access frontend at http://localhost:3000
# gRPC server at localhost:50051
# HTTP proxy at http://localhost:8000
```

**To run in background:**
```bash
docker-compose up -d
```

**To stop services:**
```bash
docker-compose down
```

### Running Tests in Docker

```bash
# Run all unit tests
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor -v

# Or with pytest
docker-compose run --rm grpc-server pytest tests/ -v

# Or use the test service
docker-compose --profile test run --rm test
```

### Manual Setup

#### Backend

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Generate Python code from proto:
```bash
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto
```

3. Start gRPC server:
```bash
python server.py
```

4. Start HTTP proxy (in another terminal):
```bash
python http_proxy.py
```

#### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open http://localhost:3000

## How It Works

### Architecture

The system uses a three-tier architecture:

1. **Frontend (Next.js)**: React-based UI for file upload
2. **HTTP Proxy (Flask)**: Thin HTTP server that forwards requests to gRPC
3. **gRPC Server (Python)**: Processes CSV files using streaming I/O

### Processing Flow

1. User uploads CSV file via frontend
2. Frontend sends file to HTTP proxy via multipart/form-data
3. HTTP proxy streams file chunks to gRPC server
4. gRPC server processes CSV line-by-line:
   - Reads CSV using `csv.reader` (streaming)
   - Aggregates department counts using `defaultdict(int)`
   - Writes output CSV to `storage/processed/`
5. Returns job ID and download URL

### Algorithm & Complexity

**Processing Algorithm:**

```
1. Receive CSV chunks via gRPC stream
2. Combine chunks into byte buffer
3. Decode bytes to text stream
4. Skip header row
5. For each data row:
   - Extract department name (first column)
   - Increment department counter
6. Write aggregated results to output CSV
```

**Time Complexity:** O(n)
- Single pass through CSV file
- Dictionary operations are O(1) average case
- Where n = number of rows

**Space Complexity:** O(d)
- Only stores department counts in memory
- CSV file is processed as stream (not fully loaded)
- Where d = number of unique departments

**Memory Efficiency:**

- Uses `csv.reader` for line-by-line processing
- Only accumulates department counts, not full CSV data
- Output written after aggregation completes

### Example CSV Input

```csv
Department,Sales Amount,Date
Electronics,150.50,2024-01-01
Clothing,75.00,2024-01-01
Electronics,200.00,2024-01-02
Books,45.00,2024-01-02
Electronics,120.00,2024-01-03
```

### Example CSV Output

```csv
Department Name,Total Number of Sales
Books,1
Clothing,1
Electronics,3
```

## API Endpoints

### gRPC Endpoints

- `UploadCSV(stream UploadChunk) -> UploadResponse`: Stream CSV file upload
- `GetJobStatus(JobStatusRequest) -> JobStatusResponse`: Check processing status

### HTTP Proxy Endpoints

- `POST /api/upload`: Upload CSV file (multipart/form-data)
- `GET /api/status/<job_id>`: Get job status

## Testing

### Docker (Recommended)

```bash
# Run all unit tests
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor -v

# Or with pytest
docker-compose run --rm grpc-server pytest tests/ -v

# Or use the test service
docker-compose --profile test run --rm test
```

### Local Development

```bash
cd backend
python -m pytest tests/
# or
python -m unittest tests.test_csv_processor -v
```

## Configuration

### Environment Variables

**Backend:**
- `GRPC_PORT`: gRPC server port (default: 50051)
- `OUTPUT_DIR`: Output directory for processed files (default: storage/processed)

**HTTP Proxy:**
- `GRPC_SERVER`: gRPC server address (default: localhost:50051)
- `HTTP_PORT`: HTTP proxy port (default: 8000)

**Frontend:**
- `NEXT_PUBLIC_API_URL`: HTTP proxy URL (default: http://localhost:8000)

## File Naming

Output files are named using UUID4 hex strings (e.g., `a1b2c3d4e5f6...csv`) for uniqueness and security.

## Error Handling

- Malformed CSV rows are skipped (logged but not fatal)
- Empty files return empty results
- Network errors are caught and returned as error responses

## Limitations & Future Improvements

**Current Limitations:**
- In-memory job tracking (not persistent)
- No authentication/authorization
- HTTP proxy loads entire file into memory before streaming to gRPC
- No background job queue (processing is synchronous)

**Potential Improvements:**
- Background processing with Celery or similar
- Redis/database for job tracking
- Token-based authentication
- Metrics (processing time, memory usage, rows processed)
- Better error handling for malformed CSV
- Support for different CSV formats/encodings

## Development Notes

- Proto files need to be regenerated after changes: `python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto`
- Make sure `storage/processed/` directory exists before running server
- Frontend uses Tailwind CSS for styling

## License

MIT

