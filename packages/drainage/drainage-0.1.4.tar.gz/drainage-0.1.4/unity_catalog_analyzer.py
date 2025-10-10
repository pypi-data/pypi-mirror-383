#!/usr/bin/env python3
"""
Unity Catalog Delta Lake analyzer for drainage
"""

import drainage
import boto3
from botocore.exceptions import ClientError
import json
import os

def analyze_unity_catalog_table(s3_path, aws_region="us-east-1"):
    """
    Analyze a Unity Catalog Delta table by finding the actual Delta log location
    """
    print(f"🔍 Analyzing Unity Catalog table: {s3_path}")
    
    # Parse the Unity Catalog S3 path
    if not s3_path.startswith("s3://"):
        raise ValueError("Not an S3 path")
    
    parts = s3_path[5:].split("/", 1)
    bucket = parts[0]
    unity_path = parts[1] if len(parts) > 1 else ""
    
    print(f"📦 Bucket: {bucket}")
    print(f"📁 Unity Path: {unity_path}")
    
    # Set up S3 client
    s3_client = boto3.client('s3', region_name=aws_region)
    
    # Look for Delta log in the Unity Catalog structure
    delta_log_paths = [
        f"{unity_path}/_delta_log/",
        f"{unity_path}/_delta_log",
        f"{unity_path}/delta_log/",
        f"{unity_path}/delta_log"
    ]
    
    actual_delta_path = None
    for delta_path in delta_log_paths:
        try:
            print(f"🔍 Checking for Delta log at: s3://{bucket}/{delta_path}")
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=delta_path,
                MaxKeys=1
            )
            
            if 'Contents' in response:
                actual_delta_path = f"s3://{bucket}/{delta_path.rstrip('/')}"
                print(f"✅ Found Delta log at: {actual_delta_path}")
                break
                
        except ClientError as e:
            print(f"❌ No Delta log at {delta_path}: {e.response['Error']['Code']}")
            continue
    
    if not actual_delta_path:
        # Try to find any JSON files that might be Delta logs
        print("🔍 Searching for Delta log files...")
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=unity_path,
                MaxKeys=100
            )
            
            if 'Contents' in response:
                json_files = [obj['Key'] for obj in response['Contents'] 
                            if obj['Key'].endswith('.json') and 'delta' in obj['Key'].lower()]
                
                if json_files:
                    print(f"📄 Found potential Delta files: {json_files[:5]}")
                    # Use the parent directory as the Delta log location
                    actual_delta_path = f"s3://{bucket}/{os.path.dirname(json_files[0])}"
                    print(f"✅ Using Delta log at: {actual_delta_path}")
                else:
                    raise ValueError("No Delta log files found in Unity Catalog path")
            else:
                raise ValueError("No files found in Unity Catalog path")
                
        except ClientError as e:
            raise ValueError(f"Failed to list objects in Unity Catalog path: {e}")
    
    # Now analyze using the found Delta log path
    print(f"🚀 Analyzing Delta table at: {actual_delta_path}")
    try:
        report = drainage.analyze_table(
            s3_path=actual_delta_path,
            aws_region=aws_region
        )
        return report
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise

def analyze_unity_catalog_tables(tables_df, aws_region="us-east-1"):
    """
    Analyze multiple Unity Catalog tables from a Spark DataFrame
    """
    results = []
    
    for table in tables_df.collect():
        table_name = table['tableName']
        print(f"\n{'='*60}")
        print(f"📊 Analyzing table: {table_name}")
        print(f"{'='*60}")
        
        try:
            # Get table location
            desc = spark.sql(f"DESCRIBE EXTENDED development.backend_dev.{table_name}")
            location_row = desc.filter(desc['col_name'] == 'Location').collect()
            
            if location_row:
                s3_path = location_row[0]['data_type']
                if s3_path.startswith("s3://") and "__unitystorage" in s3_path:
                    print(f"🔍 Unity Catalog Delta table: {s3_path}")
                    
                    try:
                        report = analyze_unity_catalog_table(s3_path, aws_region)
                        results.append({
                            'table_name': table_name,
                            's3_path': s3_path,
                            'report': report,
                            'status': 'success'
                        })
                        print(f"✅ Successfully analyzed {table_name}")
                        
                    except Exception as e:
                        print(f"❌ Failed to analyze {table_name}: {e}")
                        results.append({
                            'table_name': table_name,
                            's3_path': s3_path,
                            'error': str(e),
                            'status': 'failed'
                        })
                else:
                    print(f"⚠️  Skipping {table_name}: Not a Unity Catalog S3 table")
                    results.append({
                        'table_name': table_name,
                        's3_path': s3_path,
                        'status': 'skipped'
                    })
            else:
                print(f"⚠️  No location found for {table_name}")
                results.append({
                    'table_name': table_name,
                    'status': 'no_location'
                })
                
        except Exception as e:
            print(f"❌ Error processing {table_name}: {e}")
            results.append({
                'table_name': table_name,
                'error': str(e),
                'status': 'error'
            })
    
    return results

# Example usage for Databricks
def main():
    """Main function for Databricks usage"""
    print("🚀 Unity Catalog Delta Lake Analyzer")
    print("=" * 50)
    
    # Get all tables
    tables = spark.sql("SHOW TABLES IN development.backend_dev")
    
    # Analyze all Unity Catalog tables
    results = analyze_unity_catalog_tables(tables, aws_region="us-east-1")
    
    # Print summary
    print(f"\n📊 Analysis Summary:")
    print(f"Total tables: {len(results)}")
    print(f"Successful: {len([r for r in results if r['status'] == 'success'])}")
    print(f"Failed: {len([r for r in results if r['status'] == 'failed'])}")
    print(f"Skipped: {len([r for r in results if r['status'] == 'skipped'])}")
    
    # Print detailed results for successful analyses
    for result in results:
        if result['status'] == 'success':
            print(f"\n📋 {result['table_name']} Health Report:")
            print("-" * 40)
            drainage.print_health_report(result['report'])

if __name__ == "__main__":
    main()
