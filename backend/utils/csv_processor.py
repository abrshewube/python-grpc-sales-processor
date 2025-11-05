import csv
import io
from collections import defaultdict
from typing import Dict, Iterator
from uuid import uuid4
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def aggregate_sales_from_stream(stream: Iterator[str]) -> Dict[str, int]:
    """
    Process CSV stream and aggregate sales per department.
    
    CSV Format Expected:
    - Column 1: Department Name (string)
    - Column 2: Date (ISO format: YYYY-MM-DD)
    - Column 3: Number of Sales (integer)
    
    Returns dict mapping department name -> total number of sales.
    """
    dept_counts = defaultdict(int)
    
    # Skip header row
    try:
        header = next(stream)
        if not header.strip():
            return dept_counts
    except StopIteration:
        return dept_counts
    
    rows_processed = 0
    rows_skipped = 0
    
    # Process rows one by one
    for row_num, row in enumerate(stream, start=2):
        if not row.strip():
            continue
            
        try:
            reader = csv.reader([row])
            for fields in reader:
                if len(fields) < 3:  # Need Department Name, Date, and Number of Sales
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Insufficient columns, skipping")
                    continue
                
                dept_name = fields[0].strip()
                date_str = fields[1].strip()
                sales_str = fields[2].strip()
                
                # Validate department name
                if not dept_name:
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Empty department name, skipping")
                    continue
                
                # Validate date format (ISO format: YYYY-MM-DD)
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Invalid date format '{date_str}', skipping")
                    continue
                
                # Validate and parse number of sales
                try:
                    num_sales = int(sales_str)
                    if num_sales < 0:
                        rows_skipped += 1
                        logger.warning(f"Row {row_num}: Negative sales value {num_sales}, skipping")
                        continue
                    
                    # Sum sales by department (not count rows)
                    dept_counts[dept_name] += num_sales
                    rows_processed += 1
                    
                except ValueError:
                    rows_skipped += 1
                    logger.warning(f"Row {row_num}: Invalid sales value '{sales_str}', skipping")
                    continue
                    
        except Exception as e:
            rows_skipped += 1
            logger.warning(f"Row {row_num}: Error processing row: {str(e)}")
            continue
    
    logger.info(f"Processed {rows_processed} rows, skipped {rows_skipped} invalid rows")
    return dept_counts


def write_output_csv(dept_counts: Dict[str, int], output_path: str) -> None:
    """Write aggregated results to output CSV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Department Name', 'Total Number of Sales'])
        
        # sort by department name for consistent output
        for dept in sorted(dept_counts.keys()):
            writer.writerow([dept, dept_counts[dept]])


def process_csv_stream(input_stream: Iterator[bytes], output_dir: str) -> str:
    """
    Process CSV file from byte stream, aggregate sales, write output.
    Returns the output filename (UUID-based).
    """
    output_filename = f"{uuid4().hex}.csv"
    output_path = os.path.join(output_dir, output_filename)
    
    # decode bytes to text line by line
    text_stream = io.TextIOWrapper(io.BytesIO(b''.join(input_stream)), encoding='utf-8')
    lines = (line for line in text_stream)
    
    dept_counts = aggregate_sales_from_stream(lines)
    write_output_csv(dept_counts, output_path)
    
    return output_filename

