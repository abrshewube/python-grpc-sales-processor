FROM python:3.9-slim

WORKDIR /app

# install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy proto files first
COPY backend/proto/ ./proto/

# generate python code from proto (generates in proto/ directory)
RUN python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/sales.proto

# copy rest of application code
COPY backend/ ./

# create storage directory
RUN mkdir -p storage/processed

EXPOSE 50051

CMD ["python", "server.py"]

