# travel_agent/utils.py
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
from django.conf import settings
from common . models import *

def send_fcm_notification_to_users(title, message, agent_name):
    """
    Sends an FCM push notification to all users using HTTP v1 API.

    Parameters:
    - title (str): The title of the notification.
    - message (str): The content/message of the notification.

    Returns:
    - dict: Response details from FCM.
    """
    try:
        # Load service account credentials from settings
        credentials = service_account.Credentials.from_service_account_file(
            settings.FIREBASE_CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )
        credentials.refresh(Request())
        access_token = credentials.token

        # Get project ID from service account file
        with open(settings.FIREBASE_CREDENTIALS_PATH, 'r') as f:
            project_id = json.load(f)["project_id"]

        # FCM HTTP v1 endpoint
        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

        # Headers with OAuth 2.0 token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Get all registered users' FCM tokens
        users = UserProfile.objects.filter(fcm_token__isnull=False)
        tokens = [user.fcm_token for user in users]

        if not tokens:
            return {"error": "No user tokens available"}

        # Message payload (multicast to multiple tokens, max 500 per request)
        payload = {
            "message": {
                "notification": {
                    "title": title,
                    "body": f"{message} from {agent_name}"
                },
                # "tokens": tokens[:500]  # Uncomment for multicast (up to 500)
            }
        }

        # Send to each token individually (simpler for small user bases)
        results = {"success_count": 0, "failure_count": 0, "errors": []}
        for token in tokens:
            payload["message"]["token"] = token
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
                results["errors"].append({
                    "token": token,
                    "error": response.json().get("error", "Unknown error")
                })

        return results

    except Exception as e:
        return {"error": str(e)}