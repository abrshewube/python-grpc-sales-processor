import os
import io
import threading
import time
from typing import Iterator, Dict, Optional
from collections import defaultdict
import csv
from uuid import uuid4
from datetime import datetime
import logging
import psutil
import sys

from proto import sales_pb2, sales_pb2_grpc
from utils.auth import get_auth_manager

logger = logging.getLogger(__name__)


class SalesService(sales_pb2_grpc.SalesServiceServicer):
    """gRPC service for processing CSV sales data with background processing and metrics."""
    
    def __init__(self, output_dir: str = "storage/processed"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # In-memory job tracking
        self.jobs: Dict[str, Dict] = {}
        self.jobs_lock = threading.Lock()
        
        # Auth manager
        self.auth_manager = get_auth_manager()
    
    def UploadCSV(self, request_iterator: Iterator[sales_pb2.UploadChunk], context) -> sales_pb2.UploadResponse:
        """Handle streaming CSV upload with authentication."""
        job_id = str(uuid4())
        chunks = []
        filename = None
        auth_token = None
        first_chunk = True
        
        try:
            # Collect chunks and extract metadata
            try:
                for chunk in request_iterator:
                    if first_chunk:
                        if chunk.filename:
                            filename = chunk.filename
                        if hasattr(chunk, 'auth_token') and chunk.auth_token:
                            auth_token = chunk.auth_token
                        first_chunk = False
                    
                    if chunk.data:
                        chunks.append(chunk.data)
            except Exception as iter_error:
                logger.error(f"Error iterating request chunks for job {job_id}: {str(iter_error)}", exc_info=True)
                raise ValueError(f"Failed to receive file data: {str(iter_error)}")
            
            if not chunks:
                raise ValueError("No file data received")
            
            # Validate authentication
            try:
                self.auth_manager.require_auth(auth_token)
            except PermissionError as e:
                logger.warning(f"Unauthorized upload attempt for job {job_id}: {str(e)}")
                response = sales_pb2.UploadResponse(
                    job_id=job_id,
                    status='error',
                    message='Authentication failed'
                )
                # Initialize empty metrics (if field exists)
                try:
                    response.metrics.processing_time_ms = 0
                    response.metrics.rows_processed = 0
                    response.metrics.rows_skipped = 0
                    response.metrics.departments_count = 0
                    response.metrics.peak_memory_mb = 0
                except AttributeError:
                    # Metrics field not available - proto files need regeneration
                    pass
                return response
            
            # Mark as processing immediately
            with self.jobs_lock:
                self.jobs[job_id] = {
                    'status': 'processing',
                    'filename': filename,
                    'start_time': time.time(),
                    'metrics': None
                }
            
            # Process in background thread
            thread = threading.Thread(
                target=self._process_csv_background,
                args=(chunks, job_id, filename)
            )
            thread.daemon = True
            thread.start()
            
            # Return immediately with job ID
            response = sales_pb2.UploadResponse(
                job_id=job_id,
                status='processing',
                message='File upload accepted, processing in background',
                download_url=''
            )
            # Initialize empty metrics (if field exists)
            try:
                response.metrics.processing_time_ms = 0
                response.metrics.rows_processed = 0
                response.metrics.rows_skipped = 0
                response.metrics.departments_count = 0
                response.metrics.peak_memory_mb = 0
            except AttributeError:
                # Metrics field not available - proto files need regeneration
                pass
            return response
            
        except Exception as e:
            logger.error(f"Error accepting CSV upload for job {job_id}: {str(e)}", exc_info=True)
            with self.jobs_lock:
                self.jobs[job_id] = {
                    'status': 'error',
                    'error': str(e)
                }
            response = sales_pb2.UploadResponse(
                job_id=job_id,
                status='error',
                message=f'Upload failed: {str(e)}'
            )
            # Initialize empty metrics (if field exists)
            try:
                response.metrics.processing_time_ms = 0
                response.metrics.rows_processed = 0
                response.metrics.rows_skipped = 0
                response.metrics.departments_count = 0
                response.metrics.peak_memory_mb = 0
            except AttributeError:
                # Metrics field not available - proto files need regeneration
                pass
            return response
    
    def GetJobStatus(self, request: sales_pb2.JobStatusRequest, context) -> sales_pb2.JobStatusResponse:
        """Get status of a processing job with authentication."""
        job_id = request.job_id
        auth_token = request.auth_token if hasattr(request, 'auth_token') else None
        
        # Validate authentication
        try:
            self.auth_manager.require_auth(auth_token)
        except PermissionError as e:
            logger.warning(f"Unauthorized status check attempt for job {job_id}: {str(e)}")
            return sales_pb2.JobStatusResponse(
                job_id=job_id,
                status='unauthorized',
                error_message='Authentication failed'
            )
        
        with self.jobs_lock:
            if job_id not in self.jobs:
                return sales_pb2.JobStatusResponse(
                    job_id=job_id,
                    status='not_found'
                )
            
            job = self.jobs[job_id]
            
            # Build response with metrics if available
            response = sales_pb2.JobStatusResponse(
                job_id=job_id,
                status=job['status'],
                download_url=job.get('download_url', ''),
                error_message=job.get('error', '')
            )
            
            # Initialize metrics (if field exists)
            try:
                response.metrics.processing_time_ms = 0
                response.metrics.rows_processed = 0
                response.metrics.rows_skipped = 0
                response.metrics.departments_count = 0
                response.metrics.peak_memory_mb = 0
                
                # Add metrics if available
                if job.get('metrics'):
                    metrics = job['metrics']
                    if isinstance(metrics, sales_pb2.ProcessingMetrics):
                        response.metrics.CopyFrom(metrics)
            except AttributeError:
                # Metrics field not available - proto files need regeneration
                pass
            
            return response
    
    def _process_csv_background(self, chunks: list, job_id: str, filename: Optional[str]) -> None:
        """Process CSV in background thread with metrics tracking."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        try:
            output_filename = self._process_csv(chunks, job_id)
            
            # Generate download URL
            download_url = f"/processed/{output_filename}"
            
            # Calculate metrics
            processing_time_ms = int((time.time() - start_time) * 1000)
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            with self.jobs_lock:
                job = self.jobs[job_id]
                
                # Create metrics object
                metrics = sales_pb2.ProcessingMetrics()
                metrics.processing_time_ms = processing_time_ms
                metrics.rows_processed = job.get('rows_processed', 0)
                metrics.rows_skipped = job.get('rows_skipped', 0)
                metrics.departments_count = job.get('departments_count', 0)
                metrics.peak_memory_mb = max(0, int(peak_memory - initial_memory))
                
                self.jobs[job_id] = {
                    'status': 'completed',
                    'download_url': download_url,
                    'filename': output_filename,
                    'metrics': metrics
                }
            
            logger.info(f"Job {job_id} completed successfully in {processing_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Error processing CSV for job {job_id}: {str(e)}", exc_info=True)
            with self.jobs_lock:
                self.jobs[job_id] = {
                    'status': 'error',
                    'error': str(e)
                }
    
    def _process_csv(self, chunks: list, job_id: str) -> str:
        """
        Process CSV chunks and write output.
        
        CSV Format Expected:
        - Column 1: Department Name (string)
        - Column 2: Date (ISO format: YYYY-MM-DD)
        - Column 3: Number of Sales (integer)
        """
        # Combine chunks into single buffer for processing
        full_data = b''.join(chunks)
        
        # Process CSV line-by-line to keep memory footprint low
        dept_counts = defaultdict(int)
        text_stream = io.TextIOWrapper(io.BytesIO(full_data), encoding='utf-8')
        reader = csv.reader(text_stream)
        
        # Skip header row
        try:
            header = next(reader)
            if len(header) < 3:
                raise ValueError("CSV must have at least 3 columns: Department Name, Date, Number of Sales")
        except StopIteration:
            raise ValueError("CSV file is empty")
        
        rows_processed = 0
        rows_skipped = 0
        
        # Process each data row
        for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
            if not row or len(row) < 3:
                rows_skipped += 1
                logger.warning(f"Row {row_num}: Skipping malformed row (insufficient columns)")
                continue
            
            try:
                dept_name = row[0].strip()
                date_str = row[1].strip()
                sales_str = row[2].strip()
                
                # Validate department name
                if not dept_name:
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Skipping row with empty department name")
                    continue
                
                # Validate date format (ISO format: YYYY-MM-DD)
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Invalid date format '{date_str}', expected YYYY-MM-DD")
                    continue
                
                # Validate and parse number of sales
                try:
                    num_sales = int(sales_str)
                    if num_sales < 0:
                        rows_skipped += 1
                        logger.warning(f"Row {row_num}: Negative sales value {num_sales}, skipping")
                        continue
                    
                    # Aggregate sales by department
                    dept_counts[dept_name] += num_sales
                    rows_processed += 1
                    
                except ValueError:
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Invalid sales value '{sales_str}', must be an integer")
                    continue
                    
            except Exception as e:
                rows_skipped += 1
                logger.warning(f"Row {row_num}: Error processing row: {str(e)}")
                continue
        
        logger.info(f"Job {job_id}: Processed {rows_processed} rows, skipped {rows_skipped} invalid rows")
        
        # Write output CSV to bytes buffer
        output_buffer = io.BytesIO()
        text_writer = io.TextIOWrapper(output_buffer, encoding='utf-8')
        writer = csv.writer(text_writer)
        
        writer.writerow(['Department Name', 'Total Number of Sales'])
        
        # Sort alphabetically for consistent output
        for dept in sorted(dept_counts.keys()):
            writer.writerow([dept, dept_counts[dept]])
        
        text_writer.flush()
        output_data = output_buffer.getvalue()
        
        # Save to local filesystem
        output_filename = f"{uuid4().hex}.csv"
        output_path = os.path.join(self.output_dir, output_filename)
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        # Store metrics in job
        with self.jobs_lock:
            if job_id in self.jobs:
                self.jobs[job_id]['rows_processed'] = rows_processed
                self.jobs[job_id]['rows_skipped'] = rows_skipped
                self.jobs[job_id]['departments_count'] = len(dept_counts)
        
        return output_filename
