import os
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Demo mode for local development without Firebase
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

if not DEMO_MODE:
    cred = credentials.Certificate("firebase_adminsdk.json")
    firebase_admin.initialize_app(cred)

from enum import Enum
from typing import List, Dict, Optional, TypedDict, Annotated, Tuple
from typing import List, Dict, Optional, TypedDict, Annotated, Tuple, cast

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AppStatus(str, Enum):
    INFO_COLLECTION = "info_collection"
    STRATEGIZING = "strategizing"
    NEGOTIATING = "negotiating"
    ANALYSING = "analyzing"
    COMPLETED = "completed"

class CallStatus(str, Enum):
    CALL_INITIATED = "CALL_INITIATED"
    CALL_INPROGRESS = "CALL_INPROGRESS"
    CALL_COMPLETED = "CALL_COMPLETED"

class User(TypedDict):
    uid: str
    user_id: str
    email: str

class SessionData(TypedDict):
    status: AppStatus
    strategy: Optional[str]
    movers: Optional[List[str]]
    transcripts: Optional[List[str]]
    callSummaries: Optional[List[str]]
    recommendation: Optional[str]

# Mock database for demo mode
_mock_db = {}

if DEMO_MODE:
    db = None
    print("WARNING: Running in DEMO_MODE - Firebase disabled, using in-memory storage")
else:
    db = firestore.client()

def update_data(user_id: str, data: SessionData, merge = True):
    if DEMO_MODE:
        if user_id not in _mock_db:
            _mock_db[user_id] = {}
        if merge:
            _mock_db[user_id].update(data)
        else:
            _mock_db[user_id] = data
        print(f"Mock DB updated for {user_id}")
    else:
        db.collection('users').document(user_id).set(data, merge=merge)

def update_status(user_id: str, status: AppStatus):
    update_data(user_id, { "status": status })

def update_call_data(user_id: str, call_sid: str, data: Dict, merge=True):
    """
    Update the Firestore document at the path 'users/{user_id}/calls/{call_sid}' with the provided data.

    :param user_id: The ID of the user.
    :param call_sid: The SID of the call.
    :param data: The data to update in the Firestore document.
    :param merge: Whether to merge the data with existing data.
    """
    if DEMO_MODE:
        if user_id not in _mock_db:
            _mock_db[user_id] = {}
        if 'calls' not in _mock_db[user_id]:
            _mock_db[user_id]['calls'] = {}
        if call_sid not in _mock_db[user_id]['calls']:
            _mock_db[user_id]['calls'][call_sid] = {}
        if merge:
            _mock_db[user_id]['calls'][call_sid].update(data)
        else:
            _mock_db[user_id]['calls'][call_sid] = data
    else:
        db.collection('users').document(user_id).collection('calls').document(call_sid).set(data, merge=merge)

def get_call_data_as_json(user_id: str, call_sid: str) -> Optional[Dict]:
    """
    Retrieve the Firestore document at the path 'users/{user_id}/calls/{call_sid}' and return it as JSON.

    :param user_id: The ID of the user.
    :param call_sid: The SID of the call.
    :return: The document data as a dictionary, or None if the document does not exist.
    """
    if DEMO_MODE:
        if user_id in _mock_db and 'calls' in _mock_db[user_id]:
            return _mock_db[user_id]['calls'].get(call_sid)
        return None
    else:
        doc_ref = db.collection('users').document(user_id).collection('calls').document(call_sid)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        else:
            return None

auth_scheme = HTTPBearer(auto_error=False)

def verify_user(auth_token: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)):
    if DEMO_MODE:
        # In demo mode, return a mock user
        return cast(User, {"uid": "demo_user", "user_id": "demo_user", "email": "demo@movescout.com"})

    if not auth_token:
        raise HTTPException(status_code=401, detail="Auth token required")

    token = auth_token.credentials
    try:
        # Verify the token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(token)
        return cast(User, decoded_token)
    except firebase_admin.exceptions.FirebaseError as e:
        raise HTTPException(status_code=401, detail="Invalid Auth Token")