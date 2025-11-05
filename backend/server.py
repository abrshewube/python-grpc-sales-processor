import grpc
from concurrent import futures
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proto import sales_pb2_grpc
from services.sales_service import SalesService


def serve():
    """Start gRPC server."""
    port = os.getenv('GRPC_PORT', '50051')
    output_dir = os.getenv('OUTPUT_DIR', 'storage/processed')
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sales_pb2_grpc.add_SalesServiceServicer_to_server(
        SalesService(output_dir=output_dir),
        server
    )
    
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    logger = logging.getLogger(__name__)
    logger.info(f"gRPC server started on port {port}")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    serve()

