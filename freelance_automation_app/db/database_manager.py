import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='freelance_jobs.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                platform TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                date_posted DATETIME,
                status TEXT DEFAULT 'New', -- e.g., New, Applied, Archived
                application_date DATETIME,
                notes TEXT,
                UNIQUE(title, platform, url)
            )
        ''')
        self.conn.commit()

    def add_job(self, title, platform, url, description=None, date_posted=None):
        try:
            if date_posted and isinstance(date_posted, str):
                date_posted = datetime.strptime(date_posted, '%Y-%m-%d %H:%M:%S')

            self.cursor.execute('''
                INSERT INTO jobs (title, platform, url, description, date_posted)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, platform, url, description, date_posted))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Job already exists: {title} on {platform}")
            return None
        except Exception as e:
            print(f"Error adding job: {e}")
            return None

    def get_job_by_url(self, url):
        self.cursor.execute("SELECT * FROM jobs WHERE url = ?", (url,))
        return self.cursor.fetchone()

    def get_all_jobs(self):
        self.cursor.execute("SELECT * FROM jobs ORDER BY date_posted DESC")
        return self.cursor.fetchall()

    def update_job_status(self, job_id, status):
        self.cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
        self.conn.commit()

    def update_job_application_date(self, job_id, application_date=None):
        if application_date is None:
            application_date = datetime.now()
        elif isinstance(application_date, str):
            application_date = datetime.strptime(application_date, '%Y-%m-%d %H:%M:%S')

        self.cursor.execute("UPDATE jobs SET application_date = ? WHERE id = ?", (application_date, job_id))
        self.conn.commit()

    def add_note_to_job(self, job_id, note):
        self.cursor.execute("UPDATE jobs SET notes = ? WHERE id = ?", (note, job_id))
        self.conn.commit()

    def search_jobs(self, keyword):
        self.cursor.execute("SELECT * FROM jobs WHERE title LIKE ? OR description LIKE ? ORDER BY date_posted DESC",
                            (f'%{keyword}%', f'%{keyword}%'))
        return self.cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == '__main__':
    # Example Usage
    db_manager = DatabaseManager(db_name='test_jobs.db')
    db_manager.connect()

    # Add a new job
    job_id = db_manager.add_job(
        title="Software Engineer",
        platform="LinkedIn",
        url="https://linkedin.com/jobs/123",
        description="Develop amazing software.",
        date_posted=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    if job_id:
        print(f"Added job with ID: {job_id}")

    # Try adding the same job again (should fail due to UNIQUE constraint)
    db_manager.add_job("Software Engineer", "LinkedIn", "https://linkedin.com/jobs/123", "Develop amazing software.")

    # Get all jobs
    all_jobs = db_manager.get_all_jobs()
    print("\nAll Jobs:")
    for job in all_jobs:
        print(job)

    # Update job status
    if all_jobs:
        db_manager.update_job_status(all_jobs[0][0], "Applied")
        db_manager.update_job_application_date(all_jobs[0][0])
        db_manager.add_note_to_job(all_jobs[0][0], "Sent application and resume.")

    # Get updated job
    updated_job = db_manager.get_job_by_url("https://linkedin.com/jobs/123")
    print("\nUpdated Job:")
    print(updated_job)

    # Search for jobs
    searched_jobs = db_manager.search_jobs("Software")
    print("\nSearched Jobs (Software):")
    for job in searched_jobs:
        print(job)

    db_manager.close()

    # Clean up the test database
    import os
    os.remove('test_jobs.db')
    print("\nCleaned up test_jobs.db")
