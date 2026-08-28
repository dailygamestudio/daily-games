#!/usr/bin/env python3
"""
YouTube Uploader for Daily Game Studio Devlog Series
Handles authentication, upload, playlist management, scheduling, and thumbnails.
Requires: google-auth, google-auth-oauthlib, google-api-python-client
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import argparse

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️  YouTube API libraries not available. Install with:")
    print("   pip install google-auth google-auth-oauthlib google-api-python-client")

GAMES_DIR = Path("/home/ethan/Hermes Project/daily-games")
OUTPUT_DIR = GAMES_DIR / "video-pipeline" / "output"
CREDENTIALS_FILE = GAMES_DIR / "client_secret_469392085195-4o11dl9s2s30ssr1n5j8e597o2qvqn47.apps.googleusercontent.com.json"
TOKEN_FILE = GAMES_DIR / "youtube_credentials.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

PLAYLIST_TITLE = "Daily Game Studio Devlog Series"
PLAYLIST_DESCRIPTION = "Every day, an AI agent (Hermes) creates a complete HTML5 Canvas game from scratch. Watch the self-healing pipeline test, find bugs, and auto-fix them via NIM API (Nemotron 3 Ultra)."

def get_authenticated_service():
    """Get authenticated YouTube service"""
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"✗ Credentials file not found: {CREDENTIALS_FILE}")
                print("Please download OAuth client credentials from Google Cloud Console")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)

def get_or_create_playlist(youtube) -> str:
    """Get existing playlist ID or create new one"""
    # Search for existing playlist
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()
    
    for item in response.get("items", []):
        if item["snippet"]["title"] == PLAYLIST_TITLE:
            print(f"  ✓ Found existing playlist: {item['id']}")
            return item["id"]
    
    # Create new playlist
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": PLAYLIST_TITLE,
                "description": PLAYLIST_DESCRIPTION,
                "tags": ["AI gamedev", "HTML5 Canvas", "Daily Game Studio", "Nemotron 3 Ultra"],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    playlist_id = response["id"]
    print(f"  ✓ Created new playlist: {playlist_id}")
    return playlist_id

def upload_video(youtube, video_path: Path, metadata: Dict, playlist_id: str) -> Optional[str]:
    """Upload video to YouTube"""
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": "28",  # Science & Technology
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": "private",  # Start private, can change later
            "selfDeclaredMadeForKids": False
        }
    }
    
    # Add scheduling if specified
    if metadata.get("schedule"):
        body["status"]["publishAt"] = metadata["schedule"]
        body["status"]["privacyStatus"] = "private"
    
    # Media upload
    media = MediaFileUpload(
        str(video_path),
        chunksize=1024*1024,  # 1MB chunks
        resumable=True,
        mimetype="video/mp4"
    )
    
    print(f"  📤 Uploading: {video_path.name}")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    Progress: {int(status.progress() * 100)}%")
    
    video_id = response["id"]
    print(f"  ✓ Video uploaded: {video_id}")
    
    # Add to playlist
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()
    print(f"  ✓ Added to playlist")
    
    # Set thumbnail if exists
    thumb_path = video_path.parent / "assets" / "thumbnail.jpg"
    if thumb_path.exists():
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
        ).execute()
        print(f"  ✓ Thumbnail set")
    
    return video_id

def load_episode_metadata(ep_dir: Path) -> Optional[Dict]:
    meta_file = ep_dir / "youtube_metadata.json"
    if not meta_file.exists():
        return None
    return json.loads(meta_file.read_text())

def main():
    parser = argparse.ArgumentParser(description="Upload Daily Game Studio Devlog episodes to YouTube")
    parser.add_argument("--episode", type=int, help="Upload specific episode")
    parser.add_argument("--all", action="store_true", help="Upload all rendered episodes")
    parser.add_argument("--playlist-only", action="store_true", help="Only create/get playlist")
    args = parser.parse_args()
    
    if not YOUTUBE_API_AVAILABLE:
        print("Please install required packages first")
        return
    
    print("🔐 Authenticating with YouTube API...")
    youtube = get_authenticated_service()
    if not youtube:
        return
    
    print("📋 Getting/Creating playlist...")
    playlist_id = get_or_create_playlist(youtube)
    
    if args.playlist_only:
        print(f"Playlist ID: {playlist_id}")
        return
    
    episodes = []
    if args.episode:
        episodes = [args.episode]
    elif args.all:
        episodes = range(1, 55)
    else:
        episodes = [1]
    
    for ep_num in episodes:
        matches = list(OUTPUT_DIR.glob(f"ep{ep_num:02d}_*"))
        if not matches:
            print(f"Episode {ep_num} not found, skipping")
            continue
        ep_dir = matches[0]
        
        # Find video file
        video_files = list(ep_dir.glob("*_final.mp4"))
        if not video_files:
            print(f"No rendered video found for episode {ep_num}, skipping")
            continue
        video_path = video_files[0]
        
        metadata = load_episode_metadata(ep_dir)
        if not metadata:
            print(f"No metadata found for episode {ep_num}, skipping")
            continue
        
        print(f"\n📤 Uploading Episode #{ep_num:02d}: {metadata['title']}")
        video_id = upload_video(youtube, video_path, metadata, playlist_id)
        
        if video_id:
            # Save video ID to metadata
            metadata["video_id"] = video_id
            metadata["video_url"] = f"https://youtube.com/watch?v={video_id}"
            (ep_dir / "youtube_metadata.json").write_text(json.dumps(metadata, indent=2))
            print(f"  ✅ Episode {ep_num} uploaded successfully!")
        else:
            print(f"  ✗ Episode {ep_num} upload failed")
    
    print(f"\n✅ Upload complete! Playlist: https://youtube.com/playlist?list={playlist_id}")

if __name__ == "__main__":
    main()