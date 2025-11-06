# CSV Sales Processing System

A gRPC-based backend with React frontend for processing CSV files and aggregating sales by department.

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
   - Aggregates sales by department
   - Writes output CSV to `storage/processed/`
5. Returns job ID and download URL

### Algorithm & Complexity

**Time Complexity:** O(n)
- Single pass through CSV file
- Dictionary operations are O(1) average case
- Where n = number of rows

**Space Complexity:** O(d)
- Only stores department counts in memory
- CSV file is processed as stream (not fully loaded)
- Where d = number of unique departments

### CSV Format

**Input Format:**
```csv
Department Name,Date,Number of Sales
Electronics,2024-01-01,150
Clothing,2024-01-01,75
```

**Output Format:**
```csv
Department Name,Total Number of Sales
Clothing,75
Electronics,150
```

## API Endpoints

### HTTP Proxy Endpoints

- `POST /api/upload`: Upload CSV file (multipart/form-data)
- `GET /api/status/<job_id>`: Get job status
- `GET /processed/<filename>`: Download processed CSV file

## Testing

### Docker (Recommended)

```bash
# Run all unit tests
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor -v

# Or with pytest
docker-compose run --rm grpc-server pytest tests/ -v
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

## Development Notes

- Proto files need to be regenerated after changes: `python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto`
- Make sure `storage/processed/` directory exists before running server

## License

MIT
