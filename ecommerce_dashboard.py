
import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

# Get the active Snowflake session
session = get_active_session()

# Title of the app
st.title("E-Commerce Dashboard for Etsy")

# Query to get data from Snowflake
query = "SELECT * FROM DATASLEEK.Data"

# Load the data into a DataFrame
data = session.sql(query).to_pandas()

# Display the first few rows of the dataframe
st.header("$ Sales and # of Orders Over Time")

# Filter data for 'Sale' types
sales_data = data[data['TYPE'] == 'Sale']

# Convert 'Date' to datetime format
sales_data['DATE'] = pd.to_datetime(sales_data['DATE'])

# Extract day, month, and year for filtering
sales_data['Day'] = sales_data['DATE'].dt.day
sales_data['Month'] = sales_data['DATE'].dt.month
sales_data['Year'] = sales_data['DATE'].dt.year

# Sidebar filters
st.sidebar.header("Filter Options")

# Year filter
year_options = sales_data['Year'].unique()
selected_years = st.sidebar.multiselect("Select Year", year_options, default=year_options)

# Month filter
month_options = list(range(1, 13))
selected_months = st.sidebar.multiselect("Select Month", month_options, default=month_options)

# Day filter
day_options = list(range(1, 32))
selected_days = st.sidebar.multiselect("Select Day", day_options, default=day_options)

# Apply filters to data
filtered_data = sales_data[
    (sales_data['Year'].isin(selected_years)) &
    (sales_data['Month'].isin(selected_months)) &
    (sales_data['Day'].isin(selected_days))
]

# Group by Date and calculate total sales and number of orders
sales_summary = filtered_data.groupby('DATE').agg(
    total_sales=('AMOUNT', 'sum'),
    num_orders=('AMOUNT', 'count')
).reset_index()

# Create the chart
chart = alt.Chart(sales_summary).mark_bar().encode(
    x=alt.X('DATE:T', title='Period'),
    y=alt.Y('total_sales:Q', title='Sales (USD)'),
    tooltip=['DATE:T', 'total_sales:Q', 'num_orders:Q']
).properties(
    width=700,
    height=400
)

line = alt.Chart(sales_summary).mark_line(color='blue').encode(
    x='DATE:T',
    y=alt.Y('num_orders:Q', title='# of Orders'),
    tooltip=['DATE:T', 'total_sales:Q', 'num_orders:Q']
)

text = line.mark_text(
    align='left',
    baseline='middle',
    dx=3
).encode(
    text='num_orders:Q'
)

# Combine the charts
combined_chart = alt.layer(chart, line, text).resolve_scale(
    y='independent'
)

# Display the chart
st.altair_chart(combined_chart, use_container_width=True)
