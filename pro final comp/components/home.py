from dash import html, dcc, Input, Output, callback
import dash

# Function to create the home page layout without database content
def create_home_page():

    # Define the feature cards directly (no database query)
    feature_cards = [

            html.Div([
                html.I(className="fas fa-chart-line feature-icon"),
                html.H3("Customizable Dashboards"),
                html.P("Build dashboards tailored to your team's needs and monitor testing progress with ease.")
            ], className="feature-card"),
            html.Div([
                html.I(className="fas fa-tools feature-icon"),
                html.H3("Seamless Integration"),
                html.P("Connect with popular test tools and CI/CD pipelines effortlessly.")
            ], className="feature-card"),
            html.Div([
                html.I(className="fas fa-clock feature-icon"),
                html.H3("Real-Time Insights"),
                html.P("Stay updated on build and test statuses with instant feedback.")
            ], className="feature-card"),
            html.Div([
                html.I(className="fas fa-users feature-icon"),
                html.H3("Team Collaboration"),
                html.P("Enhance collaboration with centralized reporting and trend analysis.")
            ], className="feature-card"),
        ]

    

    return html.Div([

        # Tracks the URL changes
        dcc.Location(id='url', refresh=True),

        # Navbar section
        html.Div([
            html.A("Home", href="#", className="nav-link"),
            html.A("Contact", href="/contact-us", className="nav-link"),
            html.A("About Us", href="/about-us", className="nav-link"),
            html.Div([
                html.A("Sign In / Sign Up", className="dropdown-toggle", id='dropdown-toggle'),
                html.Div(id='dropdown-menu', className="dropdown-menu", children=[
                    html.A("Sign In", href="/login", className="dropdown-item", id="signin-link"),
                    html.A("Sign Up", href="/signup", className="dropdown-item", id="signup-link"),
                ])
            ], className="dropdown")
        ], className="navbar"),

        # Hero section
        html.Div([
            html.H1("Welcome to Testwave", className="hero-title"),
            html.P("Streamline Your Testing Lifecycle with Testwave", className="hero-tagline"),
            html.A("Get Started", href="#", className="hero-button")
        ], className="hero-section"),

        # Features section
        html.Div([
            html.H2("Why Choose Testwave?", className="features-title"),
            html.Div(feature_cards, className="features-grid")
        ], className="features-section"),

        # Call to Action (CTA) section
        html.Div([
            html.H2("Join Testwave Today!", className="cta-title"),
            html.P("Ready to take your testing process to the next level?", className="cta-text"),
            html.A("Sign Up Now", href="/signup", className="cta-button")
        ], className="cta-section"),

        # Footer section
        html.Div([
            html.P("© 2024 Testwave. All Rights Reserved.", className="footer-text"),
            html.Div([
                html.A(href="#", className="fab fa-facebook-f social-link"),
                html.A(href="#", className="fab fa-twitter social-link"),
                html.A(href="#", className="fab fa-linkedin-in social-link")
            ], className="footer-social")
        ], className="footer")
    ])

# Callback to handle dropdown menu visibility
@callback(
    Output('dropdown-menu', 'style'),
    Input('dropdown-toggle', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_dropdown(n_clicks):
    if n_clicks:
        return {'display': 'block'} if n_clicks % 2 == 1 else {'display': 'none'}
    return {'display': 'none'}
