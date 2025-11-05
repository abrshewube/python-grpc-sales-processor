# Docker Testing Roadmap

## Prerequisites

1. **Install Docker Desktop** (if not already installed)
   - Download from: https://www.docker.com/products/docker-desktop
   - Ensure Docker and Docker Compose are running

2. **Verify Docker Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

## Step 1: Build Docker Images

```bash
# Build all services
docker-compose build

# Or build individually
docker-compose build grpc-server
docker-compose build http-proxy
docker-compose build frontend
```

## Step 2: Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up
```

## Step 3: Verify Services Are Running

```bash
# Check running containers
docker-compose ps

# Expected output:
# - grpc-server (port 50051)
# - http-proxy (port 8000)
# - frontend (port 3000)

# Check logs
docker-compose logs grpc-server
docker-compose logs http-proxy
docker-compose logs frontend
```

## Step 4: Test Each Service

### 4.1 Test gRPC Server (Port 50051)

```bash
# Check if gRPC server is listening
docker exec grpc-server python -c "import grpc; print('gRPC server is running')"

# Or check logs for startup message
docker-compose logs grpc-server | grep "Server started"
```

### 4.2 Test HTTP Proxy (Port 8000)

```bash
# Test health endpoint (if available)
curl http://localhost:8000/api/status/test

# Or open in browser
# http://localhost:8000
```

### 4.3 Test Frontend (Port 3000)

```bash
# Open in browser
# http://localhost:3000

# Check if Next.js is running
curl http://localhost:3000
```

## Step 5: Test CSV Upload Flow

### 5.1 Prepare Test CSV File

Ensure `sample_sales.csv` exists with format:
```csv
Department Name,Date,Number of Sales
Electronics,2024-01-01,150
Clothing,2024-01-01,75
```

### 5.2 Upload via Frontend

1. Open browser: `http://localhost:3000`
2. Click "Choose File" or drag & drop `sample_sales.csv`
3. Click "Upload & Process CSV"
4. Wait for processing to complete
5. Download processed file

### 5.3 Verify Processing

```bash
# Check processed files in volume
ls -la backend/storage/processed/

# Check logs for processing metrics
docker-compose logs grpc-server | grep "Processed"
```

## Step 6: Test API Endpoints Directly

### 6.1 Upload CSV via HTTP Proxy

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@sample_sales.csv"

# Expected response:
# {
#   "job_id": "...",
#   "status": "processing",
#   "message": "...",
#   "download_url": "...",
#   "metrics": {...}
# }
```

### 6.2 Check Job Status

```bash
# Replace JOB_ID with actual job ID from upload response
curl http://localhost:8000/api/status/JOB_ID

# Expected response:
# {
#   "job_id": "...",
#   "status": "completed",
#   "download_url": "/processed/...",
#   "metrics": {...}
# }
```

### 6.3 Download Processed File

```bash
# Replace FILENAME with actual filename from download_url
curl http://localhost:8000/processed/FILENAME.csv -o output.csv

# Verify content
cat output.csv
```

## Step 7: Test Error Handling

### 7.1 Invalid CSV Format

```bash
# Upload invalid CSV (wrong column order)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@invalid.csv"
```

### 7.2 Empty File

```bash
# Create empty CSV
touch empty.csv
curl -X POST http://localhost:8000/api/upload \
  -F "file=@empty.csv"
```

### 7.3 Large File Test

```bash
# Generate large CSV (if needed)
# Upload and verify memory efficiency
```

## Step 8: Monitor Container Resources

```bash
# Check resource usage
docker stats

# Check specific container
docker stats grpc-server
docker stats http-proxy
docker stats frontend
```

## Step 9: Test Logs and Debugging

```bash
# Follow logs in real-time
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f grpc-server
docker-compose logs -f http-proxy
docker-compose logs -f frontend

# Check last 100 lines
docker-compose logs --tail=100 grpc-server
```

## Step 10: Stop and Clean Up

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Clean up everything
docker system prune -a
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :50051
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process or change ports in docker-compose.yml
```

### Container Fails to Start

```bash
# Check logs
docker-compose logs [service-name]

# Rebuild without cache
docker-compose build --no-cache [service-name]

# Start with verbose output
docker-compose up --verbose
```

### Frontend Can't Connect to Backend

```bash
# Check network connectivity
docker exec frontend ping http-proxy
docker exec http-proxy ping grpc-server

# Verify environment variables
docker exec frontend env | grep NEXT_PUBLIC_API_URL
```

### Proto Files Not Generated

```bash
# Check if proto files exist in container
docker exec grpc-server ls -la proto/

# Regenerate if needed
docker exec grpc-server python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto
```

## Success Criteria

✅ All three containers are running  
✅ Frontend accessible at http://localhost:3000  
✅ HTTP proxy responding at http://localhost:8000  
✅ gRPC server running on port 50051  
✅ CSV upload works end-to-end  
✅ Processed files appear in `backend/storage/processed/`  
✅ Metrics displayed correctly in UI  
✅ Download link works  

## Quick Test Commands

```bash
# One-liner to test everything
docker-compose up -d && \
sleep 5 && \
curl http://localhost:3000 && \
curl http://localhost:8000 && \
docker-compose ps
```

## Next Steps After Testing

1. ✅ Verify all functionality works
2. ✅ Check performance with large files
3. ✅ Test error scenarios
4. ✅ Review logs for any issues
5. ✅ Document any problems found
6. ✅ Optimize if needed

