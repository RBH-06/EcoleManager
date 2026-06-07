"""Google Drive helper functions for OAuth and file uploads.

This module provides minimal wrappers to authenticate with Google Drive
and upload files. It stores token and credentials under the app data dir.
"""
from __future__ import annotations

import os
from typing import Optional

# Third-party packages (installed via pip):
#   google-api-python-client, google-auth-httplib2, google-auth-oauthlib
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    _GOOGLE_DEPS_OK = True
except Exception:
    # Deps missing; caller should handle messaging to user
    _GOOGLE_DEPS_OK = False

# Minimal scope: can create and access files created by this app
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def google_deps_installed() -> bool:
    return _GOOGLE_DEPS_OK


def build_service(credentials_path: str, token_path: str):
    """Build an authenticated Drive v3 service.

    Ensures token exists/valid, runs local OAuth flow if needed.
    """
    if not _GOOGLE_DEPS_OK:
        raise RuntimeError(
            "Google Drive packages are not installed. Install: "
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Download an OAuth Client ID (Desktop app) JSON from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            # This opens a browser for user consent and handles redirect locally
            creds = flow.run_local_server(port=0)
        # Save token to disk
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    return service


def ensure_folder(service, name: str, parent_id: Optional[str] = None) -> str:
    """Return the folder ID with given name (under parent), creating it if missing."""
    q_parts = ["mimeType='application/vnd.google-apps.folder'", "trashed=false", f"name='{name}'"]
    if parent_id:
        q_parts.append(f"'{parent_id}' in parents")
    else:
        # Restrict to root if no parent specified
        q_parts.append("'root' in parents")
    q = " and ".join(q_parts)

    resp = service.files().list(q=q, spaces="drive", fields="files(id, name)", pageSize=1).execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"]

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        meta["parents"] = [parent_id]
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]


essential_fields = "id, webViewLink, name"

def upload_file(service, folder_id: str, local_path: str, dest_name: Optional[str] = None) -> dict:
    """Upload a local file to Drive inside the specified folder.

    Returns file metadata dict with at least id and webViewLink.
    """
    if dest_name is None:
        dest_name = os.path.basename(local_path)

    media = MediaFileUpload(local_path, mimetype="application/octet-stream", resumable=False)
    metadata = {"name": dest_name, "parents": [folder_id]}
    file = service.files().create(body=metadata, media_body=media, fields=essential_fields).execute()
    return file