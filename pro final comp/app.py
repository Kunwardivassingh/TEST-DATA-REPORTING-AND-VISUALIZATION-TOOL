import os
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd  # For handling Excel files
import base64
import io
import mysql.connector  # For MySQL connection
# from components.sidebar import side
from components.aboutus import create_about_us_layout
from components.contactus import create_contact_us_layout

from components.home import create_home_page
from utils.auth_handler import register_user, validate_login, save_dataset_to_db, fetch_dataset_from_db

# Import components
from components.auth import signup_page, signin_page, reset_password_page
from components.upload_page import upload_page,sidebarr
from components.dashboard import dashboard_page,sidebar


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.server.secret_key = os.urandom(24)  # or set your own static secret key for consistency

# MySQL Connection Setup
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'testwave_db'
}

def create_db_connection():
    return mysql.connector.connect(**db_config)

# Define initial layout with Location for routing
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # For dynamic routing
    html.Div(id="page-content")  # Will contain the page content
])
app.clientside_callback(
    """
    function(n_clicks) {
        // Ensure n_clicks is a valid number and trigger print only if n_clicks is greater than 0
        if (typeof n_clicks === 'number' && n_clicks > 0) {
            window.print();  // Open the print dialog for the entire dashboard page
            return 0;  // Reset n_clicks to 0 after printing
        }
        return n_clicks;  // Return the current n_clicks value for no action
    }
    """,
    Output("print-btn", "n_clicks"),  # Reset button clicks after action
    Input("print-btn", "n_clicks")
)
# Routing Callback
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/login":
        return signin_page()
    elif pathname == "/signup":
        return signup_page()
    elif pathname == "/reset-password":
        return reset_password_page()
    elif pathname == "/upload":
        return html.Div([sidebarr(), upload_page()])
    elif pathname == "/dashboard":
        return html.Div([sidebar(), dashboard_page()])
    elif pathname == "/contact-us":
        return create_contact_us_layout() # Render the contact us layout
    elif pathname == "/about-us":
        return create_about_us_layout()
    else:
        return create_home_page()




if __name__ == '__main__':
    app.run_server(debug=True)
