#!/bin/bash
# Generate Python code from proto files
# This script activates the venv and regenerates proto files

cd backend

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Warning: Virtual environment not found at backend/venv"
    echo "Using system Python instead..."
fi

# Generate proto files
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto

# Fix imports in generated files
python fix_proto_imports.py

echo ""
echo "Proto files generated successfully!"
echo "Files created in backend/proto/:"
echo "  - sales_pb2.py"
echo "  - sales_pb2_grpc.py"
echo ""
