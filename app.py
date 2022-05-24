from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import json
from urllib.request import urlopen
from utils import get_df_for_regions, get_df_for_individual_accidents, get_labels, get_speed_limit, get_time

#Loading the Road Safety Data
df = pd.read_csv('dataset.csv', low_memory=False)
df2 = df.copy()
df2['Date'] = pd.to_datetime(df2['Date'], format='%Y/%m/%d')

#Getting dataframe columns for the 'Color by' option when viewing choropleth map
hover_data_region = ['Number_of_Casualties', 'Accident_Count']

#Getting display names for attributes in df
labels = get_labels(df2)

#Making lists for checklist filter options
light_conditions = list(df2['Light_Conditions'].unique())
light_conditions.insert(0, 'All')

road_type = list(df2['Road_Type'].unique())
road_type.insert(0, 'All')

junction_details = list(df2['Junction_Detail'].unique())
junction_details.insert(0, 'All')

weather_conditions = list(df2['Weather_Conditions'].unique())
weather_conditions.insert(0, 'All')

road_conditions = list(df2['Road_Surface_Conditions'].unique())
road_conditions.insert(0, 'All')

vehicle_type = list(df2['Vehicle_Type'].unique())
vehicle_type.insert(0, 'All')

#Loading the geometry data for the choropleth map
with open('uk_regions.geojson') as f:
  data = json.load(f)

#Initialising the dash app
app = Dash(__name__)

app.layout = html.Div([

	html.H1("Visualisation Tool for UK Road Safety Data 2015", style={'text-align':'center'}),

	#Making filters for viewing the choropleth map
	html.Div([
		html.Div([
			html.Label("Select a month"),
			dcc.Dropdown(id='select_month',
					options=[
						{'label':'All', 'value':'All'},
						{'label':'January', 'value':'January'},
						{'label':'February', 'value':'February'},
						{'label':'March', 'value':'March'},
						{'label':'April', 'value':'April'},
						{'label':'May', 'value':'May'},
						{'label':'June', 'value':'June'},
						{'label':'July', 'value':'July'},
						{'label':'August', 'value':'August'},
						{'label':'September', 'value':'September'},
						{'label':'October', 'value':'October'},
						{'label':'November', 'value':'November'},
						{'label':'December', 'value':'December'},
						],
					multi=True,
					value='All',
					style={'width': '60%'},
					clearable=False,
					),
			html.Br(),

			html.Label("Select a day"),
			dcc.Dropdown(id='select_day',
					options=[
						{'label':'All', 'value':'All'},
						{'label':'Monday', 'value':1},
						{'label':'Tuesday', 'value':2},
						{'label':'Wednesday', 'value':3},
						{'label':'Thursday', 'value':4},
						{'label':'Friday', 'value':5},
						{'label':'Saturday', 'value':6},
						{'label':'Sunday', 'value':7},
						],
					multi=True,
					value='All',
					style={'width': '60%'},
					clearable=False,
					),
			], style={'padding': 10, 'flex': 1}),

		html.Div([
			html.Label("Select Area"),
			dcc.RadioItems(id='select_area',
					options=[
						{'label': 'All', 'value': 'All'},
						{'label': 'Urban', 'value': 'Urban'},
						{'label': 'Rural', 'value': 'Rural'},
						],
					value='All',
					),
			html.Br(),

			html.Label("Select Speed Limit"),
			dcc.RadioItems(id='select_speed_limit',
					options=[
						{'label': 'All', 'value': 'All'},
						{'label': 'Less than 50km/h', 'value': '<50'},
						{'label': 'More than 50km/h', 'value': '>50'},
						],
					value='All',
					),
			html.Br(),

			html.Label("Select Time"),
			dcc.RadioItems(id='select_time',
					options=[
						{'label': 'All', 'value': 'All'},
						{'label': 'Peak Hours', 'value': 'peak_hours'},
						{'label': 'Off-peak Hours', 'value': 'off_peak_hours'},
						],
					value='All',
					),
			], style={'padding': 10, 'flex': 1}),
		], style={'display': 'flex', 'flex-direction': 'row'}),

	html.Div(id='output_container', children=[]),
	html.Br(),

	#Main map
	dcc.Graph(id='uk_map', figure={}),

	html.Div([
		html.Label("View by"),
		dcc.RadioItems(id='select_type',
			options=[
				{'label': 'Region', 'value':'region'},
				{'label': 'Individual Accidents', 'value':'individual_accidents'},
				],
				value='region',
				),
		html.Br(),

		html.Label("Colory by"),
		dcc.Dropdown(id='select_attribute',
			options=[
				],
				value='Number_of_Casualties',
				style={'width': '50%'},
				clearable=False,
				),
		], style={'padding': 10, 'flex': 1}),
	
	html.Div([
		html.Div([
			html.Label("Select Severity Class"),
			dcc.Checklist(id='select_casualty_severity',
				options=['All', 'Slight', 'Serious', 'Fatal'],
				value=['All'],
				labelStyle={'display': 'block'},
				),
			html.Br(),
			], style={'padding': 10, 'flex': 1}),

		html.Div([	
			html.Label("Select Light Conditions"),
			dcc.Checklist(id='select_light_conditions',
				options=light_conditions,
				value=['All'],
				labelStyle={'display': 'block'},
				),
			html.Br(),
			], style={'padding': 10, 'flex': 1}),

		html.Div([
			html.Label("Select Road Type"),
			dcc.Checklist(id='select_road_type',
				options=road_type,
				value=['All'],
				labelStyle={'display': 'block'},
				),
			html.Br(),
			], style={'padding': 10, 'flex': 1}),
		], style={'display': 'flex', 'flex-direction': 'row'}),

	html.Div([
		html.Div([
			html.Label("Select Junction Details"),
			dcc.Checklist(id='select_junction_details',
				options=junction_details,
				value=['All'],
				labelStyle={'display': 'block'},
				),
			html.Br(),
			], style={'padding': 10, 'flex': 1}),

		html.Div([
			html.Label("Select Weather Conditions"),
			dcc.Checklist(id='select_weather_conditions',
				options=weather_conditions,
				value=['All'],
				labelStyle={'display': 'block'},
				),
			html.Br(),
			], style={'padding': 10, 'flex': 1}),

		html.Div([
			html.Label("Select Road Surface Conditions"),
			dcc.Checklist(id='select_road_conditions',
				options=road_conditions,
				value=['All'],
				labelStyle={'display': 'block'},
				),
			html.Br(),
			], style={'padding': 10, 'flex': 1}),
		], style={'display': 'flex', 'flex-direction': 'row'}),

	html.Div([
		html.Label("Select Vehicle Type"),
		dcc.Checklist(id='select_vehicle_type',
			options=vehicle_type,
			value=['All'],
			labelStyle={'display': 'block'},
			),
		], style={'padding': 10, 'flex': 1}),


	html.Div([
		    html.Pre(children= "Bar Plot",
		    style={"text-align": "center", "font-size":"100%", "color":"black"})
		]),

	html.Div([
	    html.Label(['X-axis:'],style={'font-weight': 'bold'}),
	    dcc.Dropdown(
		id='xaxis_raditem',
		options=[
			 {'label': 'Month', 'value': 'Month'},
			 {'label': 'Region', 'value': 'Region'},
			{'label': 'Pedestrian Crossing Human Control', 'value': 'Pedestrian_Crossing-Human_Control'},
			{'label': 'Pedestrian Crossing Physical Facilities', 'value': 'Pedestrian_Crossing-Physical_Facilities'},
			{'label': 'Casualty Severity', 'value': 'Casualty_Severity'},
			{'label': 'Casualty Class', 'value': 'Casualty_Class'},
			{'label': 'Vehicle Manoeuvre', 'value': 'Vehicle_Manoeuvre'},
			{'label': 'Urban or Rural Area', 'value': 'Urban_or_Rural_Area'},
			{'label': 'Vehicle Type', 'value': 'Vehicle_Type'},
			{'label': 'Light Conditions', 'value': 'Light_Conditions'},
			{'label': 'Road Surface Conditions', 'value': 'Road_Surface_Conditions'},
			{'label': 'Weather Conditions', 'value': 'Weather_Conditions'},
			{'label': 'Junction Detail', 'value': 'Junction_Detail'},
			{'label': 'Speed limit', 'value': 'Speed_limit'},
			{'label': 'Road Type', 'value': 'Road_Type'},
			{'label': 'Time', 'value': 'Time'},
			{'label': 'Day of Week', 'value': 'Day_of_Week'},
			{'label': 'Latitude', 'value': 'Latitude'},
			{'label': 'Longitude', 'value': 'Longitude'},
			{'label': 'Number of Vehicles', 'value': 'Number_of_Vehicles'},
		],
		value='Road_Surface_Conditions',
		style={"width": "50%"}
	    ),

	    html.Br(),

	    html.Label(['Y-axis'], style={'font-weight': 'bold'}),
	    dcc.RadioItems(
	    	id='yaxis_raditem',
		options=[
			{'label': 'Number of Casualties', 'value': 'Number_of_Casualties'},
			{'label': 'Number of Accidents', 'value': 'Accident_Count'},
			],
			value='Number_of_Casualties',
			style={'width': '50%'}
		),
		
		dcc.Graph(id='bar_graph'),

	], style={'padding': 10, 'flex':1}),



	html.Div([
		html.Pre(children="PCP Plot",
				 style={"text-align": "center", "font-size": "100%", "color": "black"})
	]),

	html.Div([
		html.Label(['Variables to compare:'], style={'font-weight': 'bold'}),
		dcc.Checklist(
			id='dimension',
			options=[
				{'label': 'Speed limit', 'value': 'Speed_limit'},
				{'label': 'Day of Week', 'value': 'Day_of_Week'},
				{'label': 'Latitude', 'value': 'Latitude'},
				{'label': 'Longitude', 'value': 'Longitude'},
				{'label': 'Number of Vehicles', 'value': 'Number_of_Vehicles'},
				{'label': 'Number of Casualties', 'value': 'Number_of_Casualties'},
			],
			value=[],
			style={"width": "50%"},
		),
		html.Br(),

		html.Label(['Color-filter:'], style={'font-weight': 'bold'}),
		dcc.Dropdown(
			id='color-filter',
			options=[
				{'label': 'Speed limit', 'value': 'Speed_limit'},
				{'label': 'Day of Week', 'value': 'Day_of_Week'},
				{'label': 'Latitude', 'value': 'Latitude'},
				{'label': 'Longitude', 'value': 'Longitude'},
				{'label': 'Number of Vehicles', 'value': 'Number_of_Vehicles'},
				{'label': 'Number of Casualties', 'value': 'Number_of_Casualties'},
			],
			value=None,
			style={"width": "50%"}
		),

			dcc.Graph(id='the_graph'),

	], style={'padding': 10, 'flex': 1}),


	])

@app.callback(
	[Output('select_attribute', 'options'),
	Output('select_attribute', 'value')],
	Input('select_type', 'value'),
	)
def show_hide_dropdown(fig_type):
	'''
	Changes dropdown values depending on which figure is being displayes

	Parameters:
	fig_type(str): Name of map being displayed (Chropleth or Dot)

	Returns:
	options(list): Dictionary of dropdown options corresponding to type of map chosen
	value(str): Default value for dropdown
	'''

	if fig_type == 'region':
		options=[
			{'label': 'Number of Casualties', 'value': 'Number_of_Casualties'},
			{'label': 'Number of Accidents', 'value' : 'Accident_Count'},
			]
	else:
		options=[
			{'label': 'Number of Casualties', 'value': 'Number_of_Casualties'},
			{'label': 'Light Conditions', 'value': 'Light_Conditions'},
			{'label': 'Weather Conditions', 'value': 'Weather_Conditions'},
			{'label': 'Road Surface Condtions', 'value': 'Road_Surface_Conditions'},
			{'label': 'Vehicle Type', 'value': 'Vehicle_Type'},
			{'label': 'Road Type', 'value': 'Road_Type'},
			]
	value = 'Number_of_Casualties'
	return options, value

@app.callback(
	Output('uk_map', 'figure'),
	Input('select_month', 'value'),
	Input('select_day', 'value'),
	Input('select_area', 'value'),
	Input('select_speed_limit', 'value'),
	Input('select_time', 'value'),
	Input('select_casualty_severity', 'value'),
	Input('select_light_conditions', 'value'),
	Input('select_road_type', 'value'),
	Input('select_junction_details', 'value'),
	Input('select_weather_conditions', 'value'),
	Input('select_road_conditions', 'value'),
	Input('select_vehicle_type', 'value'),
	Input('select_type', 'value'),
	Input('select_attribute', 'value'),
	)
def update_graph(month, day, area, speed_limit, time, severity, light_conditions, 
		road_type, junction_details, weather_conditions, road_conditions,
		vehicle_type, fig_type, att):
	'''
	Updates map according to values chosen in the filters

	Parameters:
	Values chosen for each filter

	Returns:
	fig(plotly figure): Choropleth or dot map (depending on user input)
	'''

	sl = get_speed_limit(speed_limit, df2)
	new_time = get_time(time, df2)

	params_for_df = [month, day, area, sl, new_time, severity, light_conditions,
			road_type, junction_details, weather_conditions, road_conditions,
			vehicle_type]

	if fig_type == 'region':
		dff = get_df_for_regions(params_for_df, df2)
		fig = px.choropleth_mapbox(
			dff,
			geojson=data,
			locations='rgn19nm',
			featureidkey='properties.rgn19nm',
			color=att,
			opacity=0.5,
			hover_data = hover_data_region,
			labels=labels
		)
	else:
		dff = get_df_for_individual_accidents(params_for_df, df2)
		fig = px.scatter_mapbox(dff,
			dff.Latitude,
			dff.Longitude,
			color=att,
			opacity=0.5,
			hover_name='Accident_Index',
			labels=labels
		)

	fig.update_layout(mapbox_style="carto-positron", 
			      mapbox_zoom=4,
			      mapbox_center={"lat": 55, "lon": 0},
			      margin={"r":0,"t":0,"l":0,"b":0},
			      uirevision='constant',
			      font_family='Courier New',
			      hoverlabel=dict(
			      	font_size=16,
				font_family='Rockwell',
				)
		)

	return fig




@app.callback(
    Output(component_id='bar_graph', component_property='figure'),
    [Input(component_id='xaxis_raditem', component_property='value'),
    Input(component_id='yaxis_raditem', component_property='value'),
     Input(component_id='uk_map', component_property='clickData'),]
)

def bar_graph(x_axis, y_axis, clickData):
    '''
    Updates the bar graph 
    
    Parameters:
    Values chosen for the bar graph filters
    
    Returns:
    histogram(plotly figure): Histogram showing the values of attribute chosen by user
    		: Values are grouped according to attribute chosen by user
    '''

    bar_df = df.copy()

    if clickData is None:
        bar_df_copy = bar_df.copy()

        bar_df_copy.rename(columns={'rgn19nm': 'Region'}, inplace=True)
        bar_df_copy['Date'] = pd.to_datetime(bar_df_copy['Date'], format='%Y/%m/%d')
        bar_df_copy['Month'] = bar_df_copy['Date'].dt.month_name()

        histogram=px.histogram(
                data_frame=bar_df_copy,
                x=x_axis,
                y=y_axis,
                title= labels[y_axis] + ' by '+ labels[x_axis],
		labels=labels,
		opacity=0.8,
                )

        histogram.update_layout(xaxis={'categoryorder':'total ascending'},
				yaxis_title = labels[y_axis],
				)

        return (histogram)

    else:
        bar_df_copy = bar_df.copy()

        bar_df_copy.rename(columns={'rgn19nm': 'Region'}, inplace=True)
        bar_df_copy['Date'] = pd.to_datetime(bar_df_copy['Date'], format='%Y/%m/%d')
        bar_df_copy['Month'] = bar_df_copy['Date'].dt.month_name()
        click_region = clickData["points"][0]["location"]
        bar_df_copy = bar_df_copy[bar_df_copy["Region"] == click_region]

        histogram = px.histogram(
            data_frame=bar_df_copy,
            x=x_axis,
            y=y_axis,
            title= labels[y_axis] + ' by ' + labels[x_axis] + " ({})".format(click_region),
	    labels=labels,
        )

        histogram.update_layout(xaxis={'categoryorder': 'total ascending'},
			yaxis_title = labels[y_axis],
			)

        return (histogram)

@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='dimension', component_property='value'),
     Input(component_id='color-filter', component_property='value'),
	 Input(component_id='uk_map', component_property='clickData'),]
)

def pcp_graph(dimension, color, clickData):
	'''
	Updates the parallels coordinate plot(pcp)

	Parameters:
	Values chosen for the pcp filters

	Returns:
	pcp_plot(plotly figure): Shows relationship between variables chosen by the user
	'''

	pcp_df = df.copy()

	if clickData is None:
		pcp_df_copy = pcp_df.copy()

		pcp_plot = px.parallel_coordinates(
			pcp_df_copy, dimensions=dimension, color = color, 
			color_continuous_scale=px.colors.diverging.Tealrose,
			labels=labels,
				)

		return (pcp_plot)

	else:
		pcp_df_copy = pcp_df.copy()
		pcp_df_copy = pcp_df
		pcp_df_copy['Date'] = pd.to_datetime(pcp_df_copy['Date'], format='%Y/%m/%d')
		pcp_df_copy['Month'] = pcp_df_copy['Date'].dt.month_name()
		pcp_df_copy.rename(columns={'rgn19nm': 'Region'}, inplace=True)
		click_region = clickData["points"][0]["location"]
		pcp_df_copy = pcp_df_copy[pcp_df_copy["Region"] == click_region]



		pcp_plot = px.parallel_coordinates(
			pcp_df_copy, dimensions=dimension, color=color, 
			color_continuous_scale=px.colors.diverging.Tealrose,
			title = click_region,
			labels=labels
		)

		return (pcp_plot)


#Run app
if __name__ == '__main__':
	app.run_server(debug=True)
