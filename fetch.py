import os
import boto3
filename = 'blob'
local_file_path = os.path.join('/Users/rohitmeshram/Development/FE/finalproject16apr/eulerian-remote/videos' , filename)
s3_client = boto3.client('s3', aws_access_key_id='AKIAQSUFXSSL2EJNUZNE', aws_secret_access_key='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', region_name='ap-south-1')
s3_client.download_file('evm-rohit-next-bucket', filename, local_file_path)
print('success')