import streamlit as st
import sys
import os

# Adjust Python path to include the root directory of the app
# This allows Streamlit to find modules in `core` and `db` when `main_window.py` is run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import modules from `gui`, `db`, and `core`
try:
    from .dashboard_tab import display_dashboard
    from .settings_tab import display_settings, load_config, save_config # Added save_config
    from ..db.database_manager import DatabaseManager # Corrected: from ..db import ...
    from ..core.automation_worker import AutomationWorker # Corrected: from ..core import ...
    # Import other necessary components like log_viewer_tab if it exists
except ImportError as e:
    st.error(f"Error importing modules: {e}. Make sure all components are in their respective directories (gui, db, core) and sys.path is correct.")
    st.error(f"Current sys.path: {sys.path}")
    # If running from within `gui` directory, `..db` and `..core` should work.
    # If running from root `freelance_automation_app`, then `from gui...`, `from db...`, `from core...`
    # The sys.path.append above should handle the case of running `streamlit run gui/main_window.py`
    st.stop()


# Initialize DatabaseManager
# Use the database name from config, falling back to a default if not found
config = load_config() # Load config first
db_manager = DatabaseManager(db_name=config.get('DATABASE_NAME', 'freelance_jobs.db'))
db_manager.connect() # Ensure tables are created

# Initialize AutomationWorker
# The worker will also load its config internally or could be passed `config`
try:
    automation_worker = AutomationWorker(config=config)
except Exception as e:
    st.error(f"Failed to initialize AutomationWorker: {e}")
    automation_worker = None # Set to None if initialization fails

def main_app_window():
    st.set_page_config(page_title="Freelance Automation Hub", layout="wide")
    st.title("Freelance Automation Hub")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose a section:",
                                    ["Dashboard", "Manage Jobs", "Run Automation", "Settings", "Logs"])

    # Main content area based on selection
    if app_mode == "Dashboard":
        display_dashboard(db_manager) # Pass the db_manager instance

    elif app_mode == "Manage Jobs":
        st.subheader("Manage Job Entries")
        # TODO: Implement job management UI (add, edit, delete jobs from DB)
        # This would involve forms and interacting with db_manager methods
        st.info("Job management UI (add, edit, view details) is under construction.")

        # Basic display of all jobs for now
        all_jobs = db_manager.get_all_jobs()
        if all_jobs:
            # Define columns based on your database schema
            columns = ['id', 'title', 'platform', 'url', 'description', 'date_posted', 'status', 'application_date', 'notes']
            import pandas as pd
            jobs_df = pd.DataFrame(all_jobs, columns=columns)
            st.dataframe(jobs_df, use_container_width=True)
        else:
            st.write("No jobs found in the database.")

    elif app_mode == "Run Automation":
        st.subheader("Automation Control Panel")
        if automation_worker:
            if st.button("Start Job Fetching & Application Process"):
                with st.spinner("Automation worker is running... This may take some time."):
                    try:
                        # Make sure db is connected before worker runs
                        db_manager.connect() # Worker might also connect, ensure it's idempotent or handled.
                        automation_worker.find_and_apply_for_jobs()
                        st.success("Automation cycle completed!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"An error occurred during automation: {e}")
                    finally:
                        db_manager.close() # Ensure DB connection is closed after operation
            st.caption("Click the button above to start the automated process of fetching new jobs, generating proposals, and (if configured) applying to them.")
        else:
            st.error("Automation Worker is not available. Check configuration and error messages.")

    elif app_mode == "Settings":
        display_settings() # Manages its own config loading/saving

    elif app_mode == "Logs":
        st.subheader("Application Logs")
        # TODO: Implement a log viewer tab (e.g., display logs from a file or in-memory)
        # For now, a placeholder. Could use a custom LogHandler that writes to a Streamlit widget.
        st.info("Log viewing functionality is under construction.")
        # Example: display content of a log file if you have one
        # log_file_path = os.path.join(os.path.dirname(__file__), '..', 'app.log')
        # if os.path.exists(log_file_path):
        #     try:
        #         with open(log_file_path, 'r') as f:
        #             st.text_area("Log Content", f.read(), height=300)
        #     except Exception as e:
        #         st.error(f"Could not read log file: {e}")
        # else:
        #     st.write("Log file not found.")


    # Footer or sidebar bottom note
    st.sidebar.markdown("---")
    st.sidebar.info("Freelance Automation App v0.1")

if __name__ == '__main__':
    # This allows running the app by executing: streamlit run freelance_automation_app/gui/main_window.py
    # from the project root directory.
    main_app_window()

    # Ensure DB connection is closed when Streamlit app shuts down (if not managed elsewhere)
    # This is tricky with Streamlit's execution model. db_manager.close() here might not always run.
    # Better to manage connections within specific operations (e.g., in display_dashboard, find_and_apply_for_jobs)
    # or use context managers if db_manager supports it.
    # For simplicity, we'll rely on operations to manage their connections.
    # If db_manager.connect() is called multiple times, it should handle existing connections gracefully.
