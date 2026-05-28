#!/usr/bin/env python3
"""Upload video to YouTube Shorts."""
import json, subprocess, os

# Get YouTube token
result = subprocess.run(
    ['curl', '-s', '-X', 'POST', 'https://oauth2.googleapis.com/token',
     '-d', 'client_id=' + os.environ['YOUTUBE_CLIENT_ID'],
     '-d', 'client_secret=' + os.environ['YOUTUBE_CLIENT_SECRET'],
     '-d', 'refresh_token=' + os.environ['YOUTUBE_REFRESH_TOKEN'],
     '-d', 'grant_type=refresh_token'],
    capture_output=True, text=True
)
token = json.loads(result.stdout)['access_token']

# Step 1: Start resumable upload with metadata
metadata = json.dumps({
    'snippet': {
        'title': 'Fasting Blood Sugar vs HbA1c #Shorts',
        'description': 'Fasting sugar vs HbA1c — which number actually matters? Most Indians obsess over fasting. The real story is HbA1c. Both needed.\n\n#Shorts #Diabetes #HbA1c #BloodSugar #Type1Diabetes #Type2Diabetes #IndianDiabetics',
        'categoryId': '22'
    },
    'status': {'privacyStatus': 'public', 'madeForKids': False}
})

# Start resumable upload
result = subprocess.run(
    ['curl', '-s', '-D', '/tmp/youtube_headers.txt', '-o', '/tmp/youtube_response.txt',
     '-X', 'POST',
     'https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&uploadType=resumable',
     '-H', 'Authorization: Bearer ' + token,
     '-H', 'Content-Type: application/json',
     '-d', metadata],
    capture_output=True, text=True
)
print('Start upload response:', result.stdout[:200] if result.stdout else '(empty)')

# Read Location header
upload_url = None
with open('/tmp/youtube_headers.txt') as f:
    for line in f:
        if line.startswith('Location:'):
            upload_url = line.strip().split(':', 1)[1].strip()
            break

if not upload_url:
    print('ERROR: No Location header in response')
    print('Headers:', open('/tmp/youtube_headers.txt').read()[:300])
    print('Response:', result.stdout[:300])
    exit(1)

print('Upload URL:', upload_url[:80] + '...')

# Step 2: Upload video data
result = subprocess.run(
    ['curl', '-s', '-D', '/tmp/youtube_final_headers.txt',
     '-X', 'PUT',
     upload_url,
     '-H', 'Content-Type: video/mp4',
     '-H', 'Content-Range: bytes 0-6999999/6999999',
     '--data-binary', '@/tmp/fastingsugar-hba1c-reel.mp4'],
    capture_output=True, text=True
)
print('Upload response:', result.stdout[:300])

# Get video ID
video_id = None
with open('/tmp/youtube_final_headers.txt') as f:
    for line in f:
        if 'watch?v=' in line:
            video_id = line.strip().split('watch?v=')[-1].strip()
            break

if video_id:
    print('YOUTUBE VIDEO ID:', video_id)
    # Update yt-queue
    queue = json.load(open('/home/openclaw/.openclaw/workspace/scripts/ig-scheduler/yt-queue.json'))
    queue.append({
        'slug': 'fasting-blood-sugar-vs-hba1c-which-matters',
        'status': 'posted',
        'posted_at': '2026-05-27T16:00:00Z',
        'video_id': video_id,
        'title': 'Fasting Blood Sugar vs HbA1c #Shorts',
        'platforms': ['youtube_shorts']
    })
    json.dump(queue, open('/home/openclaw/.openclaw/workspace/scripts/ig-scheduler/yt-queue.json', 'w'), indent=2)
    print('yt-queue updated')
else:
    print('ERROR: No video ID found')
    print('Final headers:', open('/tmp/youtube_final_headers.txt').read())
    print('Response body:', result.stdout[:500])
