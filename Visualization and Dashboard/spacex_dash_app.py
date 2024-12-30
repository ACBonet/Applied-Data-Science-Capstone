# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique().tolist()
min_payload = 0
max_payload = 10000

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    # Include the 'All Sites' option plus each unique site
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                            [{'label': site, 'value': site} for site in launch_sites],
                                    value='ALL',  # Default dropdown value to ALL
                                    placeholder="Select a Launch Site here",
                                    searchable=True  # Enable searching within the dropdown
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                # Suppose these are the min/max from your data or you simply set them manually.
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    # You can add or customize 'marks' to show intervals
                                    marks={i: str(i) for i in range(0, 10001, 2500)},
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])                               

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # If ALL sites are selected
    if entered_site == 'ALL':
        # Create a pie chart using all rows in spacex_df
        # We want to see overall successes by site.
        
        # Count the total number of successful launches (class=1) by site
        success_counts = spacex_df[spacex_df['class'] == 1] \
                         .groupby('Launch Site', as_index=False)['class'] \
                         .count()
        
        fig = px.pie(
            success_counts, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches by Site'
        )
        return fig
    
    else:
        # Filter spacex_df to only data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # For pie chart: we want success vs. failure counts
        # class=1 (success), class=0 (failure)
        # Let's create a simple value_counts or groupby
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count'] 
        # 'index' had 0 or 1, renaming it to 'class'
        
        # Make the pie chart
        fig = px.pie(
            outcome_counts,
            values='count',
            names='class', 
            title=f"Total Success vs. Failure for site {entered_site}"
        )
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(selected_site, payload_range):
    """Return a scatter chart of Payload vs. class, colored by Booster Version, 
       filtered by site (if not ALL) and payload range."""
    
    # Extract the slider min and max
    low, high = payload_range
    
    # Filter the DataFrame by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # Check if ALL sites are selected
    if selected_site == 'ALL':
        # Show all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        # Filter by the selected site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {selected_site}'
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
