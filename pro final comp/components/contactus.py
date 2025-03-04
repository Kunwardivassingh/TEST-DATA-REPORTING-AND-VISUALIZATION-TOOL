import dash 
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import mysql.connector
from dash.dependencies import Input, Output
from dash import html,callback

# MySQL database configuration
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  # Change to your MySQL host
        user="root",       # Your MySQL username
        password="",  # Your MySQL password
        database="testwave"  # Database name
    )
    return conn

# Function to create the contact_us table if it doesn't exist
def create_contact_us_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_us (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Function to insert form data into the database
def save_contact_form_data(name, email, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contact_us (name, email, message)
        VALUES (%s, %s, %s)
    """, (name, email, message))
    conn.commit()
    conn.close()

# Contact Us page layout function with card style
def create_contact_us_layout():
    return html.Div(
        children=[
            dbc.Container(
                children=[
                    html.Div(
                        className="header",
                        children=[
                            html.H1("Contact Us", className="my-4"),
                            html.P("We'd love to hear from you! Please fill out the form below, and we'll get back to you as soon as possible."),
                        ]
                    ),
                    
                    # Card layout for the form
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Label("Full Name", html_for="name", className="form-label"),
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Input(type="text", id="name", placeholder="Enter your full name", required=True, className="form-input"),
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Label("Email Address", html_for="email", className="form-label"),
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Input(type="email", id="email", placeholder="Enter your email address", required=True, className="form-input"),
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Label("Message", html_for="message", className="form-label"),
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Textarea(id="message", placeholder="Enter your message", rows=4, required=True, className="form-textarea"),
                                            )
                                        ),
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Button("Submit", color="primary", id="submit-button", style={"width": "100%"}, className="submit-button"),
                                            )
                                        ),
                                    ]
                                ),
                                className="contact-form-card"
                            ),
                            width={"size": 6, "offset": 3},
                        ),
                    ),
                    html.Div(id="confirmation-message", className="mt-4", style={"color": "green"}),
                ],
                fluid=True
            )
        ]
    )

# Callback to handle form submission
@callback(
    Output("confirmation-message", "children"),
    Input("submit-button", "n_clicks"),
    [Input("name", "value"), Input("email", "value"), Input("message", "value")],
    prevent_initial_call=True
)
def handle_form_submission(n_clicks, name, email, message):
    if n_clicks is not None:
        if name and email and message:
            # Create the table if it doesn't exist
            create_contact_us_table()

            # Save the contact form data
            save_contact_form_data(name, email, message)

            return "Thank you for your message! We will get back to you shortly."
        else:
            return "Please fill out all fields."

