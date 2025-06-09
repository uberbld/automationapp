import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes required for the Google APIs you want to access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] # Example: Gmail API

class AuthHandler:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None # Initialize service to None

    def authenticate(self):
        """Authenticates the user and obtains credentials."""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        return self.creds

    def get_gmail_service(self):
        """Returns an authenticated Gmail API service client."""
        if not self.creds:
            self.authenticate()

        # Check if service is already built
        if not self.service:
            try:
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                print(f"An error occurred while building the Gmail service: {e}")
                return None
        return self.service

# Example Usage (Optional - for testing purposes)
if __name__ == '__main__':
    # Create a dummy credentials.json for testing if it doesn't exist
    # Important: Replace this with your actual credentials.json for real use
    if not os.path.exists('credentials.json'):
        print("Creating a dummy credentials.json for testing.")
        print("Please replace it with your actual 'credentials.json' from Google Cloud Console.")
        dummy_credentials = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                "project_id": "YOUR_PROJECT_ID",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": ["http://localhost"]
            }
        }
        import json
        with open('credentials.json', 'w') as f:
            json.dump(dummy_credentials, f)

    auth_handler = AuthHandler()

    print("Attempting to authenticate and get Gmail service...")
    gmail_service = auth_handler.get_gmail_service()

    if gmail_service:
        print("Successfully authenticated and obtained Gmail service.")
        # You can add more test calls here, e.g., list labels
        try:
            results = gmail_service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            if not labels:
                print('No labels found.')
            else:
                print('Labels:')
                for label in labels:
                    print(f"- {label['name']}")
        except Exception as e:
            print(f"An error occurred while trying to use the Gmail service: {e}")
            print("This might be due to the dummy credentials or API not being enabled.")
    else:
        print("Failed to authenticate or obtain Gmail service.")

    # Clean up dummy files if they were created
    if os.path.exists('token.pickle'):
        # os.remove('token.pickle') # Comment out if you want to keep token for faster subsequent tests
        pass
    # if os.path.exists('credentials.json') and "YOUR_CLIENT_ID" in open('credentials.json').read():
        # os.remove('credentials.json') # Be careful not to remove actual credentials
        # pass
    print("Test finished. Remember to use actual credentials for real application.")
