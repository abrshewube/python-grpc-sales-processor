# CSV Sales Processing System

A gRPC-based backend with React frontend for processing CSV files and aggregating sales by department.

## Quick Start with Docker

### Prerequisites

- Docker Desktop installed and running
- Docker Compose installed

### Run the Application

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# gRPC Server: localhost:50051
```

**Run in background:**
```bash
docker-compose up -d
```

**Stop services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

### Run Tests

```bash
# Run all unit tests
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor -v

# Or with pytest
docker-compose run --rm grpc-server pytest tests/ -v
```

## CSV Format

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

## Usage

1. Open http://localhost:3000 in your browser
2. Upload a CSV file with format: `Department Name, Date, Number of Sales`
3. Wait for processing to complete
4. Download the aggregated results

## API Endpoints

- `POST /api/upload` - Upload CSV file
- `GET /api/status/<job_id>` - Get job status
- `GET /processed/<filename>` - Download processed CSV file

## Local Development (Without Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto
python server.py  # Terminal 1
python http_proxy.py  # Terminal 2
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

- `GRPC_PORT`: gRPC server port (default: 50051)
- `OUTPUT_DIR`: Output directory (default: storage/processed)
- `GRPC_SERVER`: gRPC server address (default: localhost:50051)
- `HTTP_PORT`: HTTP proxy port (default: 8000)
- `NEXT_PUBLIC_API_URL`: Frontend API URL (default: http://localhost:8000)

## Project Structure

```
├── backend/          # Python gRPC backend
├── frontend/         # Next.js React frontend
├── docker-compose.yml
└── README.md
```

## License

MIT
