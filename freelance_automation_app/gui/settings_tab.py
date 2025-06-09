import streamlit as st
import json
import os

# Define the path for the configuration file
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json') # Store in parent dir

# Default configuration settings
DEFAULT_CONFIG = {
    "OPENAI_API_KEY": "",
    "DATABASE_NAME": "freelance_jobs.db",
    "ENABLE_GMAIL_INTEGRATION": False,
    "GMAIL_CREDENTIALS_FILE": "credentials.json",
    "GMAIL_TOKEN_FILE": "token.pickle",
    "GMAIL_JOB_ALERT_QUERY": "subject:\"job alert\" is:unread newer_than:7d",
    "USER_PROFILE_FOR_LLM": "A highly skilled and experienced freelance professional.",
    "COVER_LETTER_TEMPLATE": "Dear Hiring Manager,\n\nI am very interested in this opportunity...",
    "PLATFORM_CREDENTIALS": {
        "ExamplePlatform1": {
            "login_url": "https://platform1.com/login",
            "username": "",
            "password": ""
        },
        "ExamplePlatform2": {
            "login_url": "https://platform2.com/login",
            "username": "",
            "password": ""
        }
    },
    "DELAY_BETWEEN_APPLICATIONS_SEC": 30,
    "LOG_LEVEL": "INFO"
}

def load_config():
    """Loads configuration from JSON file, or returns defaults if not found."""
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
                # Ensure all default keys are present
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                    # Ensure nested defaults for PLATFORM_CREDENTIALS
                    elif key == "PLATFORM_CREDENTIALS":
                        for p_key, p_value in DEFAULT_CONFIG["PLATFORM_CREDENTIALS"].items():
                            if p_key not in config[key]:
                                config[key][p_key] = p_value
                return config
        except json.JSONDecodeError:
            st.error("Error decoding config.json. Using default settings.")
            return DEFAULT_CONFIG.copy() # Return a copy to avoid modifying global default
    return DEFAULT_CONFIG.copy() # Return a copy

def save_config(config_data):
    """Saves configuration to JSON file."""
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_data, f, indent=4)
        st.success(f"Configuration saved to {CONFIG_FILE_PATH}")
    except Exception as e:
        st.error(f"Error saving configuration: {e}")

def display_settings():
    st.subheader("Application Settings")

    config = load_config()

    # OpenAI Settings
    st.markdown("#### OpenAI Configuration")
    config["OPENAI_API_KEY"] = st.text_input(
        "OpenAI API Key",
        value=config.get("OPENAI_API_KEY", ""),
        type="password",
        help="Your API key for OpenAI services (GPT)."
    )

    # Database Settings
    st.markdown("#### Database Configuration")
    config["DATABASE_NAME"] = st.text_input(
        "Database File Name",
        value=config.get("DATABASE_NAME", "freelance_jobs.db"),
        help="Name of the SQLite database file (e.g., jobs.db)."
    )

    # Gmail Integration Settings
    st.markdown("#### Gmail Integration")
    config["ENABLE_GMAIL_INTEGRATION"] = st.checkbox(
        "Enable Gmail Integration for Job Alerts",
        value=config.get("ENABLE_GMAIL_INTEGRATION", False)
    )
    if config["ENABLE_GMAIL_INTEGRATION"]:
        config["GMAIL_CREDENTIALS_FILE"] = st.text_input(
            "Gmail Credentials File",
            value=config.get("GMAIL_CREDENTIALS_FILE", "credentials.json"),
            help="Path to your Gmail API credentials.json file."
        )
        # GMAIL_TOKEN_FILE is usually auto-generated, maybe not directly editable here
        st.text(f"Gmail Token File (auto-generated): {config.get('GMAIL_TOKEN_FILE', 'token.pickle')}")
        config["GMAIL_JOB_ALERT_QUERY"] = st.text_area(
            "Gmail Query for Job Alerts",
            value=config.get("GMAIL_JOB_ALERT_QUERY", 'subject:"job alert" is:unread newer_than:7d'),
            help="Gmail search query to find job alert emails."
        )

    # LLM and Proposal Settings
    st.markdown("#### LLM & Proposal Customization")
    config["USER_PROFILE_FOR_LLM"] = st.text_area(
        "Your Profile/Resume Highlights (for LLM)",
        value=config.get("USER_PROFILE_FOR_LLM", ""),
        height=150,
        help="Brief summary of your skills and experience for the LLM to use in proposals."
    )
    config["COVER_LETTER_TEMPLATE"] = st.text_area(
        "Base Cover Letter Template (for LLM)",
        value=config.get("COVER_LETTER_TEMPLATE", ""),
        height=200,
        help="A base template or key phrases for the LLM to build cover letters upon."
    )

    # Platform Credentials - Dynamic handling
    st.markdown("#### Freelance Platform Credentials")
    st.caption("Configure login details for platforms you use. The BiddingStrategy will use these.")

    platform_creds = config.get("PLATFORM_CREDENTIALS", {})

    # Display existing platforms
    for platform_name, creds in list(platform_creds.items()): # Use list to allow modification during iteration
        with st.expander(f"Platform: {platform_name}", expanded=False):
            new_platform_name = st.text_input(f"Platform Name ({platform_name})", value=platform_name, key=f"name_{platform_name}")
            login_url = st.text_input(f"Login URL ({platform_name})", value=creds.get('login_url', ''), key=f"url_{platform_name}")
            username = st.text_input(f"Username ({platform_name})", value=creds.get('username', ''), key=f"user_{platform_name}")
            password = st.text_input(f"Password ({platform_name})", value=creds.get('password', ''), type="password", key=f"pass_{platform_name}")

            # Update logic: if platform name changes, need to handle dict key change
            if new_platform_name != platform_name:
                platform_creds[new_platform_name] = platform_creds.pop(platform_name)
                platform_name = new_platform_name # update current platform_name for current iteration

            platform_creds[platform_name] = {
                'login_url': login_url,
                'username': username,
                'password': password
            }
            if st.button(f"Remove {platform_name}", key=f"del_{platform_name}"):
                del platform_creds[platform_name]
                st.experimental_rerun() # Rerun to reflect removal

    # Add new platform
    st.markdown("##### Add New Platform")
    new_platform_name_input = st.text_input("New Platform Name", key="new_platform_name_input")
    if st.button("Add Platform") and new_platform_name_input:
        if new_platform_name_input not in platform_creds:
            platform_creds[new_platform_name_input] = {"login_url": "", "username": "", "password": ""}
            st.experimental_rerun() # Rerun to show new platform expander
        else:
            st.warning(f"Platform '{new_platform_name_input}' already exists.")

    config["PLATFORM_CREDENTIALS"] = platform_creds


    # Other Settings
    st.markdown("#### Other Settings")
    config["DELAY_BETWEEN_APPLICATIONS_SEC"] = st.number_input(
        "Delay Between Applications (seconds)",
        min_value=0,
        value=config.get("DELAY_BETWEEN_APPLICATIONS_SEC", 30),
        help="Time to wait between processing job applications to avoid rate limiting."
    )
    config["LOG_LEVEL"] = st.selectbox(
        "Log Level",
        options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        index=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].index(config.get("LOG_LEVEL", "INFO").upper()),
        help="Set the logging verbosity for the application."
    )

    # Save Button
    st.markdown("---")
    if st.button("Save Settings"):
        save_config(config)
        # Optionally, could trigger a re-initialization of services if settings changed
        st.success("Settings saved. Some changes may require an application restart to take full effect.")

# For testing this tab independently
if __name__ == '__main__':
    st.set_page_config(layout="wide", page_title="Settings Tab Test")

    st.title("Settings Tab Test Environment")
    st.sidebar.info("This page is for testing the Settings Tab component of the Freelance Automation App.")

    display_settings()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"Configuration file will be managed at: `{CONFIG_FILE_PATH}`")

    # Display current config for debugging (optional)
    with st.sidebar.expander("Show Current Config State (Debug)"):
        st.json(load_config())

    # Instructions to test:
    # 1. Save this as settings_tab.py in your gui directory.
    # 2. Ensure a directory structure like:
    #    freelance_automation_app/
    #    ├── gui/
    #    │   └── settings_tab.py
    #    └── config.json (this file will be created/managed by the script)
    # 3. Run: streamlit run settings_tab.py
    # Changes should be saved to freelance_automation_app/config.json relative to this script's location.
