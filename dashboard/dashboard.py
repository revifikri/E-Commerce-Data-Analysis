import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# Page Configuration
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# Title and Introduction
st.title("🛒 E-commerce Data Analysis Dashboard")
st.markdown("## Comprehensive Insights")

# Load Data Function
main_data = pd.read_csv('main_data.csv')

# Preprocess data - convert date columns to datetime
main_data['order_purchase_date'] = pd.to_datetime(main_data['order_purchase_date'])

datetime_columns = ["order_purchase_date"]
main_data.sort_values(by="order_purchase_date", inplace=True)
main_data.reset_index(inplace=True)
 
for column in datetime_columns:
    main_data[column] = pd.to_datetime(main_data[column])
    

min_date = main_data["order_purchase_date"].min()
max_date = main_data["order_purchase_date"].max()


with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = main_data[(main_data["order_purchase_date"] >= str(start_date)) & 
                (main_data["order_purchase_date"] <= str(end_date))]


# Sidebar for Navigation
st.sidebar.title("📊 Dashboard Sections")
section = st.sidebar.radio("Navigate", [
    "Sales Analysis", 
    "Product Insights", 
    "Geographic Analysis", 
    "Customer Segmentation"
])

# Helper Functions for Analysis
def monthly_sales_trend(data):
    monthly_sales = data.groupby(pd.Grouper(key='order_purchase_date', freq='M'))['price'].sum().reset_index()
    return monthly_sales

def top_product_categories(data, top_n=10):
    return data.groupby('product_category_name')['price'].sum().nlargest(top_n)

def geographic_sales_analysis(data):
    return data.groupby('customer_state')['price'].sum().sort_values(ascending=False)


if section == "Sales Analysis":
    st.header("💹 Sales Analysis")
    
    # Monthly Sales Trend
    st.subheader("Monthly Sales Trend")
    monthly_sales = monthly_sales_trend(main_df)
    
    fig = px.line(monthly_sales, x='order_purchase_date', y='price', 
                  title='Monthly Sales Trend', 
                  labels={'order_purchase_date':'Date', 'price':'Total Sales'})
    st.plotly_chart(fig, use_container_width=True)
    

elif section == "Product Insights":
    st.header("📦 Product Insights")
    
    # Top 10 Product Categories (new visualization)
    st.subheader("Top 10 Products by Category")
    
    # Create matplotlib figure
    plt.figure(figsize=(20, 10))
    
    # Create countplot for top 10 categories
    ax = sns.countplot(
        x='product_category_name', 
        data=main_df, 
        palette='gist_earth',
        order=main_df['product_category_name'].value_counts()[:10].sort_values().index
    )
    
    # Set title
    ax.set_title("Top 10 Products", fontsize=15, weight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Display the figure in Streamlit
    st.pyplot(plt.gcf())
    
    
elif section == "Geographic Analysis":
    st.header("🗺️ Geographic Sales Analysis")
    
    # Calculate sales by state
    geo_sales = main_df.groupby('customer_state')['price'].sum().sort_values(ascending=False)
    
    # Display state sales distribution
    st.subheader("Sales Distribution by State")
    
    # Create matplotlib figure with specified styling
    plt.figure(figsize=(12, 6))
    
    # Create bar plot using the Blues color palette
    colors = sns.color_palette("Blues_d", n_colors=10)
    geo_sales.head(10).plot(kind='bar', color=colors)
    
    # Configure chart appearance
    plt.title('Top 10 States by Sales', fontsize=14)
    plt.xlabel('State', fontsize=12)
    plt.ylabel('Total Sales', fontsize=12)
    plt.xticks(rotation=45)
    
    # Adjust layout
    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(plt.gcf())

elif section == "Customer Segmentation":
    st.header("👥 Customer Segmentation")
    
    # Prepare Customer Metrics
    customer_metrics = main_df.groupby('customer_unique_id').agg({
        'order_id': 'nunique',
        'price': 'sum',
        'order_purchase_date': 'max'
    }).reset_index()
    
    customer_metrics.columns = ['customer_unique_id', 'frequency', 'monetary', 'last_purchase']
    latest_date = main_df['order_purchase_date'].max()
    customer_metrics['recency'] = (latest_date - customer_metrics['last_purchase']).dt.days
    customer_metrics['customer_unique_id'] = customer_metrics['customer_unique_id'].str[-8:]
    
    # Original 3D Scatter visualization
    st.subheader("Customer Segments by Recency, Frequency, and Monetary Value")
    
    # RFM Top Customers Visualization (3 bar charts in a row)
    st.subheader("Best Customer Based on RFM Parameters")
    
    # Create a figure with 3 subplots using Matplotlib
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
    
    # Define consistent color scheme for bars
    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
    
    # First chart (left): Top 5 customers by Recency (lowest days = best)
    sns.barplot(
        y="recency",  # Vertical axis shows recency values 
        x="customer_unique_id",  # Horizontal axis shows customer IDs
        data=customer_metrics.sort_values(by="recency", ascending=True).head(5),  # Sort ascending because lower days = more recent
        palette=colors,
        ax=ax[0]  # Place in first subplot position
    )
    
    # Configure first chart appearance
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=16)
    ax[0].tick_params(axis='x', labelsize=12, rotation=45)
    
    # Second chart (middle): Top 5 customers by Frequency
    sns.barplot(
        y="frequency",
        x="customer_unique_id",
        data=customer_metrics.sort_values(by="frequency", ascending=False).head(5),  # Descending because higher = better
        palette=colors,
        ax=ax[1]  # Place in second subplot position
    )
    
    # Configure second chart appearance
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=16)
    ax[1].tick_params(axis='x', labelsize=12, rotation=45)
    
    # Third chart (right): Top 5 customers by Monetary value
    sns.barplot(
        y="monetary",
        x="customer_unique_id",
        data=customer_metrics.sort_values(by="monetary", ascending=False).head(5),  # Descending because higher = better
        palette=colors,
        ax=ax[2]  # Place in third subplot position
    )
    
    # Configure third chart appearance
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary", loc="center", fontsize=16)
    ax[2].tick_params(axis='x', labelsize=12, rotation=45)
    
    # Add overall title for the entire figure
    plt.suptitle("Best Customer Based on RFM Parameters", fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout
    
    # Display the figure in Streamlit
    st.pyplot(fig)
    
    # High-Value Customer Analysis
    st.subheader("High-Value Customer Insights")
    
    # Simple segmentation
    customer_metrics['segment'] = pd.qcut(
        customer_metrics['monetary'], 
        q=[0, 0.6, 0.8, 1.0], 
        labels=['Low Value', 'Medium Value', 'High Value']
    )
    
    segment_breakdown = customer_metrics['segment'].value_counts()
    
    fig_pie = px.pie(values=segment_breakdown.values, 
                 names=segment_breakdown.index, 
                 title='Customer Value Segments')
    st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🚀 Olist E-commerce Data Analysis | Built with Streamlit")