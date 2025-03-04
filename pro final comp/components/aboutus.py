import dash_html_components as html

def create_about_us_layout():
    return html.Div(
        className="about-container",
        children=[
            html.Div(
                className="about-header",
                children=[
                    html.H1("About Us"),
                    html.P("Testwave is a powerful tool designed to streamline the reporting and visualization of test execution data."),
                ]
            ),
            html.Div(
                className="about-content",
                children=[
                    html.P("We aim to improve collaboration, identify trends, and enhance visibility in the testing lifecycle."),
                    html.P("With customizable dashboards, teams can monitor testing progress and make informed decisions."),
                    html.P("Join us today and elevate your testing processes with Testwave."),
                ]
            ),
            html.Div(
                className="about-footer",
                children="© 2024 Testwave. All rights reserved."
            ),
        ]
    )
