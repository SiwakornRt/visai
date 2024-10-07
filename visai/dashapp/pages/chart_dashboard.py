import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import callback, Input, Output

# Register the page
dash.register_page(__name__, path="/chart-dashboard")

# Load the data from the CSV file
csv_file_path = r"airflow-redis-postgres/src/spark/assets/data/cameras_images_data2.csv"
df = pd.read_csv(csv_file_path)

# Convert the 'timestamp' column to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Function to create the figure and calculate statistics
def create_figure_and_stats(start_date, end_date):
    filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    # Hourly aggregation for maximum
    hourly_df = filtered_df.resample('H', on='timestamp').max().reset_index()

    fig = px.bar(filtered_df, x='timestamp', y='count_bbox', title='Count of Bounding Boxes per Image',
                 labels={'timestamp': 'Timestamp', 'count_bbox': 'Count of Bounding Boxes'})
    
    # Create hourly chart for max count
    hourly_fig = px.bar(hourly_df, x='timestamp', y='count_bbox', title='Max Count of Bounding Boxes per Hour',
                        labels={'timestamp': 'Timestamp', 'count_bbox': 'Max Count of Bounding Boxes'})

    # Calculate statistics
    min_count = filtered_df['count_bbox'].min() if not filtered_df.empty else 0
    max_count = filtered_df['count_bbox'].max() if not filtered_df.empty else 0
    median_count = filtered_df['count_bbox'].median() if not filtered_df.empty else 0

    min_date = filtered_df.loc[filtered_df['count_bbox'] == min_count, 'timestamp'].iloc[0] if not filtered_df.empty else None
    max_date = filtered_df.loc[filtered_df['count_bbox'] == max_count, 'timestamp'].iloc[0] if not filtered_df.empty else None
    median_date = filtered_df.loc[filtered_df['count_bbox'] == median_count, 'timestamp'].iloc[0] if not filtered_df.empty else None
    
    average_count = filtered_df['count_bbox'].mean() if not filtered_df.empty else 0

    # Hourly statistics
    hourly_min_count = hourly_df['count_bbox'].min() if not hourly_df.empty else 0
    hourly_max_count = hourly_df['count_bbox'].max() if not hourly_df.empty else 0
    hourly_median_count = hourly_df['count_bbox'].median() if not hourly_df.empty else 0
    hourly_average_count = hourly_df['count_bbox'].mean() if not hourly_df.empty else 0

    return fig, hourly_fig, min_count, max_count, median_count, average_count, min_date, max_date, median_date, \
           hourly_min_count, hourly_max_count, hourly_median_count, hourly_average_count

# Define the layout of the Dash app using Bootstrap components with padding
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Image Bounding Box Counts", className="text-center"),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df['timestamp'].min(),
                end_date=df['timestamp'].max(),
                display_format='YYYY-MM-DD',
                style={'margin-bottom': '20px'}
            ),
            width=8
        ),
        dbc.Col(
            dcc.Link(
                html.Button('Go to Image Dashboard', className='btn btn-primary'),
                href='/dashboard/image-dashboard',
                style={'margin-top': '20px'}
            ),
            width=4,
            className='d-flex justify-content-end'
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='bar-chart'),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Statistics", className="card-title"),
                    html.P(id='date-range', className='card-text'),  # Date range display
                    html.P(id='min-count', className='card-text'),
                    html.P(id='max-count', className='card-text'),
                    html.P(id='median-count', className='card-text'),
                    html.P(id='average-count', className='card-text'),  # Average count display
                ])
            ]),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='hourly-chart'),
            width=12
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Hourly Statistics", className="card-title"),
                    html.P(id='hourly-min-count', className='card-text'),
                    html.P(id='hourly-max-count', className='card-text'),
                    html.P(id='hourly-median-count', className='card-text'),
                    html.P(id='hourly-average-count', className='card-text'),  # Average count display
                ])
            ]),
            width=12
        )
    ])
], fluid=True, style={'padding': '20px'})  # Add overall padding

# Callback to update the graph and statistics based on the selected date range
@callback(
    Output('bar-chart', 'figure'),
    Output('hourly-chart', 'figure'),  # Output for hourly chart
    Output('date-range', 'children'),  # Output for date range
    Output('min-count', 'children'),
    Output('max-count', 'children'),
    Output('median-count', 'children'),
    Output('average-count', 'children'),  # Output for average count
    Output('hourly-min-count', 'children'),  # Output for hourly min count
    Output('hourly-max-count', 'children'),  # Output for hourly max count
    Output('hourly-median-count', 'children'),  # Output for hourly median count
    Output('hourly-average-count', 'children'),  # Output for hourly average count
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_graph(start_date, end_date):
    fig, hourly_fig, min_count, max_count, median_count, average_count, min_date, max_date, median_date, \
        hourly_min_count, hourly_max_count, hourly_median_count, hourly_average_count = create_figure_and_stats(start_date, end_date)
    
    date_range_text = f"Selected Date Range: {start_date} to {end_date}"
    
    min_count_text = f"Date of Min: {min_date.strftime('%Y-%m-%d %H:%M:%S') if min_date else 'N/A'}, Count: {min_count}"
    max_count_text = f"Date of Max: {max_date.strftime('%Y-%m-%d %H:%M:%S') if max_date else 'N/A'}, Count: {max_count}"
    median_count_text = f"Date of Median: {median_date.strftime('%Y-%m-%d %H:%M:%S') if median_date else 'N/A'}, Count: {median_count}"
    
    average_count_text = f"Average: {average_count:.2f}"

    hourly_min_count_text = f"Hourly Min: {hourly_min_count}"
    hourly_max_count_text = f"Hourly Max: {hourly_max_count}"
    hourly_median_count_text = f"Hourly Median: {hourly_median_count}"
    hourly_average_count_text = f"Hourly Average: {hourly_average_count:.2f}"

    return (fig, hourly_fig, date_range_text, min_count_text, max_count_text, median_count_text, 
            average_count_text, hourly_min_count_text, hourly_max_count_text, hourly_median_count_text, 
            hourly_average_count_text)

