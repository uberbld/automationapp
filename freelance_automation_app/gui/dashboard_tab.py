import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from .mpl_canvas import MplCanvas # Assuming MplCanvas is in the same directory
from ..db.database_manager import DatabaseManager # Adjusted relative import

def display_dashboard(db_manager):
    st.subheader("Job Application Dashboard")

    # Fetch all jobs data
    all_jobs_tuples = db_manager.get_all_jobs()
    if not all_jobs_tuples:
        st.info("No job data available yet to display on the dashboard.")
        return

    # Convert list of tuples to DataFrame for easier analysis
    # Get column names from cursor description
    # This needs to be done carefully. If db_manager is already closed or cursor is not available, this will fail.
    # It's safer if DatabaseManager.get_all_jobs() returns a list of dicts or a DataFrame directly.
    # For now, let's assume we can get column names after fetching.
    # This is a common pattern but requires the db_manager to keep the cursor available or provide column names.

    # A robust way: If db_manager.get_all_jobs() was just executed, cursor description should be available
    # However, if connect/close is managed per call, this might not work.
    # Let's define column names explicitly based on database_manager.py schema for reliability here.
    columns = ['id', 'title', 'platform', 'url', 'description',
               'date_posted', 'status', 'application_date', 'notes']
    jobs_df = pd.DataFrame(all_jobs_tuples, columns=columns)

    # Data type conversions (especially for dates)
    jobs_df['date_posted'] = pd.to_datetime(jobs_df['date_posted'], errors='coerce')
    jobs_df['application_date'] = pd.to_datetime(jobs_df['application_date'], errors='coerce')

    # Key Metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    total_jobs = len(jobs_df)
    col1.metric("Total Jobs Tracked", total_jobs)

    jobs_applied = jobs_df[jobs_df['status'] == 'Applied'].shape[0]
    col2.metric("Jobs Applied", jobs_applied)

    jobs_new = jobs_df[jobs_df['status'] == 'New'].shape[0]
    col3.metric("New Opportunities", jobs_new)

    # Example: Jobs applied in the last 7 days
    last_week = datetime.now() - timedelta(days=7)
    applied_last_week = jobs_df[
        (jobs_df['application_date'] >= last_week) & (jobs_df['status'] == 'Applied')
    ].shape[0]
    col4.metric("Applied (Last 7 Days)", applied_last_week)

    st.markdown("---")

    # Visualizations
    st.markdown("### Visualizations")

    # Visualization 1: Job Status Distribution (Pie Chart)
    status_counts = jobs_df['status'].value_counts()
    if not status_counts.empty:
        st.markdown("#### Job Status Distribution")
        pie_canvas = MplCanvas(width=5, height=4)
        pie_canvas.plot_pie_chart(status_counts.values, status_counts.index, title="Job Statuses")
        st.pyplot(pie_canvas.get_figure())
    else:
        st.info("No status data to display for pie chart.")

    # Visualization 2: Jobs Posted Over Time (Line Chart)
    # Ensure 'date_posted' is not NaT before resampling
    jobs_df_time = jobs_df.dropna(subset=['date_posted']).copy()
    if not jobs_df_time.empty:
        jobs_df_time.set_index('date_posted', inplace=True)
        # Resample by week or month for a cleaner look, e.g., weekly: 'W-Mon'
        postings_over_time = jobs_df_time.resample('W-Mon').size()
        if not postings_over_time.empty:
            st.markdown("#### Job Postings Over Time (Weekly)")
            line_canvas = MplCanvas(width=7, height=4)
            line_canvas.plot_line_chart(
                x_data=postings_over_time.index.strftime('%Y-%m-%d'), # Format dates for better display
                y_data=postings_over_time.values,
                title="Weekly Job Postings",
                xlabel="Week",
                ylabel="Number of Jobs Posted"
            )
            st.pyplot(line_canvas.get_figure())
        else:
            st.info("Not enough posting date data to display trend chart.")
    else:
        st.info("No valid posting date data to display trend chart.")


    # Visualization 3: Jobs by Platform (Bar Chart)
    platform_counts = jobs_df['platform'].value_counts()
    if not platform_counts.empty:
        st.markdown("#### Jobs by Platform")
        bar_canvas = MplCanvas(width=7, height=4)
        bar_canvas.plot_bar_chart(
            x_data=platform_counts.index,
            y_data=platform_counts.values,
            title="Job Sources by Platform",
            xlabel="Platform",
            ylabel="Number of Jobs"
        )
        st.pyplot(bar_canvas.get_figure())
    else:
        st.info("No platform data to display for bar chart.")

    st.markdown("---")

    # Recent Activity (Optional - display last 5 applied jobs or new jobs)
    st.markdown("### Recent Job Postings (Top 5)")
    recent_jobs_df = jobs_df.sort_values(by='date_posted', ascending=False).head(5)
    if not recent_jobs_df.empty:
        st.dataframe(recent_jobs_df[['title', 'platform', 'date_posted', 'status']], use_container_width=True)
    else:
        st.info("No recent jobs to display.")

# Example of how to run this tab (usually part of a larger Streamlit app)
if __name__ == '__main__':
    # This setup is for testing this specific tab file.
    # In the main app, db_manager would be initialized and passed.
    st.set_page_config(layout="centered", page_title="Dashboard Tab Test")

    # --- Database Setup for Test ---
    # Create an in-memory SQLite DB for testing or use a test file
    TEST_DB_NAME = 'test_dashboard_jobs.db'
    db_manager_test = DatabaseManager(db_name=TEST_DB_NAME)
    db_manager_test.connect() # Creates tables if they don't exist

    # Add some dummy data for testing the dashboard
    def add_dummy_data_if_empty(db_m):
        if not db_m.get_all_jobs(): # Only add if DB is empty
            dummy_data = [
                ("Software Engineer", "LinkedIn", "http://linkedin.com/job/1", "Python, SQL", (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), "Applied", (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), "Applied via referral."),
                ("Data Analyst", "Indeed", "http://indeed.com/job/2", "Excel, Tableau", (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), "New", None, None),
                ("Project Manager", "LinkedIn", "http://linkedin.com/job/3", "Agile, Scrum", (datetime.now() - timedelta(days=12)).strftime('%Y-%m-%d %H:%M:%S'), "Archived", (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), "Not a good fit."),
                ("UX Designer", "Company Careers", "http://company.com/job/4", "Figma, Adobe XD", (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), "New", None, None),
                ("Software Engineer", "LinkedIn", "http://linkedin.com/job/5", "Java, Spring", (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "New", None, None),
                ("Data Scientist", "AngelList", "http://angel.co/job/6", "Python, ML", (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'), "Applied", (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'), "Followed up."),
            ]
            for job_details in dummy_data:
                db_m.add_job(*job_details[:-2]) # Add job details
                # Update status, application_date, notes if they exist in dummy data
                job_entry = db_m.get_job_by_url(job_details[2])
                if job_entry:
                    job_id = job_entry[0] # Assuming ID is the first column
                    db_m.update_job_status(job_id, job_details[5])
                    if job_details[6]: # If application_date is not None
                         db_m.update_job_application_date(job_id, job_details[6])
                    if job_details[7]: # If notes is not None
                        db_m.add_note_to_job(job_id, job_details[7])
            print("Dummy data added to test_dashboard_jobs.db")
        else:
            print("Database already contains data. Skipping dummy data addition.")

    add_dummy_data_if_empty(db_manager_test)
    # --- End Database Setup for Test ---

    # Display the dashboard tab content
    display_dashboard(db_manager_test)

    # --- Cleanup for Test ---
    # db_manager_test.close() # Close connection
    # Optional: remove the test DB file after script runs
    # import os
    # if os.path.exists(TEST_DB_NAME):
    #     os.remove(TEST_DB_NAME)
    #     print(f"Cleaned up test database: {TEST_DB_NAME}")
    # --- End Cleanup for Test ---

    st.sidebar.info("This is a test run of the Dashboard Tab.")
    st.sidebar.warning("Make sure `database_manager.py` and `mpl_canvas.py` are accessible (e.g., in correct relative paths).")
