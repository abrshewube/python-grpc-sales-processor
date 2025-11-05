# Docker Testing Commands

## Running Tests in Docker

### Method 1: Using Docker Compose Test Service

```bash
# Run tests using the test service
docker-compose --profile test run --rm test

# Run tests with pytest (if installed)
docker-compose --profile test run --rm test pytest tests/ -v

# Run tests with unittest
docker-compose --profile test run --rm test python -m unittest tests.test_csv_processor -v
```

### Method 2: Run Tests in Running Container

```bash
# If containers are already running
docker exec grpc-server python -m unittest tests.test_csv_processor -v

# Or with pytest
docker exec grpc-server pytest tests/ -v
```

### Method 3: Run Tests in One-off Container

```bash
# Build the image first
docker-compose build grpc-server

# Run tests in a temporary container
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor -v

# Or with pytest
docker-compose run --rm grpc-server pytest tests/ -v
```

### Method 4: Direct Docker Command

```bash
# Build image
docker build -f backend/Dockerfile -t csv-sales-backend .

# Run tests
docker run --rm csv-sales-backend python -m unittest tests.test_csv_processor -v

# Or with pytest
docker run --rm csv-sales-backend pytest tests/ -v
```

## Quick Test Commands

```bash
# Test with unittest (quickest)
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor -v

# Test with pytest
docker-compose run --rm grpc-server pytest tests/ -v

# Test with coverage (if pytest-cov installed)
docker-compose run --rm grpc-server pytest tests/ --cov=. --cov-report=html
```

## Test Service Configuration

The `docker-compose.yml` includes a test service that:
- Uses the same Dockerfile as grpc-server
- Mounts the code directory for live changes
- Runs tests and exits
- Can be run with: `docker-compose --profile test run --rm test`

## Running Tests During Development

```bash
# Watch mode (if pytest-watch installed)
docker-compose run --rm grpc-server ptw tests/

# Run specific test file
docker-compose run --rm grpc-server python -m unittest tests.test_csv_processor.TestCSVProcessor.test_aggregate_sales_basic

# Run specific test method
docker-compose run --rm grpc-server pytest tests/test_csv_processor.py::TestCSVProcessor::test_aggregate_sales_basic -v
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Build and test in one command
docker-compose build test && docker-compose --profile test run --rm test

# Exit code will be non-zero if tests fail
if [ $? -eq 0 ]; then
  echo "Tests passed!"
else
  echo "Tests failed!"
  exit 1
fi
```

