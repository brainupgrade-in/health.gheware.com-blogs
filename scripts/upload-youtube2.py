#!/usr/bin/env python3
"""Upload video to YouTube Shorts - retry."""
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

# Start resumable upload
metadata = json.dumps({
    'snippet': {
        'title': 'Fasting Blood Sugar vs HbA1c #Shorts',
        'description': 'Fasting sugar vs HbA1c — which number actually matters? Most Indians obsess over fasting. The real story is HbA1c. Both needed.\n\n#Shorts #Diabetes #HbA1c #BloodSugar #Type1Diabetes #Type2Diabetes #IndianDiabetics',
        'categoryId': '22'
    },
    'status': {'privacyStatus': 'public', 'madeForKids': False}
})

# Use -L to follow redirects and capture headers properly
result = subprocess.run(
    ['curl', '-s', '-D', '/tmp/yh.txt', '-o', '/tmp/yr.txt',
     '-X', 'POST',
     'https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&uploadType=resumable',
     '-H', 'Authorization: Bearer ' + token,
     '-H', 'Content-Type: application/json',
     '-d', metadata],
    capture_output=True, text=True
)

# Parse Location from headers
upload_url = None
with open('/tmp/yh.txt') as f:
    for line in f:
        line = line.strip()
        if line.lower().startswith('location:'):
            upload_url = line[9:].strip()
            break

if not upload_url:
    print('ERROR: No Location header')
    print('Headers:', open('/tmp/yh.txt').read())
    exit(1)

print('Upload URL:', upload_url)

# Upload video
result = subprocess.run(
    ['curl', '-s', '-D', '/tmp/yhf.txt',
     '-X', 'PUT',
     upload_url,
     '-H', 'Content-Type: video/mp4',
     '-H', 'Content-Range: bytes 0-6999999/6999999',
     '--data-binary', '@/tmp/fastingsugar-hba1c-reel.mp4'],
    capture_output=True, text=True
)

print('Upload status code from response:', result.stdout[:100])

# Parse video ID from headers or response
video_id = None
# Check response body first
if result.stdout:
    resp = json.loads(result.stdout)
    video_id = resp.get('id', '')
    if video_id:
        print('Video ID from response body:', video_id)

# Check headers for watch URL
if not video_id:
    with open('/tmp/yhf.txt') as f:
        for line in f:
            if 'watch?v=' in line:
                video_id = line.strip().split('watch?v=')[-1].strip()
                print('Video ID from header:', video_id)
                break

if video_id:
    print('SUCCESS! Video ID:', video_id)
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
    
    # Report to dashboard
    subprocess.run([
        'curl', '-s', '-X', 'POST', 'https://agentgrow.io/admin/agent-updates',
        '-H', 'Authorization: Bearer ' + os.environ['AGENTGROW_API_KEY'],
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'client_email': 'alex@gheware.com',
            'category': 'youtube',
            'title': 'Fasting Blood Sugar vs HbA1c #Shorts',
            'summary': 'YouTube Shorts published',
            'url': 'https://youtube.com/shorts/' + video_id,
            'module_key': 'youtube',
            'action_count': 1
        })
    ], capture_output=True)
else:
    print('ERROR: No video ID found')
    print('Response:', result.stdout[:500])
    print('Headers:', open('/tmp/yhf.txt').read())
