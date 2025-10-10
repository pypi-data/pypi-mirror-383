#!/usr/bin/env python3
"""
Debug script to test S3 access in Databricks environment
"""

import drainage
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_s3_access(s3_path, aws_region="us-east-1"):
    """Test S3 access step by step"""
    print(f"🔍 Testing S3 access for: {s3_path}")
    
    # Parse S3 path
    if not s3_path.startswith("s3://"):
        print("❌ Not an S3 path")
        return False
    
    parts = s3_path[5:].split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    
    print(f"📦 Bucket: {bucket}")
    print(f"📁 Prefix: {prefix}")
    
    try:
        # Test 1: Basic AWS credentials
        print("\n1️⃣ Testing AWS credentials...")
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if not credentials:
            print("❌ No AWS credentials found")
            return False
        
        print(f"✅ AWS credentials found: {credentials.access_key[:8]}...")
        
        # Test 2: S3 client creation
        print("\n2️⃣ Testing S3 client creation...")
        s3_client = boto3.client('s3', region_name=aws_region)
        print(f"✅ S3 client created for region: {aws_region}")
        
        # Test 3: Bucket access
        print("\n3️⃣ Testing bucket access...")
        try:
            s3_client.head_bucket(Bucket=bucket)
            print(f"✅ Bucket {bucket} is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket {bucket} not found")
            elif error_code == '403':
                print(f"❌ Access denied to bucket {bucket}")
            else:
                print(f"❌ Error accessing bucket: {error_code}")
            return False
        
        # Test 4: List objects
        print("\n4️⃣ Testing object listing...")
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=10
            )
            
            if 'Contents' in response:
                print(f"✅ Found {len(response['Contents'])} objects")
                for obj in response['Contents'][:3]:  # Show first 3
                    print(f"   - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print(f"⚠️  No objects found with prefix: {prefix}")
                
        except ClientError as e:
            print(f"❌ Error listing objects: {e}")
            return False
        
        # Test 5: Try drainage analysis
        print("\n5️⃣ Testing drainage analysis...")
        try:
            report = drainage.analyze_table(
                s3_path=s3_path,
                aws_region=aws_region
            )
            print("✅ Drainage analysis successful!")
            return True
            
        except Exception as e:
            print(f"❌ Drainage analysis failed: {e}")
            return False
            
    except NoCredentialsError:
        print("❌ No AWS credentials configured")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main debug function"""
    print("🐛 S3 Access Debug Tool")
    print("=" * 50)
    
    # Test with the Unity Catalog path
    s3_path = "s3://development-unity-catalog/backend_dev/__unitystorage/schemas/d42c4578-6050-45f5-80da-0499d2e4ac4d/tables/56b9c765-c770-475c-8ff7-1fd03d557e5d"
    
    success = test_s3_access(s3_path)
    
    if success:
        print("\n🎉 All tests passed! S3 access is working.")
    else:
        print("\n💡 Troubleshooting suggestions:")
        print("1. Check if AWS credentials are configured in Databricks")
        print("2. Verify S3 bucket permissions")
        print("3. Check if the S3 path exists and is accessible")
        print("4. Try with a different AWS region")

if __name__ == "__main__":
    main()
