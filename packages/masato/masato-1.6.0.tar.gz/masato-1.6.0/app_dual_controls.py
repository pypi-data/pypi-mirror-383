import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, no_update, ctx, ALL

# --- 1. Data and Style Setup ---
# Use the 'tips' dataset
df = px.data.tips()

# Define a scalable and reusable list of styles and their Unicode representations
plotly_symbols = [
    "circle",
    "square",
    "diamond",
    "cross",
    "x",
    "triangle-up",
    "star",
    "hexagon",
    "triangle-down",
    "triangle-left",
    "triangle-right",
]
unicode_symbols = ["●", "■", "◆", "✚", "✖", "▲", "★", "⬢", "▼", "◄", "►"]

# Create mappings for unique categories
all_sexes = df["sex"].unique()
all_days = df["day"].unique()

symbol_map = {
    day: plotly_symbols[i % len(plotly_symbols)] for i, day in enumerate(all_days)
}
color_map = {"Male": "royalblue", "Female": "firebrick"}

# --- 2. Create the Base Figure ---
# This figure contains all possible data points. The callback will control their visibility.
fig = go.Figure()

# Add a trace for every combination of color and style category
for sex in all_sexes:
    for day in all_days:
        df_subset = df[(df["sex"] == sex) & (df["day"] == day)]
        if df_subset.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=df_subset["total_bill"],
                y=df_subset["tip"],
                mode="markers",
                legendgroup=sex,
                customdata=df_subset[["day"]],  # Used to filter by style
                name=f"{sex}, {day}",
                marker=dict(color=color_map[sex], symbol=symbol_map[day], size=10),
                visible=True,  # Initially all are visible
            )
        )

# Set fixed axis ranges and a clean template
x_range_padded = [df["total_bill"].min() * 0.95, df["total_bill"].max() * 1.05]
y_range_padded = [df["tip"].min() * 0.95, df["tip"].max() * 1.05]
fig.update_layout(
    xaxis_range=x_range_padded,
    yaxis_range=y_range_padded,
    xaxis=dict(fixedrange=True),  # Lock the x-axis
    yaxis=dict(fixedrange=True),  # Lock the y-axis
    showlegend=False,
    template="plotly_white",
    margin=dict(t=50, b=50, l=50, r=200),  # Make room for legends on the right
)

# --- 3. Define App and Layout ---
app = Dash(__name__)

# CSS styles for our button-based legends
legend_style = {
    "position": "absolute",
    "top": "20px",
    "right": "20px",
    "display": "flex",
    "flexDirection": "column",
    "alignItems": "flex-start",
}
button_style_active = {
    "backgroundColor": "white",
    "color": "black",
    "border": "1px solid #ccc",
    "padding": "5px 10px",
    "margin": "2px",
    "borderRadius": "5px",
    "textAlign": "left",
    "width": "120px",
    "cursor": "pointer",
    "opacity": 1.0,
}
button_style_inactive = {**button_style_active, "opacity": 0.35}

# Define the app layout with the graph and button legends
app.layout = html.Div(
    [
        html.H1("Multi-Select Scatter Plot with Dash"),
        html.Div(
            style={"position": "relative"},
            children=[
                dcc.Graph(id="scatter-plot", figure=fig),
                html.Div(
                    id="legend-container",
                    style=legend_style,
                    children=[
                        html.H4("Color"),
                        *[
                            html.Button(
                                f"● {sex}",
                                id={"type": "color-btn", "index": sex},
                                style=button_style_active,
                            )
                            for sex in all_sexes
                        ],
                        html.Br(),
                        html.H4("Style"),
                        *[
                            html.Button(
                                f"{unicode_symbols[i % len(unicode_symbols)]} {day}",
                                id={"type": "style-btn", "index": day},
                                style=button_style_active,
                            )
                            for i, day in enumerate(all_days)
                        ],
                    ],
                ),
            ],
        ),
    ]
)


# --- 4. Define the Multi-Select Callback ---
@app.callback(
    Output("scatter-plot", "figure"),
    [
        Input({"type": "color-btn", "index": ALL}, "n_clicks"),
        Input({"type": "style-btn", "index": ALL}, "n_clicks"),
    ],
    [
        State({"type": "color-btn", "index": ALL}, "id"),
        State({"type": "style-btn", "index": ALL}, "id"),
        State({"type": "color-btn", "index": ALL}, "style"),
        State({"type": "style-btn", "index": ALL}, "style"),
        State("scatter-plot", "figure"),
    ],
    prevent_initial_call=True,
)
def update_visibilty(
    color_clicks,
    style_clicks,
    color_ids,
    style_ids,
    color_styles,
    style_styles,
    current_figure,
):
    # Determine which button was clicked
    triggered_id = ctx.triggered_id

    # Create dictionaries to hold the active/inactive state of each button
    color_active_map = {
        id["index"]: style for id, style in zip(color_ids, color_styles)
    }
    style_active_map = {
        id["index"]: style for id, style in zip(style_ids, style_styles)
    }

    # Toggle the state of the clicked button
    category_type = triggered_id["type"]
    category_value = triggered_id["index"]

    if category_type == "color-btn":
        current_style = color_active_map[category_value]
        color_active_map[category_value] = (
            button_style_inactive
            if current_style["opacity"] == 1.0
            else button_style_active
        )
    elif category_type == "style-btn":
        current_style = style_active_map[category_value]
        style_active_map[category_value] = (
            button_style_inactive
            if current_style["opacity"] == 1.0
            else button_style_active
        )

    # Get the set of currently active categories
    active_sexes = {
        sex for sex, style in color_active_map.items() if style["opacity"] == 1.0
    }
    active_days = {
        day for day, style in style_active_map.items() if style["opacity"] == 1.0
    }

    # Create a new figure object to update trace visibility
    new_fig = go.Figure(current_figure)

    # Update visibility based on active categories
    new_fig.for_each_trace(
        lambda trace: trace.update(visible=True)
        if trace.legendgroup in active_sexes and trace.customdata[0][0] in active_days
        else trace.update(visible=False)
    )

    return new_fig


# --- 5. Run the App ---
if __name__ == "__main__":
    app.run(debug=True)
