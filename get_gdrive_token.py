#!/usr/bin/env python3
"""
One-time script to authorize Google Drive access and get a refresh token.

Run this locally ONCE to get the refresh token, then add it to GitHub Secrets.

Usage:
    1. Download your OAuth credentials JSON from Google Cloud Console
    2. Run: python get_gdrive_token.py path/to/credentials.json
    3. Follow the browser authorization flow
    4. Copy the refresh token and add it to GitHub Secrets as GDRIVE_REFRESH_TOKEN
"""

import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Scope for uploading files to Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_refresh_token(credentials_file: str):
    """Run OAuth flow and print the refresh token."""
    
    print("\n=== Google Drive OAuth Setup ===\n")
    
    # Load credentials from file
    try:
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find credentials file: {credentials_file}")
        print("\nPlease download the OAuth credentials JSON from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services → Credentials")
        print("4. Click on your OAuth 2.0 Client ID")
        print("5. Click 'Download JSON'")
        sys.exit(1)
    
    # Extract client info
    if 'installed' in creds_data:
        client_info = creds_data['installed']
    elif 'web' in creds_data:
        client_info = creds_data['web']
    else:
        print("Error: Invalid credentials file format")
        sys.exit(1)
    
    print(f"Client ID: {client_info['client_id'][:50]}...")
    print(f"Project: {client_info.get('project_id', 'N/A')}")
    print("\nStarting authorization flow...")
    print("A browser window will open for you to authorize access.\n")
    
    # Run the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    credentials = flow.run_local_server(port=8080)
    
    print("\n" + "=" * 60)
    print("SUCCESS! Authorization complete.")
    print("=" * 60)
    
    print("\n📋 Add these to your GitHub Secrets:\n")
    print(f"GDRIVE_CLIENT_ID:\n{client_info['client_id']}\n")
    print(f"GDRIVE_CLIENT_SECRET:\n{client_info['client_secret']}\n")
    print(f"GDRIVE_REFRESH_TOKEN:\n{credentials.refresh_token}\n")
    
    print("=" * 60)
    print("\nGitHub Secrets setup:")
    print("1. Go to your repository on GitHub")
    print("2. Settings → Secrets and variables → Actions")
    print("3. Add the three secrets above")
    print("4. You can delete the old GDRIVE_SERVICE_ACCOUNT_KEY secret")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_gdrive_token.py <path-to-credentials.json>")
        print("\nExample: python get_gdrive_token.py ~/Downloads/client_secret_123.json")
        sys.exit(1)
    
    get_refresh_token(sys.argv[1])


