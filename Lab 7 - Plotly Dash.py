# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launches data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Extracts unique launch sites
unique_launch_sites = spacex_df['Launch Site'].unique().tolist()
# Adds an 'All Sites' option for selecting all launch sites
launch_sites_options = [{'label': 'All Sites', 'value': 'ALL'}]
# Adds the rest of the launch sites to the options
launch_sites_options += [{'label': site, 'value': site} for site in unique_launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                            options=launch_sites_options,
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),

                                # TASK 3: Add a slider to select payload range
                                html.Div([
                                    dcc.RangeSlider(
                                        id='payload_slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        marks={i: {'label': f'{i} Kg'} for i in range(0, 10001, 1000)},
                                        value=[min_payload, max_payload]
                                    )
                                ]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
     Output(component_id='success-pie-chart', component_property='figure'),
     [Input(component_id='site-dropdown', component_property='value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL': 
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class',
                     title=f'Total Success Launches for site {entered_site}')
    return fig

# TASK 4: Callback function for the scatter plot updates
@app.callback(
     Output(component_id='success-payload-scatter-chart', component_property='figure'),
     [Input(component_id='site-dropdown', component_property='value'), 
      Input(component_id="payload_slider", component_property="value")]
)
def update_scattergraph(site_dropdown, payload_slider):
    low, high = payload_slider
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    if site_dropdown == 'ALL':
        title = 'Correlation between Payload and Success for All Sites'
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == site_dropdown]
        title = f'Correlation between Payload and Success for {site_dropdown} Site'

    fig = px.scatter(
            filtered_df, 
            x="Payload Mass (kg)", 
            y="class",
            title=title,
            color="Booster Version Category",
            size='Payload Mass (kg)',
            hover_data=['Payload Mass (kg)']
        )
    fig.update_layout(yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success']))

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
