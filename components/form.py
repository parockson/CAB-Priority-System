from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import date

def render_form():
    # Mapping actual names to internal keys for the importance axis[cite: 1]
    importance_map = [
        ("financial_integrity", "Financial Integrity"),
        ("service_criticality", "Service Criticality"),
        ("blast_radius", "Blast Radius"),
        ("regulatory_weight", "Regulatory Weight"),
        ("strategic_priority", "Strategic Priority")
    ]
    
    # Mapping actual names for the urgency axis (excluding automated deadline)[cite: 1]
    urgency_map = [
        ("security_pressure", "Security Pressure"),
        ("contractual_clock", "Contractual Clock (SLA)"),
        ("system_health", "System Health"),
        ("implementation_risk", "Implementation Risk")
    ]

    form_layout = [
        html.H4("New Change Request", style={'color': '#ED1944'}),
        dbc.Input(id="cr-title", placeholder="CR Title", className="mb-2"),
        html.Label("Target Completion Date"),
        dcc.DatePickerSingle(id="target-date", date=date.today(), className="mb-3 w-100"),
        
        html.Hr(),
        html.H6("Importance Factors (Y-Axis)"),
        *[html.Div([
            html.Label(name),
            dcc.Slider(0, 100, id=key, value=50, marks={0:'0', 100:'100'})
        ], className="mb-3") for key, name in importance_map],
        
        html.Hr(),
        html.H6("Urgency Factors (X-Axis)"),
        *[html.Div([
            html.Label(name),
            dcc.Slider(0, 100, id=key, value=50, marks={0:'0', 100:'100'})
        ], className="mb-3") for key, name in urgency_map],
        
        dbc.Button("Submit to CAB", id="submit-btn", className="btn-primary w-100 mt-3", style={'backgroundColor': '#ED1944'})
    ]
    
    return html.Div(form_layout, className="card p-3")