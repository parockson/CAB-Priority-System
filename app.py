import dash
from dash import html, dcc, Output, Input, State, dash_table, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
from logic.scoring import calculate_coordinates
from logic.supabase_client import supabase

# 1. Initialization
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    suppress_callback_exceptions=True 
)
server = app.server

ARCHIVE_STYLE = {'backgroundColor': '#333', 'color': 'white', 'fontWeight': 'bold'}
STATUS_OPTIONS = ["CR-raised", "In dev", "UAT", "Sign off", "Live", "Monitoring", "Suspended"]

# 2. Component: Form inside a Modal
def render_request_modal():
    factors = [
        ("financial_integrity", "Financial Integrity"), ("service_criticality", "Service Criticality"),
        ("blast_radius", "Blast Radius"), ("regulatory_weight", "Regulatory Weight"),
        ("strategic_priority", "Strategic Priority"), ("security_pressure", "Security Pressure"),
        ("contractual_clock", "Contractual Clock (SLA)"), ("system_health", "System Health"),
        ("implementation_risk", "Implementation Risk")
    ]
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("New Change Request")),
        dbc.ModalBody([
            dbc.Input(id="cr-title", placeholder="Enter CR Title...", className="mb-2"),
            html.Label("Target Completion Date"),
            dcc.DatePickerSingle(id="target-date", date=date.today(), className="mb-3 w-100"),
            html.Hr(),
            *[html.Div([
                html.Label(name, style={'fontSize': '0.85rem'}),
                dcc.Slider(0, 100, id=key, value=50, marks={0:'0', 100:'100'})
            ], className="mb-2") for key, name in factors]
        ]),
        dbc.ModalFooter(
            dbc.Button("Submit Entry", id="submit-btn", color="danger", className="w-100")
        ),
    ], id="modal-form", is_open=False, size="lg")

# 3. Helper for Tables
def create_editable_table(index_name, dataframe, is_admin=True):
    return dash_table.DataTable(
        id={'type': 'cab-table', 'index': index_name},
        columns=[
            {"name": "Title", "id": "title", "editable": is_admin},
            {"name": "Status", "id": "status", "presentation": "dropdown", "editable": is_admin},
            {"name": "Target Date", "id": "target_date", "type": "datetime", "editable": is_admin},
            {"name": "Days Left", "id": "days_to_deadline", "editable": False},
            {"name": "Quadrant", "id": "quadrant", "editable": False}
        ],
        data=dataframe.to_dict('records') if not dataframe.empty else [],
        editable=is_admin,
        row_selectable="multi" if is_admin else False,
        dropdown={'status': {'options': [{'label': i, 'value': i} for i in STATUS_OPTIONS]}},
        style_header={'backgroundColor': '#ED1944', 'color': 'white'} if index_name == 'active' else ARCHIVE_STYLE,
        style_cell={'padding': '10px', 'textAlign': 'left'},
        css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
        page_size=10
    )

# 4. Layouts
def login_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H3("CAB Priority System Login", className="text-center")),
                    dbc.CardBody([
                        dbc.Input(id="login-email", type="email", placeholder="Enter email", className="mb-3"),
                        dbc.Input(id="login-password", type="password", placeholder="Enter password", className="mb-3"),
                        dbc.Button("Login", id="login-btn", color="primary", className="w-100 mb-3"),
                        html.Div(id="login-error", className="text-danger text-center mt-2")
                    ])
                ], style={"marginTop": "20vh", "padding": "20px", "borderRadius": "15px", "boxShadow": "0px 4px 20px rgba(0,0,0,0.1)"})
            ], width=4)
        ], justify="center"),
        dbc.Button(id="logout-btn", style={"display": "none"})
    ], fluid=True, style={"height": "100vh", "backgroundColor": "#f4f6f9"})


def dashboard_layout(role, name="User"):
    is_admin = (role == 'admin')
    
    tabs_list = [
        dbc.Tab(label="Submissions", tab_id="tab-entry"),
        dbc.Tab(label="Priority Matrix", tab_id="tab-dash"),
        dbc.Tab(label="Live Archive", tab_id="tab-live"),
        dbc.Tab(label="Suspended Archive", tab_id="tab-suspended"),
        dbc.Tab(label="Info", tab_id="tab-info"),
    ]
    
    if is_admin:
        tabs_list.append(dbc.Tab(label="User Management", tab_id="tab-user-mgt"))
        
    return dbc.Container([
        render_request_modal(),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.H3("CAB Priority System", style={'color': 'white', 'fontWeight': '700', 'margin': '0'}),
                    html.P("Scientific Governance & Lifecycle Management", style={'color': '#f0f0f0', 'fontSize': '0.8rem', 'margin': '0'})
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.Span(f"Welcome, {name} ({role.capitalize()})", style={"color": "white", "marginRight": "15px", "alignSelf": "center", "fontSize": "0.85rem"}),
                        dbc.Button("+ New Request", id="open-modal-btn", color="light", size="sm", className="me-2", style=({"display": "block", "padding": "2px 8px", "fontSize": "0.75rem"} if is_admin else {"display": "none"})),
                        dbc.Button("Logout", id="logout-btn", color="dark", size="sm", style={"padding": "2px 8px", "fontSize": "0.75rem"})
                    ], className="d-flex justify-content-end align-items-center h-100")
                ], width=4)
            ], className="align-items-center")
        ], className="mb-4 dashboard-header", style={'backgroundColor': '#ED1944', 'padding': '15px 20px', 'borderRadius': '0 0 15px 15px', 'boxShadow': '0 4px 10px rgba(237, 25, 68, 0.3)'}),

        dbc.Tabs(tabs_list, id="tabs", active_tab="tab-entry", className="custom-tabs"),
        
        html.Div(id="tab-content", className="mt-4"),
        html.Div(id='hidden-storage', style={'display': 'none'}),
        html.Div(id='hidden-user-storage', style={'display': 'none'}),
        
        # Hidden auth inputs to prevent Dash ReferenceError when logged in
        html.Div([
            dbc.Input(id="login-email"),
            dbc.Input(id="login-password"),
            dbc.Button(id="login-btn"),
            html.Div(id="login-error"),
            
            # Hidden user mgt inputs for reference error prevention
            dbc.Input(id="new-user-name"),
            dbc.Input(id="new-user-email"),
            dbc.Input(id="new-user-password"),
            dbc.Select(id="new-user-role"),
            dbc.Button(id="add-user-btn"),
            dbc.Button(id="save-users-btn"),
            dbc.Button(id="delete-users-btn")
        ], style={'display': 'none'})
    ], fluid=True, style={'backgroundColor': '#f4f6f9', 'minHeight': '100vh', 'paddingBottom': '50px'})


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session', storage_type='session'),
    html.Div(id='page-content', children=[login_layout()])
])

# 5. Routing and Auth Callbacks
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('session', 'data')
)
def display_page(pathname, session_data):
    if not session_data or not session_data.get('user'):
        return login_layout()
    return dashboard_layout(session_data.get('role'), session_data.get('name', 'User'))

@app.callback(
    Output('session', 'data'),
    Output('login-error', 'children'),
    Output('url', 'pathname'),
    Input('login-btn', 'n_clicks'),
    Input('logout-btn', 'n_clicks'),
    State('login-email', 'value'),
    State('login-password', 'value'),
    State('session', 'data'),
    prevent_initial_call=True
)
def handle_auth(n_login, n_logout, email, password, session_data):
    trigger = ctx.triggered_id
    if trigger == 'logout-btn':
        return None, "", "/login"
        
    if trigger == 'login-btn' and email and password:
        email_clean = email.strip()
        pwd_clean = password.strip()
        try:
            # use ilike for case-insensitive email matching
            res = supabase.table("cab_roles").select("*").ilike("email", email_clean).eq("password", pwd_clean).execute()
            if res.data:
                user_data = res.data[0]
                role = user_data.get('role', 'user')
                name = user_data.get('name', email_clean)
                return {'user': user_data['email'], 'role': role, 'name': name, 'email': user_data['email']}, "", "/"
            else:
                return dash.no_update, "Invalid email or password", dash.no_update
        except Exception as e:
            return dash.no_update, "Database error: " + str(e), dash.no_update
            
    return dash.no_update, dash.no_update, dash.no_update

# 6. Callback: Tab Content
@app.callback(
    Output("tab-content", "children"), 
    [Input("tabs", "active_tab"), Input("hidden-storage", "children"), Input("hidden-user-storage", "children")],
    State("session", "data")
)
def render_tabs(active_tab, _, __, session_data):
    role = session_data.get('role', 'user') if session_data else 'user'
    is_admin = (role == 'admin')

    res = supabase.table("cab_prioritization").select("*").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    # Dynamically recalculate scores based on today's date
    if not df.empty:
        for idx, row in df.iterrows():
            factors = {k: row.get(k, 0) for k in ["financial_integrity", "service_criticality", "blast_radius", "regulatory_weight", "strategic_priority", "security_pressure", "contractual_clock", "system_health", "implementation_risk"]}
            x, y, quad, days = calculate_coordinates(factors, row['target_date'])
            df.at[idx, 'x_coord'] = x
            df.at[idx, 'y_coord'] = y
            df.at[idx, 'quadrant'] = quad
            df.at[idx, 'days_to_deadline'] = days

    hidden_save = dbc.Button(id="save-btn", style={'display': 'none'})
    hidden_delete = dbc.Button(id="delete-btn", style={'display': 'none'})

    if active_tab == "tab-entry":
        active_df = df[~df['status'].isin(['Live', 'Suspended'])] if not df.empty else pd.DataFrame()
        controls = html.Div([
            dbc.Button("Update & Refresh", id="save-btn", color="success", className="me-2"),
            dbc.Button("Delete Selected", id="delete-btn", color="danger"),
        ], className="mt-3") if is_admin else html.Div([hidden_save, hidden_delete])
        
        return html.Div([
            html.H4("Active Submissions Manager"),
            create_editable_table('active', active_df, is_admin),
            controls
        ])
    
    elif active_tab == "tab-dash":
        active_df = df[~df['status'].isin(['Live', 'Suspended'])] if not df.empty else pd.DataFrame()
        if not active_df.empty:
            import plotly.express as px
            fig = px.scatter(
                active_df, x="x_coord", y="y_coord", text="title", color="quadrant", 
                range_x=[0,100], range_y=[0,100],
                labels={"x_coord": "Urgent", "y_coord": "Important"},
                title="Fintech Priority Matrix"
            )
            
            fig.add_hline(y=50, line_dash="dash", line_color="gray")
            fig.add_vline(x=50, line_dash="dash", line_color="gray")
            
            fig.add_shape(type="rect", x0=0, y0=50, x1=50, y1=100, fillcolor="rgba(52, 152, 219, 0.05)", line_width=0, layer="below")
            fig.add_shape(type="rect", x0=50, y0=50, x1=100, y1=100, fillcolor="rgba(231, 76, 60, 0.05)", line_width=0, layer="below")
            fig.add_shape(type="rect", x0=0, y0=0, x1=50, y1=50, fillcolor="rgba(149, 165, 166, 0.05)", line_width=0, layer="below")
            fig.add_shape(type="rect", x0=50, y0=0, x1=100, y1=50, fillcolor="rgba(241, 196, 15, 0.05)", line_width=0, layer="below")
            
            fig.add_annotation(x=25, y=95, text="P2: SCHEDULE", showarrow=False, font=dict(color="rgba(0,0,0,0.3)", size=16))
            fig.add_annotation(x=75, y=95, text="P1: DO", showarrow=False, font=dict(color="rgba(0,0,0,0.3)", size=16))
            fig.add_annotation(x=25, y=5, text="P4: ELIMINATE", showarrow=False, font=dict(color="rgba(0,0,0,0.3)", size=16))
            fig.add_annotation(x=75, y=5, text="P3: DELEGATE", showarrow=False, font=dict(color="rgba(0,0,0,0.3)", size=16))

            fig.update_layout(plot_bgcolor="white", xaxis_title="Urgent", yaxis_title="Important")
            fig.update_traces(textposition='top center', marker=dict(size=12))

            graph = dcc.Graph(figure=fig, style={'height': '70vh'})
        else:
            graph = html.Div("No active data to display.", className="mt-5 text-center")
        return html.Div([graph, hidden_save, hidden_delete])

    elif active_tab == "tab-live":
        live_df = df[df['status'] == 'Live'] if not df.empty else pd.DataFrame()
        controls = dbc.Button("Apply Changes", id="save-btn", color="success", className="mt-3") if is_admin else hidden_save
        return html.Div([html.H4("Live Archive"), create_editable_table('live', live_df, is_admin), controls, hidden_delete])

    elif active_tab == "tab-suspended":
        susp_df = df[df['status'] == 'Suspended'] if not df.empty else pd.DataFrame()
        controls = dbc.Button("Apply Changes", id="save-btn", color="success", className="mt-3") if is_admin else hidden_save
        return html.Div([html.H4("Suspended Archive"), create_editable_table('suspended', susp_df, is_admin), controls, hidden_delete])

    elif active_tab == "tab-info":
        docs_md = r"""
# CAB Priority System Documentation

The **CAB Priority System** is a professional governance framework and digital tool designed to bring mathematical objectivity to the Change Advisory Board's decision-making process. By moving away from subjective assessments, the system ensures that every change request is evaluated against its true impact on financial integrity, regulatory compliance, and technical stability.

---

## 1. System Overview

The application functions as a lifecycle management tool that categorizes change requests based on a weighted scoring model. It plots each request on a 2D matrix, providing a clear visual representation of priorities to stakeholders and technical teams.

### Core Objectives

* **Objectivity**: Eliminates "gut-feeling" prioritization by using standardized metrics.
* **Transparency**: Provides a clear audit trail of why specific changes were prioritized over others.
* **Lifecycle Tracking**: Manages the flow of changes from initial "CR-raised" status to "Live" or "Suspended" archives.

---

## 2. Scoring Methodology & Calculations

The system generates two coordinates—**Importance (Y-axis)** and **Technical Urgency (X-axis)**—each ranging from 0 to 100.

### Importance Score (Y-Axis)

This score reflects the business value and risk profile of the change. It is calculated as a weighted average of five variables:

$$Importance (Y) = \\frac{(F \\cdot W_f) + (C \\cdot W_c) + (B \\cdot W_b) + (R \\cdot W_r) + (S \\cdot W_s)}{\\sum W}$$

* **Financial Integrity ($F$):** Risk to revenue, reconciliation accuracy, or financial reporting.
* **Service Criticality ($C$):** How essential the service is to daily operations.
* **Blast Radius ($B$):** The scale of potential impact (e.g., number of users affected) if the change fails.
* **Regulatory Weight ($R$):** Compliance requirements from governing bodies or auditors.
* **Strategic Priority ($S$):** Alignment with long-term business goals and partner commitments.

### Technical Urgency Score (X-Axis)

This score measures the pressure to deploy the change immediately. It is calculated across four technical variables:

$$Urgency (X) = \\frac{(P \\cdot W_p) + (L \\cdot W_l) + (H \\cdot W_h) + (I \\cdot W_i)}{\\sum W}$$

* **Security Pressure ($P$):** Immediate need to patch vulnerabilities or address threats.
* **Contractual Clock ($L$):** Deadline pressure dictated by Service Level Agreements (SLAs).
* **System Health ($H$):** Current performance degradation or technical debt risks.
* **Implementation Risk ($I$):** Time-sensitivity and complexity of the deployment window.

---

## 3. The Priority Matrix

Once the $(X, Y)$ coordinates are calculated, every request falls into one of four quadrants:

| Quadrant | Thresholds | Action & Meaning |
| --- | --- | --- |
| **Strategic** | $X > 50, Y > 50$ | **Top Priority.** Critical and time-sensitive; requires immediate resources. |
| **Planned** | $X \leq 50, Y > 50$ | **Scheduled.** High value but not yet urgent; to be placed in upcoming sprints. |
| **Operational** | $X > 50, Y \leq 50$ | **Firefighting.** Lower business value but must be done quickly to maintain stability. |
| **Maintenance** | $X \leq 50, Y \leq 50$ | **Low Priority.** Routine updates that can be deferred if resources are constrained. |

---

## 4. Lifecycle & Status Definitions

The system uses the **Status** field to route data across different views:

* **Active Manager**: Contains items in progress (*CR-raised, In dev, UAT, Sign off, Monitoring*).
* **Live Archive**: Automatically receives items once their status is updated to **Live**.
* **Suspended Archive**: Receives items marked as **Suspended** (deferred or cancelled).

### Key Terms

* **SLA (Service Level Agreement)**: A contractual commitment regarding the timing and quality of service delivery.
* **UAT (User Acceptance Testing)**: The phase where analysts or end-users verify the change before final sign-off.
* **Reconciliation**: The process of ensuring financial records are consistent, a primary focus for this system’s integrity checks.
        """
        return html.Div([
            dbc.Card([
                dbc.CardBody(dcc.Markdown(docs_md, mathjax=True))
            ], className="mb-4"),
            hidden_save, hidden_delete
        ])
        
    elif active_tab == "tab-user-mgt" and is_admin:
        users_res = supabase.table("cab_roles").select("*").execute()
        users_df = pd.DataFrame(users_res.data) if users_res.data else pd.DataFrame()
        
        user_table = dash_table.DataTable(
            id={'type': 'user-table', 'index': 'users'},
            columns=[
                {"name": "Name", "id": "name", "editable": True},
                {"name": "Email", "id": "email", "editable": False},
                {"name": "Role", "id": "role", "presentation": "dropdown", "editable": True},
                {"name": "Password", "id": "password", "editable": True}
            ],
            data=users_df.to_dict('records') if not users_df.empty else [],
            editable=True,
            row_selectable="multi",
            dropdown={'role': {'options': [{'label': 'admin', 'value': 'admin'}, {'label': 'user', 'value': 'user'}]}},
            style_header={'backgroundColor': '#1F2937', 'color': 'white'},
            style_cell={'padding': '10px', 'textAlign': 'left'},
            css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
            page_size=10
        )
        
        return html.Div([
            html.H4("User Management", className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.H6("Add New User"),
                    dbc.Row([
                        dbc.Col(dbc.Input(id="new-user-name", placeholder="Name")),
                        dbc.Col(dbc.Input(id="new-user-email", type="email", placeholder="Email")),
                        dbc.Col(dbc.Input(id="new-user-password", placeholder="Password")),
                        dbc.Col(dbc.Select(id="new-user-role", options=[{"label": "User", "value": "user"}, {"label": "Admin", "value": "admin"}], value="user")),
                        dbc.Col(dbc.Button("Add User", id="add-user-btn", color="primary", className="w-100"))
                    ])
                ])
            ], className="mb-4"),
            user_table,
            html.Div([
                dbc.Button("Save Changes", id="save-users-btn", color="success", className="me-2"),
                dbc.Button("Delete Selected", id="delete-users-btn", color="danger"),
            ], className="mt-3"),
            hidden_save, hidden_delete
        ])
    
    return html.Div([hidden_save, hidden_delete])

# 7. Callback: Modal Toggle
@app.callback(
    Output("modal-form", "is_open"),
    [Input("open-modal-btn", "n_clicks"), Input("submit-btn", "n_clicks")],
    [State("modal-form", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n_open, n_submit, is_open):
    if n_open or n_submit:
        return not is_open
    return is_open

# 8. Callback: CAB CRUD
@app.callback(
    Output("hidden-storage", "children"),
    [Input("submit-btn", "n_clicks"), Input("save-btn", "n_clicks"), Input("delete-btn", "n_clicks")],
    [State({'type': 'cab-table', 'index': ALL}, 'data'),
     State({'type': 'cab-table', 'index': ALL}, 'selected_rows'),
     State("cr-title", "value"), State("target-date", "date"),
     State("session", "data")] + 
    [State(f, "value") for f in ["financial_integrity", "service_criticality", "blast_radius", "regulatory_weight", "strategic_priority", "security_pressure", "contractual_clock", "system_health", "implementation_risk"]],
    prevent_initial_call=True
)
def handle_crud(n_add, n_save, n_del, all_tables_data, all_selected_rows, title, t_date, session_data, *f_vals):
    # Only admins can perform CRUD
    if not session_data or session_data.get('role') != 'admin':
        return dash.no_update

    ctx_trig = dash.callback_context
    if not ctx_trig.triggered: return dash.no_update
    tid = ctx_trig.triggered[0]['prop_id'].split('.')[0]
    
    if tid == "save-btn" and all_tables_data:
        for table_data in all_tables_data:
            if table_data:
                for row in table_data:
                    supabase.table("cab_prioritization").update({
                        "title": row.get("title"), "status": row.get("status"), "target_date": row.get("target_date")
                    }).eq("id", row.get("id")).execute()
    
    elif tid == "submit-btn" and title:
        factors = dict(zip(["financial_integrity", "service_criticality", "blast_radius", "regulatory_weight", "strategic_priority", "security_pressure", "contractual_clock", "system_health", "implementation_risk"], f_vals))
        x, y, quad, days = calculate_coordinates(factors, t_date)
        supabase.table("cab_prioritization").insert({"title": title, "target_date": t_date, "x_coord": x, "y_coord": y, "quadrant": quad, "days_to_deadline": days, "status": "CR-raised", **factors}).execute()
    
    elif tid == "delete-btn" and all_selected_rows:
        for table_idx, selected_rows in enumerate(all_selected_rows):
            if selected_rows:
                for row_idx in selected_rows:
                    row_id = all_tables_data[table_idx][row_idx].get("id")
                    supabase.table("cab_prioritization").delete().eq("id", row_id).execute()

    return str(pd.Timestamp.now())

# 9. Callback: User CRUD
@app.callback(
    Output("hidden-user-storage", "children"),
    [Input("add-user-btn", "n_clicks"), Input("save-users-btn", "n_clicks"), Input("delete-users-btn", "n_clicks")],
    [State({'type': 'user-table', 'index': ALL}, 'data'),
     State({'type': 'user-table', 'index': ALL}, 'selected_rows'),
     State("new-user-name", "value"), State("new-user-email", "value"),
     State("new-user-password", "value"), State("new-user-role", "value"),
     State("session", "data")],
    prevent_initial_call=True
)
def handle_user_crud(n_add, n_save, n_del, all_tables_data, all_selected_rows, name, email, password, role, session_data):
    if not session_data or session_data.get('role') != 'admin':
        return dash.no_update

    ctx_trig = dash.callback_context
    if not ctx_trig.triggered: return dash.no_update
    tid = ctx_trig.triggered[0]['prop_id'].split('.')[0]
    
    if tid == "save-users-btn" and all_tables_data:
        for table_data in all_tables_data:
            if table_data:
                for row in table_data:
                    supabase.table("cab_roles").update({
                        "name": row.get("name"), "role": row.get("role"), "password": row.get("password")
                    }).eq("email", row.get("email")).execute()
                    
    elif tid == "add-user-btn" and email and name and password:
        supabase.table("cab_roles").insert({
            "email": email, "name": name, "role": role, "password": password
        }).execute()
        
    elif tid == "delete-users-btn" and all_selected_rows:
        for table_idx, selected_rows in enumerate(all_selected_rows):
            if selected_rows:
                for row_idx in selected_rows:
                    row_email = all_tables_data[table_idx][row_idx].get("email")
                    # Prevent deleting oneself
                    if row_email != session_data.get('email'):
                        supabase.table("cab_roles").delete().eq("email", row_email).execute()

    return str(pd.Timestamp.now())

if __name__ == "__main__":
    app.run(debug=True)