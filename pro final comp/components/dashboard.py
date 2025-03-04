import io
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from flask import render_template, send_file, session
import pdfkit
import plotly.express as px
import pandas as pd
from utils.db import create_engine, get_db_connection  # Ensure this function returns a SQLAlchemy engine for MySQL

# Fetch username from the database
def fetch_username(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else "Guest"

# Function to fetch unique values for filters from the database
def fetch_unique_values():
    conn = get_db_connection()
    products_query = "SELECT DISTINCT product FROM datasets"
    test_types_query = "SELECT DISTINCT test_type FROM datasets"
    frequencies_query = "SELECT DISTINCT frequency FROM datasets"
    owners_query = "SELECT DISTINCT owner FROM datasets"

    products = pd.read_sql(products_query, conn)['product'].tolist()
    test_types = pd.read_sql(test_types_query, conn)['test_type'].tolist()
    frequencies = pd.read_sql(frequencies_query, conn)['frequency'].tolist()
    owners = pd.read_sql(owners_query, conn)['owner'].tolist()

    conn.close()
    return products, test_types, frequencies, owners 

# Sidebar with filter options for product, test type, and frequency
def sidebar():
    user_id = session.get('user_id')
    username = fetch_username(user_id) if user_id else "Guest"

    # Fetch unique values for filter options
    products, test_types, frequencies, owners = fetch_unique_values()

    return html.Div(className="sidebar", children=[
        html.Img(src="/static/2.jpg", className="logo"),
        html.H4("MENU", className="sidebar-title"),
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/dashboard", className="nav-item"),
                html.Hr(),
                html.P("Filter Options", className="sidebar-label"),
                dcc.Dropdown(id="product-filter",
                             options=[{'label': product, 'value': product} for product in products if product],
                             placeholder="Filter by Product", multi=True),
                dcc.Dropdown(id="test-type-filter", 
                             options=[{'label': test_type, 'value': test_type} for test_type in test_types if test_type],
                             placeholder="Filter by Test Type", multi=True),
                dcc.Dropdown(
                    id="frequency-filter",
                    options=[{'label': frequency, 'value': frequency} for frequency in frequencies if frequency],
                    placeholder="Select Frequency"
                ),
                dcc.Dropdown(
                    id="owner-filter",
                    options=[{'label': owner, 'value': owner} for owner in owners if owner],
                    placeholder="Select owner", multi=True
                ),
            ],
            vertical=True,
            pills=True
        ),
        html.Div(className="user-info", children=[
            html.P(f":User   {username}", className="username"),
            dbc.Button("Log out", id="logout-btn", href="/logout", className="logout-btn")
        ])
    ])

# Main dashboard layout with sidebar, KPIs, and charts
def dashboard_page():
    return html.Div([
        html.Div(className="sidebar-container", children=[sidebar()]),
        html.Div(className="main-content", children=[
            html.H2("Dashboard"),
            # Horizontal KPI stats bar
            html.Div(className="stats-bar", style={"display": "flex", "justify-content": "space-around"}, children=[
                html.Div("Total Tests", id="total-tests", className="stat-card1"),
                html.Div("Total Pass", id="total-pass", className="stat-card2"),
                html.Div("Total Fail", id="total-fail", className="stat-card3"),
                html.Div("Total NE", id="total-ne", className="stat-card4")
            ]),
            html.Hr(),
            html.Br(),
            # Graphs with analytical descriptions
            dcc.Graph(id="bar-graph"),
            #html.Div("This bar graph displays the product-wise test statuses. It allows for quick comparison of how each product is performing in terms of test results. A higher number of 'PASS' statuses indicates better product quality, while a significant number of 'FAIL' statuses may highlight areas needing improvement or further investigation.", className="graph-description"),
            html.Br(),
            dcc.Graph(id="pie-chart"),
            #html.Div("The pie chart illustrates the overall distribution of test statuses across all tests. A large slice representing 'PASS' indicates a successful testing phase, while a substantial 'FAIL' slice may suggest systemic issues that need addressing. This visualization helps stakeholders quickly assess the overall health of the testing process.", className="graph-description"),
            html.Br(),
            dcc.Graph(id="scatter-plot"),
            #html.Div("This scatter plot visualizes the relationship between execution dates and test frequencies, with points colored by their status. It can reveal trends over time, such as whether tests executed on specific dates tend to have better or worse outcomes. Identifying patterns in execution can help optimize testing schedules and resource allocation.", className="graph-description"),
            html.Br(),
            dcc.Graph(id="histogram"),
            #html.Div("The histogram shows the distribution of test types, colored by their status. This visualization helps identify which test types are more likely to pass or fail. A concentration of failures in specific test types may indicate the need for further investigation or refinement of those tests.", className="graph-description"),
            html.Br(),
            dcc.Graph(id="box-plot"),
            #html.Div("The box plot illustrates the distribution of test statuses, highlighting the spread and central tendency of the data. It can help identify outliers in test results, such as unusually high failure rates for certain products or test types. Understanding these outliers is crucial for quality assurance and improving testing processes.", className="graph-description"),
            html.Br(), # Add this at the end of the "main-content" children list in the `dashboard_page` function
            dbc.Button("Print as PDF", id="print-btn", n_clicks=0)
        ])
    ])

# Function to fetch filtered data from the database
def fetch_filtered_data(product=None 
, test_type=None, frequency=None, owner=None):
    conn = get_db_connection()
    query = "SELECT * FROM datasets WHERE 1=1"
    params = []
    
    if product:
        query += " AND product IN ({})".format(','.join(['%s'] * len(product)))
        params.extend(product)
    if test_type:
        query += " AND test_type IN ({})".format(','.join(['%s'] * len(test_type)))
        params.extend(test_type)
    if frequency:
        query += " AND frequency = %s"
        params.append(frequency)
    if owner:
        query += " AND owner IN ({})".format(','.join(['%s'] * len(owner)))
        params.extend(owner)

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Callback to update the dashboard charts and KPIs
@callback(
    [
        Output("bar-graph", "figure"),
        Output("pie-chart", "figure"),
        Output("scatter-plot", "figure"),
        Output("histogram", "figure"),  # Output for Histogram
        Output("box-plot", "figure"),    # Output for Box Plot
        Output("total-tests", "children"),
        Output("total-pass", "children"),
        Output("total-fail", "children"),
        Output("total-ne", "children")
    ],
    [
        Input("product-filter", "value"),
        Input("test-type-filter", "value"),
        Input("frequency-filter", "value"),
        Input("owner-filter", "value")
    ],
)
def update_dashboard(product_filter, test_type_filter, frequency_filter, owner_filter):
    # Fetch and filter the data based on selections
    df = fetch_filtered_data(product=product_filter, test_type=test_type_filter, frequency=frequency_filter, owner=owner_filter)

    # KPI calculations
    total_tests = len(df)
    total_pass = len(df[df['status'] == 'Pass'])
    total_fail = len(df[df['status'] == 'Fail'])
    total_ne = len(df[df['status'] == 'Not Executed'])

    # Create updated figures
    bar_fig = px.bar(df, x='product', color='status', title="Product-wise Test Statuses")
    pie_fig = px.pie(df, names='status', title='Test Status Distribution')
    scatter_plot = px.scatter(df, x='execution_date', y='frequency', color='status', title="Execution Date vs Frequency")
    # Histogram for test duration (assuming there's a 'duration' column in your dataframe)
    histogram_fig = px.histogram(df, x='test_type', color='status', title='Distribution of Test-type ')
    
    # Box plot for test results by product (assuming 'result' is a numeric column)
    box_plot_fig = px.box(df, x='status', color='status', title='Test_status distribution by box plot')

    # Return updated figures and KPI values
    return (
        bar_fig,
        pie_fig,
        scatter_plot,
        histogram_fig,
        box_plot_fig,
        f"Total Tests: {total_tests}",
        f"Total Pass: {total_pass}",
        f"Total Fail: {total_fail}",
        f"Total NE: {total_ne}"
    )