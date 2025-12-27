import streamlit as st
@st.cache_data(show_spinner=False)
def get_bubble_chart(plot_data):
    """Generates the Skill Match Heatmap (Bubble Chart)."""
    import plotly.express as px
    import plotly.graph_objects as go
    if plot_data.empty:
        return go.Figure()
        
    fig = px.scatter(
        plot_data,
        x="jd_skill",
        y="resume_skill",
        size="score",
        color="category",
        color_discrete_map={
            "High Match": "#10B981", 
            "Partial Match": "#F59E0B",
            "Low Match": "#EF4444"      
        },
        hover_data=["score"],
        size_max=50,
        opacity=0.9
    )
    

    fig.update_traces(marker=dict(line=dict(width=1, color='rgba(255,255,255,0.5)')))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)", 
        xaxis=dict(
            showgrid=True, 
            gridcolor="rgba(255,255,255,0.1)", 
            title="Job Description Skills", 
            tickangle=-45,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="rgba(255,255,255,0.1)", 
            title="Your Skills",
            zeroline=False
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=500, 
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02, 
            xanchor="right",
            x=1
        )
    )
    return fig

@st.cache_data(show_spinner=False)
def get_radar_chart(resume_cat_counts, jd_cat_counts):
    """Generates the Skill Category Radar Chart."""
    import plotly.graph_objects as go
    categories = list(set(list(resume_cat_counts.keys()) + list(jd_cat_counts.keys())))
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[resume_cat_counts.get(c, 0) for c in categories],
        theta=categories,
        fill='toself',
        name='Your Profile',
        line_color='#3b82f6'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[jd_cat_counts.get(c, 0) for c in categories],
        theta=categories,
        fill='toself',
        name='Job Requirement',
        line_color='#f59e0b'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False),
            bgcolor="rgba(255,255,255,0.05)"
        ),
        margin=dict(l=40, r=40, t=20, b=20),
        height=350,
        legend=dict(orientation="h", y=-0.1)
    )
    return fig

@st.cache_data(show_spinner=False)
def get_gauge_chart(score):
    """Generates the Overall Match Score Gauge."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Match Score", 'font': {'size': 24, 'color': "white"}},
        number={'font': {'size': 40, 'color': "#3b82f6"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#333",
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.3)"},
                {'range': [50, 80], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [80, 100], 'color': "rgba(16, 185, 129, 0.3)"}
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Outfit"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=250
    )
    return fig

@st.cache_data(show_spinner=False)
def get_sunburst_chart(df_sb):
    """Generates the Sunburst Chart."""
    import plotly.graph_objects as go
    if df_sb.empty:
        return go.Figure()
        
    fig = go.Figure(go.Sunburst(
        ids=df_sb.id,
        labels=df_sb.id,
        parents=df_sb.parent,
        marker=dict(colors=df_sb.color)
    ))
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

@st.cache_data(show_spinner=False)
def get_percentile_gauge(percentile):
    """Generates the Market Competitiveness Gauge."""
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percentile,
        title = {'text': "Percentile Rank"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#4F46E5"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.3)'}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 90}}))
    
    fig.update_layout(height=250, margin=dict(t=40, b=10, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

@st.cache_data(show_spinner=False)
def get_bar_chart(df_scores):
    """Generates the Skill Gap Severity Bar Chart."""
    import plotly.express as px
    import plotly.graph_objects as go
    if df_scores.empty:
        return go.Figure()
        
    fig = px.bar(df_scores, x="Match Score", y="Skill", orientation='h', 
                     color="Match Score", color_continuous_scale="RdYlGn")
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0), 
        height=250, 
        xaxis_range=[0, 100],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af")
    )
    return fig

@st.cache_data(show_spinner=False)
def get_heatmap(df_plot):
    """Generates the Detailed Heatmap."""
    import plotly.graph_objects as go
    if df_plot.empty:
        return go.Figure()
        
    heatmap_data = df_plot.pivot(index='jd_skill', columns='resume_skill', values='score')
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
        colorscale='Viridis', hoverongaps=False,
        hovertemplate='JD Skill: %{y}<br>Resume Skill: %{x}<br>Similarity: %{z:.2f}<extra></extra>'
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=350,
        xaxis=dict(side="bottom", tickangle=-45)
    )
    return fig_heat

@st.cache_data(show_spinner=False)
def get_donut_chart(sizes, labels, colors):
    """Generates a Donut Chart for Skill Distribution."""
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=sizes, 
        hole=.7,
        marker=dict(colors=colors, line=dict(color='#000000', width=2)),
        textinfo='percent',
        hoverinfo='label+value+percent'
    )])
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.2),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=0, b=0, l=0, r=0),
        height=450,
        font=dict(color="white", size=14)
    )
    return fig

@st.cache_data(show_spinner=False)
def get_category_bar_chart(df_cat):
    """Generates the Skill Category Bar Chart."""
    import plotly.express as px
    import plotly.graph_objects as go
    if df_cat.empty:
        return go.Figure()
        
    fig = px.bar(df_cat, x='Category', y='Count', color='Category', 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=300
    )
    return fig

@st.cache_data(show_spinner=False)
def get_sunburst_overview(df_sb):
    """Generates the Overview Sunburst Chart."""
    import plotly.express as px
    import plotly.graph_objects as go
    if df_sb.empty:
        return go.Figure()
        
    fig = px.sunburst(
        df_sb,
        names='id',
        parents='parent',
        values='value',
        color='id', 
        color_discrete_sequence=px.colors.qualitative.Bold,
        branchvalues="total"
    )
    fig.update_traces(textinfo="label+percent entry", insidetextorientation='radial')
    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14, color="white"),
        height=500
    )
    return fig

@st.cache_data(show_spinner=False)
def get_network_graph(edge_x, edge_y, node_x, node_y, node_text, node_color):
    """Generates the Skill Network Graph."""
    import plotly.graph_objects as go
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            color=node_color,
            size=10,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                        ))
    return fig
