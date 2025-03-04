# auth.py
from dash import dcc, html,callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from flask import session
from utils.auth_handler import register_user, validate_login,reset_password
from utils.auth_middleware import login_user, is_logged_in, logout_user

# Sign Up page
def signup_page():
   return html.Div(
    children=[
        html.Div(className="auth-container", children=[
            html.Div(className="auth-left", children=[
            #  html.H3("TESTWAVE"),

                html.Img(src="static/2.jpg", className="logo"),
                html.Div(className="illustration", children=[
                    html.Img(src="static/1.jpg", className="illustration-img"),
                    html.P("Seamlessly Manage Your Test Data")
                ])
            ]),
            html.Div(className="auth-right", children=[
                html.Div(className="auth-card", children=[
                    html.H2("Sign Up for an Account"),
                    dbc.Input(id="username", type="text", placeholder="Username", className="input-field"),
                    dbc.Input(id="email", type="email", placeholder="Email", className="input-field"),
                    dbc.Input(id="password", type="password", placeholder="Password", className="input-field"),
                    
            #  dbc.Checklist(
            #                             options=[
            #                                 {"label": "By creating an account, you agree to the Terms & Conditions", "value": 1}
            #                             ],
            #                             id="terms-checkbox",
            #                             className="mb-3",
            #                             inline=True,
            #                         ),
                    
                    dbc.Button("Sign Up", id="signup-btn", className="auth-btn"),
                    
                    html.Div(id="error-msg", className="error-msg"),
                    html.Div([
                        html.P("Already have an account? ", className="login-text"),
                        dcc.Link('Log in',href="/login", className="login-link")
                    ])
                ])
            ])
        ])
    ]
    
)



# Sign In page
def signin_page():
    return html.Div(
       children=[
        html.Div(className="auth-container", children=[
            html.Div(className="auth-left", children=[
            #  html.H3("TESTWAVE"),

                html.Img(src="static/2.jpg", className="logo"),
                html.Div(className="illustration", children=[
                    html.Img(src="static/1.jpg", className="illustration-img"),
                    html.P("Seamlessly Manage Your Test Data")
                ])
            ]),
    html.Div(className="auth-right", children=[
            html.Div(className="auth-card", children=[
                html.H2("Sign In to your Account"),
                dbc.Input(id="email-signin", type="email", placeholder="Email", className="input-field"),
                dbc.Input(id="password-signin", type="password", placeholder="Password", className="input-field"),

                html.Div([
                    dcc.Link('Forgot Password?', href="/reset-password", className="forgot-password-link"),
                ], className="forgot-password-div"),

                dbc.Button("Sign In", id="signin-btn", className="auth-btn",href=""),

                html.Div(id="error-msg-signin", className="error-msg"),
                html.Div([
                    html.P("Don't have an account?", className="signup-text"),
                    dcc.Link('Sign up', href="/signup", className="signup-link")
                 ])
                ])
            ])
        ])
    ]
    
)

# Reset Password page
def reset_password_page():
    return html.Div([
        # Your layout here, unchangedchildren=[
            html.Div(className="auth-container", children=[
                html.Div(className="auth-left", children=[
                    html.Img(src="static/2.jpg", className="logo"),
                    html.Div(className="illustration", children=[
                        html.Img(src="static/1.jpg", className="illustration-img"),
                        html.P("Manage Your Test Data Seamlessly")
                    ])
                ]),
                html.Div(className="auth-right", children=[
                    html.Div(className="auth-card", children=[
                        html.H2("Reset your password"),
                        html.P("Enter the email address associated with your account"),

                        dbc.Input(id="email-reset", type="email", placeholder="Enter your email", className="input-field"),
                        dbc.Input(id="new-password", type="password", placeholder="Enter new password", className="input-field"),
                        
                        dbc.Button("Continue", id="reset-btn", className="auth-btn"),
                        
                        html.Div(id="error-msg-reset", className="error-msg"),

                        html.Div([
                            dcc.Link('Back to Sign In', href="/login", className="back-link")
                        ], className="back-to-signin")
                    ])
                ])
            ])
        ]
    )# Callbacks for Sign-Up
@callback(
    Output("error-msg", "children"),
    [Input("signup-btn", "n_clicks")],
    [State("username", "value"), State("email", "value"), State("password", "value")]
)
def handle_signup(n_clicks, username, email, password):
    if n_clicks:
        success, message = register_user(username, email, password)
        return message if success else "Error: " + message
    return ""

# Callbacks for Sign-In
@callback(
    Output("error-msg-signin", "children"),
    [Input("signin-btn", "n_clicks")],
    [State("email-signin", "value"), State("password-signin", "value")]
)
def handle_signin(n_clicks, email, password):
    if n_clicks:
        success, user_id = validate_login(email, password)
        if success:
            login_user(user_id)
            return dcc.Location(pathname="/upload", id="redirect")
        return "Invalid email or password."
    return ""

# Callbacks for Password Reset
@callback(
    Output("error-msg-reset", "children"),
    [Input("reset-btn", "n_clicks")],
    [State("email-reset", "value"), State("new-password", "value")]
)
def handle_password_reset(n_clicks, email, new_password):
    if n_clicks:
        success, message = reset_password(email, new_password)
        return message if success else "Error: " + message
    return ""

