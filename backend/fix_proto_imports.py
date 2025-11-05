#!/usr/bin/env python3
"""
Fix proto imports after generation.
Changes absolute import to relative import in sales_pb2_grpc.py
"""
import os
import re

def fix_proto_imports():
    """Fix the import statement in generated proto file."""
    proto_file = os.path.join(os.path.dirname(__file__), 'proto', 'sales_pb2_grpc.py')
    
    if not os.path.exists(proto_file):
        print(f"Error: {proto_file} not found. Generate proto files first.")
        return False
    
    with open(proto_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for various import patterns and fix them
    # Fix duplicate "from ." patterns first
    content = re.sub(r'from \. from \. import', 'from . import', content)
    content = re.sub(r'from \. from \. from \. import', 'from . import', content)
    
    patterns_to_fix = [
        ('import sales_pb2 as sales__pb2', 'from . import sales_pb2 as sales__pb2'),
    ]
    
    fixed = False
    for old_pattern, new_pattern in patterns_to_fix:
        if old_pattern in content and old_pattern != new_pattern:
            content = content.replace(old_pattern, new_pattern)
            fixed = True
            print(f"Fixed import: {old_pattern} -> {new_pattern}")
            break
    
    if fixed or 'from . import sales_pb2 as sales__pb2' not in content:
        # Check if we need to fix duplicate "from ."
        if 'from . from .' in content:
            content = re.sub(r'from \. from \. import', 'from . import', content)
            fixed = True
            print("Fixed duplicate 'from .' pattern")
    
    if fixed:
        with open(proto_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed import in {proto_file}")
        return True
    elif 'from . import sales_pb2 as sales__pb2' in content:
        print("Import already correct!")
        return True
    else:
        print("Warning: Could not find expected import statement.")
        print("Current imports in file:")
        for line in content.split('\n')[:10]:
            if 'import' in line:
                print(f"  {line}")
        return False

if __name__ == '__main__':
    fix_proto_imports()

