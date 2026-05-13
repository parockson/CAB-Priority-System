import plotly.graph_objects as go
from dash import dcc

def create_matrix_chart(df=None):
    fig = go.Figure()

    # Add quadrant background lines
    fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color="Gray", dash="dash"))
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=dict(color="Gray", dash="dash"))

    if df is not None and not df.empty:
        # Plot changes with #ED1944 for high-risk items[cite: 2]
        fig.add_trace(go.Scatter(
            x=df['x_coord'], y=df['y_coord'],
            mode='markers+text',
            text=df['title'],
            marker=dict(size=12, color='#ED1944'),
            hovertemplate="<b>%{text}</b><br>Urgency: %{x}<br>Importance: %{y}<extra></extra>"
        ))

    fig.update_layout(
        title="Scientific Priority Matrix",
        xaxis=dict(title="Urgency", range=[0, 100]),
        yaxis=dict(title="Importance", range=[0, 100]),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return dcc.Graph(figure=fig, id='eisenhower-matrix')