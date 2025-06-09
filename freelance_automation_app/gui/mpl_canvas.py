import streamlit as st
from matplotlib.figure import Figure
import matplotlib.pyplot as plt # Added for direct plt usage if needed

# Optional: Configure Matplotlib style for better appearance in Streamlit
plt.style.use('seaborn-v0_8-whitegrid') # Example style, can be customized

class MplCanvas:
    def __init__(self, parent_fig=None, width=5, height=4, dpi=100):
        """
        Initializes a Matplotlib Figure.
        :param parent_fig: An existing Matplotlib Figure object, if any.
        :param width: Width of the figure in inches.
        :param height: Height of the figure in inches.
        :param dpi: Dots per inch for the figure.
        """
        if parent_fig:
            self.fig = parent_fig
        else:
            self.fig = Figure(figsize=(width, height), dpi=dpi)

        # It's common to add at least one subplot by default.
        # If you expect users to always add their own, this can be removed.
        self.ax = self.fig.add_subplot(111)

    def plot_bar_chart(self, x_data, y_data, title="Bar Chart", xlabel="X-axis", ylabel="Y-axis", color='skyblue'):
        """Plots a simple bar chart on the canvas's Axes."""
        self.ax.clear() # Clear previous plots
        self.ax.bar(x_data, y_data, color=color)
        self.ax.set_title(title, fontsize=14)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.ax.tick_params(axis='x', rotation=45) # Rotate x-labels if they overlap
        self.fig.tight_layout() # Adjust layout to prevent labels from being cut off

    def plot_line_chart(self, x_data, y_data, title="Line Chart", xlabel="X-axis", ylabel="Y-axis", color='coral', marker='o'):
        """Plots a simple line chart on the canvas's Axes."""
        self.ax.clear() # Clear previous plots
        self.ax.plot(x_data, y_data, color=color, marker=marker, linestyle='-')
        self.ax.set_title(title, fontsize=14)
        self.ax.set_xlabel(xlabel, fontsize=12)
        self.ax.set_ylabel(ylabel, fontsize=12)
        self.fig.tight_layout()

    def plot_pie_chart(self, sizes, labels, title="Pie Chart", autopct='%1.1f%%', startangle=90):
        """Plots a simple pie chart on the canvas's Axes."""
        self.ax.clear() # Clear previous plots
        self.ax.pie(sizes, labels=labels, autopct=autopct, startangle=startangle, shadow=True)
        self.ax.set_title(title, fontsize=14)
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        self.fig.tight_layout()

    def get_figure(self):
        """Returns the Matplotlib Figure object."""
        return self.fig

# Example Usage within a Streamlit app context (for testing this component)
if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("MplCanvas Test in Streamlit")

    st.header("Test Bar Chart")
    # Sample data for bar chart
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    values = [10, 25, 15, 30]

    bar_canvas = MplCanvas(width=6, height=4, dpi=100)
    bar_canvas.plot_bar_chart(categories, values, title="Sample Bar Chart", xlabel="Categories", ylabel="Values")
    st.pyplot(bar_canvas.get_figure())

    st.header("Test Line Chart")
    # Sample data for line chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    sales = [100, 120, 150, 130, 170, 160]

    line_canvas = MplCanvas(width=6, height=4, dpi=100)
    line_canvas.plot_line_chart(months, sales, title="Monthly Sales Trend", xlabel="Month", ylabel="Sales ($)")
    st.pyplot(line_canvas.get_figure())

    st.header("Test Pie Chart")
    # Sample data for pie chart
    job_statuses = ['New', 'Applied', 'Interviewing', 'Archived']
    counts = [5, 15, 3, 7]

    pie_canvas = MplCanvas(width=5, height=4, dpi=100) # Pie charts often look better if closer to square
    pie_canvas.plot_pie_chart(counts, job_statuses, title="Job Application Statuses")
    st.pyplot(pie_canvas.get_figure())

    st.sidebar.info("This is a test page for MplCanvas. Run with `streamlit run mpl_canvas.py`.")

    # To run this test:
    # 1. Make sure you have streamlit and matplotlib installed:
    #    pip install streamlit matplotlib
    # 2. Save this code as mpl_canvas.py (or similar) in the gui directory.
    # 3. Navigate to the gui directory in your terminal.
    # 4. Run: streamlit run mpl_canvas.py
