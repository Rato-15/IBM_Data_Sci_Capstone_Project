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

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                             ],
                                             value='ALL',
                                             placeholder="Select a launch site",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)

                                dcc.RangeSlider(id='payload-slider',              # Slider component ID
                                                min=0,                            # Slider starting point (0 Kg)
                                                max=10000,                        # Slider ending point (10,000 Kg)
                                                step=1000,                        # Slider interval (1000 Kg)
                                                marks={0: '0',                    # Custom marks for the slider
                                                    10000: '10000'},
                                                value=[min_payload, max_payload]  # Current selected range (min_payload to max_payload)
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size()
        total_launches = spacex_df.groupby('Launch Site').size()
        success_percentage = (success_counts / total_launches * 100).fillna(0)
        labels = success_percentage.index.tolist()
        values = success_percentage.values.tolist()
        title = 'Success Launches Percentage for All Sites'
    else:
        # If a specific site is selected, filter the dataframe for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success = filtered_df[filtered_df['class'] == 1]['class'].count()
        failed = filtered_df[filtered_df['class'] == 0]['class'].count()
        labels = ['Success', 'Failed']
        values = [success, failed]
        title = f'Success vs Failed Launches for {entered_site}'
    
    # Create the pie chart figure
    fig = px.pie(names=labels, values=values, title=title)
    return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        # If all sites are selected, filter the dataframe using selected payload range
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        # Create scatter plot for all sites
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Payload vs Launch Outcome for All Sites', 
                         labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'})
    else:
        # If a specific site is selected, filter the dataframe for that site and payload range
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & 
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        # Create scatter plot for the selected site
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title=f'Payload vs Launch Outcome for {entered_site}',
                         labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'})
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
