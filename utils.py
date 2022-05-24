import pandas as pd
import numpy as np

#Loading the Road Safety Data
df = pd.read_csv('dataset.csv', low_memory=False)
df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')

#List of attributes which are used as filters for the map
filter_list = ['Date', 'Day_of_Week', 'Urban_or_Rural_Area', 'Speed_limit', 'newTime', 'Casualty_Severity',
		'Light_Conditions', 'Road_Type', 'Junction_Detail', 'Weather_Conditions', 
		'Road_Surface_Conditions', 'Vehicle_Type']

def get_df_for_regions(values, df=df):
	'''
	Outputs the dataframe required to load the choropleth map according to values filtered by the user

	parameters:
	values(list): List of filter values
	df(pandas dataframe): Dataset

	returns:
	dff(pandas dataframe): Updated dataframe
	'''

	dff = df.copy()
	dff['Date'] = dff['Date'].dt.strftime('%B')
	final_list = []
	for att, value in zip(filter_list, values):
		if value == 'All':
			continue
		if type(value) == list and 'All' in value:
			continue
		if type(value) == list:
			dff = dff[dff[att].isin(value)]
		else:
			dff = dff[dff[att] == value]
		final_list.append(att)
	final_list.append('rgn19nm')
	dff = dff.groupby(final_list)[['Number_of_Casualties','Accident_Count']].sum().reset_index()
	return dff

def get_df_for_individual_accidents(values, df=df):
	'''
	Outputs the dataframe required to load the dot map according to values filtered by the user

	parameters:
	values(list): List of filter values
	df(pandas dataframe): Dataset

	returns:
	dff(pandas dataframe): Updated dataframe
	'''

	dff = df.copy()
	dff['Date'] = dff['Date'].dt.strftime('%B')
	for att, value in zip(filter_list, values):
		if value == 'All':
			continue
		if type(value) == list and 'All' in value:
			continue
		if type(value) == list:
			dff = dff[dff[att].isin(value)]
		else:
			dff = dff[dff[att] == value]
	return dff

def get_labels(df=df):
	'''
	Outputs a dictionary matching dataframe attributes with attribute names for displaying in dash

	parameters:
	df(pandas dataframe): Dataset

	returns:
	labels(dict): Dictionary containing displayable attribute names
	'''
	labels = {}
	for col in df.columns:
		labels[col] = col.replace('_',' ')	
	labels['rgn19nm'] = 'Region'
	return labels

def get_speed_limit(value, df=df):
	'''
	Converts options listed in 'Select Speed Limit' filter to values available in dataframe

	parameters:
	value(str): Value chosen in 'Select Speed Limit' filter
	df(pandas dataframe): Dataset

	returns: Output depends on value 
	'''

	l = df['Speed_limit'].unique()
	if value == '<50':
		return list(l[l<50])
	if value == '>50':
		return list(l[l>=50])
	return 'All'

def get_time(value, df=df):
	'''
	Converts options listed in 'Select Time' filter to values available in dataframe

	parameters:
	value(str): Value chosen in 'Select Time' filter
	df(pandas dataframe): Dataset

	returns: Output depends on value 
	'''
	l = df['newTime'].unique()
	peak = l[(l<17) & (l>=8)]
	if value == 'peak_hours':
		return list(peak)
	if value == 'off_peak_hours':
		return list(np.setdiff1d(l, peak, assume_unique=False))
	return 'All'

