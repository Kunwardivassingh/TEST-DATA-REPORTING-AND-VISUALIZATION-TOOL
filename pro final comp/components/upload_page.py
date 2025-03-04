import base64
import io
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from flask import session
import pandas as pd
from utils.auth_handler import save_dataset_to_db
from utils.db import get_db_connection



import dash_bootstrap_components as dbc
from dash import dcc, html

# Fetch username from the database
def fetch_username(user_id):
    if user_id is None:
        return "Guest"
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else "Guest"
    except Exception as e:
        print(f"Error fetching username: {e}")
        return "Guest"
    finally:
        cursor.close()
        conn.close()

def sidebarr():
    user_id = session.get('user_id')
    username = fetch_username(user_id) if user_id else "Guest"
    return html.Div(className="sidebar", children=[
        html.Img(src="/static/2.jpg", className="logo"),
        html.H4("MENU"),
        dbc.Nav(
            [
                # dbc.NavLink("Upload Data", href="/upload", className="nav-item"),
                dbc.NavLink("Dashboard", href="/dashboard", className="nav-item"),
                html.Hr(),
                # html.P("Filter Options", className="sidebar-label"),
                # dcc.Dropdown(id="filter-product", placeholder="Filter by Product", multi=True),
                # dcc.Dropdown(id="filter-test-type", placeholder="Filter by Test Type", multi=True),
                # dcc.Dropdown(
                #     id="filter-frequency",
                #     options=[
                #         {'label': 'Daily', 'value': 'Daily'},
                #         {'label': 'Weekly', 'value': 'Weekly'},
                #         {'label': 'Monthly', 'value': 'Monthly'}
                #     ],
                #     placeholder="Filter by Frequency"
                # )
            ],
            vertical=True,
            pills=True
            
        ),
          html.Div(className="user-info", children=[
                html.P(f"User: {username}", className="username"),
                dbc.Button("Log out", id="logout-btn", href="/logout", className="logout-btn")
            ])

    ])

# Upload Page Layout with filter-section initially hidden
def upload_page():
    return html.Div(
        className="main-content", children=[
            html.H2("Upload Dataset"),
            html.Div(
                className="upload-section", children=[
                    html.H3("Drag and Drop your dataset here"),
                    html.Div(dcc.Upload(
                        id='upload-data',
                        children=html.Button("Select File", className="upload-btn"),
                        multiple=False
                    )),
                    html.Div(id='upload-status'),  # Upload status message
                ]
            ),
            # Filter section added here, initially hidden until file upload is successful
    #         html.Div(
    #             id='filter-section', 
    #             className="filter-options", 
    #             style={'display': 'none'},  # Hidden until a file is uploaded
    #             children=[
    #                 html.H3("Filter Options"),
    #                 dcc.Dropdown(id="filter-product", placeholder="Filter by Product", multi=True),
    #                 dcc.Dropdown(id="filter-test-type", placeholder="Filter by Test Type", multi=True),
    #                 dcc.RadioItems(
    #                     id="filter-frequency",
    #                     options=[
    #                         {'label': 'Daily', 'value': 'Daily'},
    #                         {'label': 'Weekly', 'value': 'Weekly'},
    #                         {'label': 'Monthly', 'value': 'Monthly'}
    #                     ],
    #                     labelStyle={'display': 'block'}
    #                 )
    #             ]
    #         )
        ]
    )

# Callback for handling file upload, saving to database, and showing filter options
@callback(
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def upload_file(contents, filename):
    if not contents:
        return "Please upload a file."
    
    try:
        # Decode the uploaded file content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Get file extension
        file_extension = filename.lower().split('.')[-1]
        
        try:
            # Read different file formats into DataFrame
            if file_extension == 'csv':
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(io.BytesIO(decoded))
            elif file_extension == 'json':
                df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
            elif file_extension == 'parquet':
                df = pd.read_parquet(io.BytesIO(decoded))                                                                                                               
            else:
                return f"Unsupported file format: .{file_extension}. Please upload CSV, Excel, JSON, or Parquet files."

            # Validate DataFrame
            if df.empty:
                return "The uploaded file is empty. Please check the file content."
            
            # Clean the DataFrame
            # Remove completely empty columns
            df = df.dropna(axis=1, how='all')
            # Remove completely empty rows
            df = df.dropna(axis=0, how='all')
            
            # Convert numeric strings to actual numbers where possible
            # for column in df.columns:
            #     try:
            #         # df[column] = pd.to_numeric(df[column], errors='ignore')           
            #         df[column] = pd.to_datetime(df[column], errors='coerce')
            #     except:
            #         continue
            
            # Save to database
            success, message = save_dataset_to_db(df)
            
            if success:
                return html.Div([
                    html.P(message, style={'color': 'green'}),
                    html.P(f"Number of columns: {len(df.columns)}"),
                    html.P(f"Number of rows: {len(df)}")
                ])
            else:
                return html.Div(message, style={'color': 'red'})

        except pd.errors.EmptyDataError:
            return "The file is empty. Please check the file content."
        except pd.errors.ParserError:
            return "Error parsing the file. Please check if the file format is correct."
        
    except Exception as e:
        return f"Error processing file: {str(e)}"
