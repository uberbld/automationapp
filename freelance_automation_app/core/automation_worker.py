import time
import logging
from datetime import datetime
# Assuming other necessary core modules are in the same directory or package
from .llm_handler import LLMHandler
from .api_client import ApiClient
from .bidding_strategy import BiddingStrategy
from ..db.database_manager import DatabaseManager # Corrected relative import for db

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    handlers=[logging.StreamHandler()]) # Add more handlers as needed, e.g., FileHandler

class AutomationWorker:
    def __init__(self, config):
        self.config = config
        self.db_manager = DatabaseManager(db_name=config.get('DATABASE_NAME', 'freelance_jobs.db'))
        self.llm_handler = LLMHandler(api_key=config.get('OPENAI_API_KEY'))

        # Initialize ApiClient if Gmail integration is enabled
        if config.get('ENABLE_GMAIL_INTEGRATION', False):
            # This assumes AuthHandler is implicitly used by ApiClient and configured
            # or that ApiClient handles its auth dependencies.
            # auth_handler might need to be explicitly initialized and passed if not.
            from .auth_handler import AuthHandler # Ensure AuthHandler is available
            self.auth_handler = AuthHandler(
                credentials_file=config.get('GMAIL_CREDENTIALS_FILE', 'credentials.json'),
                token_file=config.get('GMAIL_TOKEN_FILE', 'token.pickle')
            )
            self.api_client = ApiClient(self.auth_handler)
        else:
            self.api_client = None

        # Bidding strategy setup (can be platform-specific)
        # For now, a generic one. This might be a dictionary of strategies by platform.
        self.bidding_strategies = {}
        if config.get('PLATFORM_CREDENTIALS'):
            for platform, creds in config.get('PLATFORM_CREDENTIALS').items():
                # This assumes a BiddingStrategy class that can handle different platforms
                # or specific strategy classes per platform.
                self.bidding_strategies[platform.lower()] = BiddingStrategy(
                    platform_url=creds.get('login_url'),
                    login_credentials={'username': creds.get('username'), 'password': creds.get('password')}
                )

        self.user_profile = config.get('USER_PROFILE_FOR_LLM', "A highly skilled freelancer.")


    def fetch_new_jobs_from_email_alerts(self):
        if not self.api_client:
            logging.info("Gmail integration is disabled. Skipping email job fetching.")
            return []

        logging.info("Fetching new job alerts from Gmail...")
        # Define your query for job alert emails
        # This query can be customized based on common subjects or senders of job alerts
        query = self.config.get('GMAIL_JOB_ALERT_QUERY', 'subject:"job alert" is:unread newer_than:7d')
        messages = self.api_client.list_messages(query=query)

        processed_jobs = []
        for msg_summary in messages:
            msg_id = msg_summary['id']
            job_details = self.api_client.get_message_details(msg_id) # This should parse the email
            if job_details:
                # TODO: Implement robust parsing of email content to extract job info
                # For now, let's assume get_message_details returns a dict with:
                # {'title': ..., 'url': ..., 'description': ..., 'platform': ..., 'date_posted': ...}
                # This parsing logic will be highly dependent on email format.

                # Example of what you might get from parsing (needs actual implementation)
                # parsed_info = self._parse_job_email(job_details) # You'd need this method

                # Placeholder for parsed info (replace with actual parsing)
                parsed_info = {
                    'title': f"Job from email {msg_id}", # Placeholder
                    'url': f"http://example.com/job/{msg_id}", # Placeholder, extract actual URL
                    'description': job_details.get('snippet', 'No description available.'), # Use snippet as placeholder
                    'platform': "EmailAlert", # Or try to determine from email
                    'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Use current time as placeholder
                }

                if self.db_manager.get_job_by_url(parsed_info['url']):
                    logging.info(f"Job already exists in DB (URL: {parsed_info['url']}), skipping.")
                    continue

                job_id = self.db_manager.add_job(
                    title=parsed_info['title'],
                    platform=parsed_info['platform'],
                    url=parsed_info['url'],
                    description=parsed_info['description'],
                    date_posted=parsed_info['date_posted']
                )
                if job_id:
                    logging.info(f"Added new job from email: {parsed_info['title']}")
                    processed_jobs.append({**parsed_info, 'id': job_id})

                # Optional: Mark email as read or label it after processing
                # self.api_client.modify_message_labels(msg_id, add_labels=['Processed'], remove_labels=['UNREAD'])
        return processed_jobs

    def _parse_job_email(self, email_data):
        # TODO: Implement logic to parse job details from email content (HTML/text)
        # This is a complex part and depends heavily on the email formats.
        # You might use BeautifulSoup for HTML emails or regex for text.
        # Return a dictionary like:
        # {'title': '...', 'url': '...', 'description': '...', 'platform': '...', 'date_posted': '...'}
        logging.warning("_parse_job_email is not fully implemented. Using placeholders.")
        return {
            'title': "Placeholder Parsed Job Title",
            'url': f"http://example.com/parsed-job/{time.time()}", # Ensure unique URL for testing
            'description': email_data.get('snippet', "Placeholder description from email snippet."),
            'platform': "ParsedFromEmail", # Or attempt to identify
            'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def find_and_apply_for_jobs(self):
        logging.info("Starting job search and application process...")
        self.db_manager.connect() # Ensure DB is connected

        # 1. Fetch new jobs from emails (if enabled)
        if self.config.get('ENABLE_GMAIL_INTEGRATION', False):
            email_jobs = self.fetch_new_jobs_from_email_alerts()
            # These jobs are already added to the DB

        # 2. TODO: Fetch jobs from other sources (e.g., direct platform scraping, RSS feeds)
        # For now, we'll work with jobs already in the DB or added via email

        # 3. Process jobs from the database that are 'New'
        new_jobs = self.db_manager.search_jobs(keyword='') # Get all jobs, then filter by status 'New'
                                                        # Or add a get_jobs_by_status('New') method

        for job_data_tuple in new_jobs:
            # Convert tuple to a more usable dict
            job = dict(zip([col[0] for col in self.db_manager.cursor.description], job_data_tuple))

            if job['status'] != 'New': # Process only new jobs
                continue

            logging.info(f"Processing job: {job['title']} from {job['platform']}")

            # 4. Generate cover letter/proposal using LLM
            cover_letter_template = self.config.get('COVER_LETTER_TEMPLATE', "Default cover letter prompt part.")
            # The user_profile is already initialized in self.user_profile

            # Construct a more detailed user profile or use specific parts for the prompt
            full_user_info_for_prompt = f"{self.user_profile}\n{cover_letter_template}"

            proposal = self.llm_handler.generate_cover_letter(
                job_title=job['title'],
                job_description=job['description'],
                user_profile=full_user_info_for_prompt # Pass the combined profile and template
            )

            if not proposal:
                logging.error(f"Failed to generate proposal for {job['title']}. Skipping.")
                self.db_manager.update_job_status(job['id'], 'Error - Proposal Generation Failed')
                continue

            logging.info(f"Generated proposal for {job['title']}:\n{proposal[:150]}...") # Log snippet

            # 5. Apply/Bid on the platform (if strategy exists)
            platform_name = job['platform'].lower()
            if platform_name in self.bidding_strategies:
                bidding_strategy = self.bidding_strategies[platform_name]
                try:
                    logging.info(f"Attempting to log in to {platform_name}...")
                    if bidding_strategy.login(): # login method in BiddingStrategy
                        logging.info(f"Logged in to {platform_name}. Placing bid for {job['title']}.")
                        # job_details for bidding_strategy should match what it expects
                        # e.g. {'url': job_url, 'title': job_title, ...}
                        bid_successful = bidding_strategy.place_bid(job, proposal) # Pass the job dict

                        if bid_successful:
                            self.db_manager.update_job_status(job['id'], 'Applied')
                            self.db_manager.update_job_application_date(job['id'])
                            self.db_manager.add_note_to_job(job['id'], f"Applied with generated proposal. Proposal: {proposal[:200]}...")
                            logging.info(f"Successfully applied for job: {job['title']}")
                        else:
                            self.db_manager.update_job_status(job['id'], 'Error - Bidding Failed')
                            logging.error(f"Failed to place bid for {job['title']} on {platform_name}.")
                    else:
                        logging.error(f"Login failed for platform: {platform_name}. Skipping bid.")
                        self.db_manager.update_job_status(job['id'], 'Error - Login Failed')
                except Exception as e:
                    logging.error(f"Exception during bidding process for {job['title']}: {e}")
                    self.db_manager.update_job_status(job['id'], 'Error - Bidding Exception')
                finally:
                    bidding_strategy.close_browser() # Ensure browser is closed
            else:
                logging.warning(f"No bidding strategy found for platform: {platform_name}. Manual application required for {job['title']}.")
                self.db_manager.update_job_status(job['id'], 'Manual Application Required')
                self.db_manager.add_note_to_job(job['id'], f"Proposal generated. Manual application needed. Proposal: {proposal[:200]}...")


            # Add a delay to avoid overwhelming services or getting rate-limited
            time.sleep(self.config.get('DELAY_BETWEEN_APPLICATIONS_SEC', 30))

        self.db_manager.close()
        logging.info("Job application cycle finished.")

# Example Usage (Illustrative - requires a config dict)
if __name__ == '__main__':
    # This is a simplified example.
    # In a real app, config would come from a file or environment variables.
    dummy_config = {
        'DATABASE_NAME': 'test_automation_jobs.db',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY_TEST'), # Ensure this is set in your .env for testing
        'ENABLE_GMAIL_INTEGRATION': False, # Set to True to test Gmail fetching (requires credentials.json)
        # 'GMAIL_CREDENTIALS_FILE': 'path/to/your/credentials.json',
        # 'GMAIL_TOKEN_FILE': 'path/to/your/token.pickle',
        # 'GMAIL_JOB_ALERT_QUERY': 'subject:"job opportunity" is:unread newer_than:2d',
        'USER_PROFILE_FOR_LLM': "I am a freelance writer with 5 years of experience in tech blogging.",
        'COVER_LETTER_TEMPLATE': "My skills in X, Y, and Z make me a good fit.",
        # 'PLATFORM_CREDENTIALS': {
        #     'ExamplePlatform': { # Replace with a real platform key if BiddingStrategy supports it
        #         'login_url': 'https://www.example-freelance-platform.com/login',
        #         'username': 'your_platform_username',
        #         'password': 'your_platform_password'
        #     }
        # },
        'DELAY_BETWEEN_APPLICATIONS_SEC': 5 # Short delay for testing
    }

    if not dummy_config['OPENAI_API_KEY']:
        print("Error: OPENAI_API_KEY_TEST not found in environment for testing. Skipping worker test.")
    else:
        print("Initializing AutomationWorker with dummy config...")
        worker = AutomationWorker(dummy_config)

        # Setup: Add a dummy job to the test database for the worker to process
        worker.db_manager.connect()
        # Clear existing test jobs for a clean run (optional)
        # worker.db_manager.cursor.execute("DELETE FROM jobs")
        # worker.db_manager.conn.commit()

        job_id_test = worker.db_manager.add_job(
            title="Test Freelance Writer Job",
            platform="ExamplePlatform", # Matches a key in PLATFORM_CREDENTIALS if testing bidding
            url="http://example.com/job/testwriter123",
            description="Looking for a skilled writer for a short-term blog project on AI.",
            date_posted=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            status="New"
        )
        if job_id_test:
            print(f"Added dummy job with ID: {job_id_test} for worker to process.")
        else:
            # If it already exists from a previous run, try to process it anyway
            print("Dummy job may already exist. Worker will attempt to process 'New' jobs.")
        worker.db_manager.close() # Close connection so worker can reopen

        print("\nStarting AutomationWorker process...")
        worker.find_and_apply_for_jobs()
        print("\nAutomationWorker process finished.")

        # Clean up: Remove the test database
        # try:
        #     if os.path.exists(dummy_config['DATABASE_NAME']):
        #         os.remove(dummy_config['DATABASE_NAME'])
        #         print(f"Cleaned up test database: {dummy_config['DATABASE_NAME']}")
        # except Exception as e:
        #     print(f"Error cleaning up test database: {e}")

        # Clean up token.pickle if created by auth_handler during test
        # if os.path.exists('token.pickle'):
        #     os.remove('token.pickle')
        #     print("Cleaned up token.pickle")
