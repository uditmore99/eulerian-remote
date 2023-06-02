import cv2
import pyramids
import heartrate
import preprocessing
import eulerian
import boto3
import botocore
import sys
import os
from dotenv import load_dotenv
# AWS S3 bucket credentials
load_dotenv()
access_key = os.getenv('S3_ACCESS_KEY');
secret_key = os.getenv('S3_SECRET_ACCESS_KEY');
bucket_name = "evm-rohit-next-bucket"
video_file_key = "blob"

local_file_path = os.path.join(os.getcwd(), video_file_key)
# Frequency range for Fast-Fourier Transform
freq_min = 1
freq_max = 1.8

# Preprocessing phase
print("Reading + preprocessing video...")
s3 = boto3.client('s3',region_name='ap-south-1', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
try:
    s3.download_file(bucket_name, video_file_key, local_file_path)
    video_frames, frame_ct, fps = preprocessing.read_video(local_file_path)
except botocore.exceptions.NoCredentialsError:
    print("Failed to access S3 bucket. Check your credentials.")
    sys.exit(1)
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The video file does not exist in the S3 bucket.")
    else:
        print("An error occurred while downloading the video file:", e)
    sys.exit(1)

# Build Laplacian video pyramid
print("Building Laplacian video pyramid...")
lap_video = pyramids.build_video_pyramid(video_frames)

amplified_video_pyramid = []

for i, video in enumerate(lap_video):
    if i == 0 or i == len(lap_video)-1:
        continue

    # Eulerian magnification with temporal FFT filtering
    print("Running FFT and Eulerian magnification...")
    result, fft, frequencies = eulerian.fft_filter(video, freq_min, freq_max, fps)
    lap_video[i] += result

    # Calculate heart rate
    print("Calculating heart rate...")
    heart_rate = heartrate.find_heart_rate(fft, frequencies, freq_min, freq_max)

# Collapse laplacian pyramid to generate final video
print("Rebuilding final video...")
amplified_frames = pyramids.collapse_laplacian_video_pyramid(lap_video, frame_ct)

# Output heart rate and final video
print("Heart rate: ", heart_rate)

#Cleanup downloaded video file
os.remove(local_file_path)

