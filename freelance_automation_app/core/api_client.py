from googleapiclient.discovery import build
from .auth_handler import AuthHandler # Corrected import

class ApiClient:
    def __init__(self, auth_handler):
        self.auth_handler = auth_handler
        self.gmail_service = None

    def get_gmail_service(self):
        if not self.gmail_service:
            # Use the AuthHandler to get the Gmail service
            self.gmail_service = self.auth_handler.get_gmail_service()
        return self.gmail_service

    def list_messages(self, query=''):
        """Lists messages in the user's mailbox matching the query."""
        service = self.get_gmail_service()
        if not service:
            print("Gmail service not available.")
            return []
        try:
            response = service.users().messages().list(userId='me', q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
            # Handle pagination if there are many messages (optional, for brevity)
            # while 'nextPageToken' in response:
            #     page_token = response['nextPageToken']
            #     response = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
            #     messages.extend(response['messages'])
            return messages
        except Exception as e:
            print(f'An error occurred: {e}')
            return []

    def get_message_details(self, message_id):
        """Gets the details of a specific message."""
        service = self.get_gmail_service()
        if not service:
            print("Gmail service not available.")
            return None
        try:
            message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
            return message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

# Example Usage (Optional - for testing purposes)
if __name__ == '__main__':
    # This assumes you have a valid credentials.json and token.pickle (or will generate one)
    # Make sure auth_handler.py is in the same directory or accessible via PYTHONPATH

    # Create a dummy credentials.json for testing if it doesn't exist
    import os
    if not os.path.exists('credentials.json'):
        print("Creating a dummy credentials.json for testing ApiClient.")
        print("Please replace it with your actual 'credentials.json' from Google Cloud Console.")
        dummy_credentials_content = {
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
            json.dump(dummy_credentials_content, f)

    print("Initializing AuthHandler for ApiClient testing...")
    # If auth_handler.py is in the same directory, this should work.
    # If it's in a parent directory (like 'core'), Python might not find it directly
    # when running api_client.py as the main script.
    # For robust testing, consider structuring as a package or adjusting sys.path.
    try:
        # Assuming auth_handler.py is in the same directory or Python can find it
        auth_handler = AuthHandler(credentials_file='credentials.json', token_file='token.pickle')
    except NameError: # Fallback if AuthHandler is not directly found (e.g. running script directly)
        print("AuthHandler not found directly, attempting relative import for script execution context.")
        # This path adjustment is for the specific case of running this script directly
        # and `auth_handler.py` being in the same directory.
        # For package structure, direct import `from .auth_handler import AuthHandler` is preferred.
        # import sys
        # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        # from auth_handler import AuthHandler # This might fail if not run as part of a package
        # auth_handler = AuthHandler(credentials_file='credentials.json', token_file='token.pickle')
        print("Cannot proceed with ApiClient test without AuthHandler. Ensure auth_handler.py is accessible.")
        exit()


    api_client = ApiClient(auth_handler)

    print("\nAttempting to get Gmail service via ApiClient...")
    gmail_service = api_client.get_gmail_service()

    if gmail_service:
        print("Successfully obtained Gmail service via ApiClient.")

        print("\nListing recent messages (no query):")
        messages = api_client.list_messages(query='is:unread in:inbox subject:"job alert" newer_than:7d') # Example query
        if messages:
            print(f"Found {len(messages)} messages.")
            # Get details for the first message (if any)
            if messages:
                first_message_id = messages[0]['id']
                print(f"\nGetting details for message ID: {first_message_id}")
                details = api_client.get_message_details(first_message_id)
                if details:
                    print("Message Snippet:", details.get('snippet'))
                    # You can print more details here if needed
                else:
                    print("Could not retrieve message details.")
        else:
            print("No messages found matching the query.")
    else:
        print("Failed to obtain Gmail service via ApiClient.")

    # Clean up dummy files if they were created by this script's test
    # Be cautious with auto-removing files, especially 'token.pickle'
    # if os.path.exists('credentials.json') and "YOUR_CLIENT_ID" in open('credentials.json').read():
        # os.remove('credentials.json')
        # print("Cleaned up dummy credentials.json created for ApiClient test.")
    print("\nApiClient test finished.")
