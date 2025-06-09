import streamlit.web.cli as stcli
import os
import sys

def run_streamlit_app():
    """
    Runs the Streamlit application located in the gui/main_window.py file.
    """
    # Get the absolute path to the directory containing this script (main.py)
    # This should be the root of your freelance_automation_app project.
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the main_window.py Streamlit script
    streamlit_app_path = os.path.join(project_root, "gui", "main_window.py")

    # Check if the Streamlit app file exists
    if not os.path.exists(streamlit_app_path):
        print(f"Error: Streamlit app file not found at {streamlit_app_path}")
        print("Please ensure main_window.py is in the gui directory.")
        sys.exit(1)

    # Add project root to sys.path to allow main_window.py to import modules
    # from core, db, etc., using relative paths like `from ..db import ...`
    # This is crucial because Streamlit runs the script as if it's the top-level script,
    # and its default working directory behavior might not align with package structure.
    sys.path.insert(0, project_root)

    print(f"Project root added to sys.path: {project_root}")
    print(f"Attempting to run Streamlit app: {streamlit_app_path}")
    print(f"Current sys.path: {sys.path}")

    # Prepare arguments for Streamlit CLI
    # Equivalent to running: streamlit run gui/main_window.py
    args = [streamlit_app_path]

    # Execute Streamlit
    # Note: stcli.main() expects sys.argv to be set up as if run from command line.
    # We can simulate this.
    original_argv = sys.argv
    sys.argv = ["streamlit", "run"] + args

    try:
        stcli.main()
    except SystemExit as e:
        # Handle potential SystemExit from Streamlit (e.g., if server fails to start)
        # SystemExit(0) is normal for Streamlit when it exits cleanly.
        if e.code != 0:
            print(f"Streamlit exited with error code: {e.code}")
            sys.exit(e.code)
    except Exception as e:
        print(f"An unexpected error occurred while trying to run Streamlit: {e}")
        sys.exit(1)
    finally:
        sys.argv = original_argv # Restore original sys.argv

if __name__ == "__main__":
    run_streamlit_app()
