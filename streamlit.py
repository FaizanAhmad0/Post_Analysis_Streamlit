import streamlit as st
import pandas as pd
import plotly.express as px
import re
from bs4 import BeautifulSoup
import os

csv_file = 'data.csv'
if not os.path.exists(csv_file):
    st.title("Import Data")
    st.write("Please import the CSV file to proceed.")
    if st.button("Import CSV"):
        st.write("CSV file imported successfully!")
    else:
        st.stop()  

combined_data = pd.read_csv(csv_file, index_col=0)


st.set_page_config(
    page_title="Article Analytics",
    page_icon=":bar_chart:",
    layout="wide"
)


st.sidebar.title("Search Articles")
search_type = st.sidebar.radio("Search by:", ("UserID", "Name"))

if search_type == "UserID":
    user_input = st.sidebar.number_input("Enter UserID:", min_value=1, step=1)
    search_results = combined_data[combined_data['id'] == user_input]
elif search_type == "Name":
    user_input = st.sidebar.text_input("Enter Name:")
    search_results = combined_data[combined_data['LastEditorDisplayName'] == user_input]

# Create buttons for navigation
st.sidebar.header("Navigation")
pages = ["Best Articles", "Views Distribution", "Dependable Columns Analysis", "User and Article Activity"]
page = st.sidebar.selectbox("Select a page", pages)

# Main content
st.title("Article Analytics")

if page == "Best Articles":

# Best Articles by Views
    st.header("Top 10 Articles by Views")
    col1, col2 = st.columns(2)
    with col1:
        best_articles = combined_data.sort_values(by='ViewCount', ascending=False).head(10)
        st.dataframe(best_articles[['Title', 'ViewCount']].style.format({'ViewCount': '{:,.0f}'}))
    with col2:
        fig = px.bar(best_articles, x='Title', y='ViewCount', title='Top 10 Articles by Views', color_discrete_sequence=['skyblue'])
        fig.update_layout(xaxis_title='Article Title', yaxis_title='View Count')
        st.plotly_chart(fig, use_container_width=True)

    # Top 10 Articles by Score
    st.header("Top 10 Articles by Score")
    col1, col2 = st.columns(2)
    with col1:
        top_score_articles = combined_data.sort_values(by='Score', ascending=False).head(10)
        st.dataframe(top_score_articles[['Title', 'Score']].style.format({'Score': '{:,.0f}'}))
    with col2:
        fig = px.bar(top_score_articles, x='Title', y='Score', title='Top 10 Articles by Score', color_discrete_sequence=['skyblue'])
        fig.update_layout(xaxis_title='Article Title', yaxis_title='Score')
        st.plotly_chart(fig, use_container_width=True)

elif page == "Views Distribution":
    # Visualize views distribution
    # Filter out view counts where count is greater than 0
    non_zero_views_data = combined_data[combined_data['ViewCount'] > 0]

    # Visualize views distribution
    st.header("Views Distribution")
    fig = px.histogram(non_zero_views_data, x='ViewCount', title='Distribution of Views (Excluding 0 views)', nbins=50)
    fig.update_layout(xaxis_title="View Count", yaxis_title="Frequency")
    st.plotly_chart(fig, use_container_width=True)

    # Additional Visualization: Article Distribution by Post Type (Top 10)
    st.header("Top 10 Article Distribution by Post Type")
    top_post_types = combined_data['PostTypeId'].value_counts().head(10)
    st.bar_chart(top_post_types)



elif page == "Dependable Columns Analysis":
    # Dependable Columns Analysis
    st.header("Dependable Columns Analysis")

    st.subheader("Correlation Matrix")
    corr_matrix = combined_data.corr()
    fig = px.imshow(corr_matrix,
                    labels=dict(x="Columns", y="Columns", color="Correlation"),
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    color_continuous_scale='viridis')
    st.plotly_chart(fig, use_container_width=True)

    
    st.subheader("Pairplot")
    numerical_cols = combined_data.select_dtypes(include='number').columns
    fig = px.scatter_matrix(combined_data[numerical_cols])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Variable Dependence Analysis")
    # Numerical Variables vs. Numerical Variables (Scatter plot matrix)
    numerical_cols = ['AnswerCount', 'CommentCount', 'Score', 'ViewCount', 'FavoriteCount']
    fig = px.scatter_matrix(combined_data[numerical_cols])
    st.plotly_chart(fig, use_container_width=True)

    # Categorical Variables vs. Numerical Variables (Box plot)
    categorical_cols = ['PostTypeId']  # Add more categorical columns if needed
    for col in categorical_cols:
        fig = px.box(combined_data, x=col, y='Score', points="all")
        fig.update_layout(title=f"{col} vs. Score", xaxis_title=col, yaxis_title="Score")
        st.plotly_chart(fig, use_container_width=True)

    # Time Series Analysis (Line plot)
    time_series_cols = ['CreationDate']  # Assuming these are datetime columns
    for col in time_series_cols:
        combined_data[col] = pd.to_datetime(combined_data[col])
        data = combined_data.set_index(col).resample('M').size()  # Resample by month
        fig = px.line(data, title=f"Number of Articles Over Time ({col})", labels={'size': 'Number of Articles'})
        st.plotly_chart(fig, use_container_width=True)


elif page == "User and Article Activity":
    # User and Article Activity Analysis
    st.header("User and Article Activity Analysis")

    # User Activity Over Time (Line plot)
    st.subheader("User Activity Over Time")
    user_activity = combined_data.groupby('OwnerUserId')['CreationDate'].count().reset_index()
    user_activity.columns = ['OwnerUserId', 'ActivityCount']
    fig = px.line(user_activity, x='OwnerUserId', y='ActivityCount', title='User Activity Over Time')
    fig.update_layout(xaxis_title="User ID", yaxis_title="Activity Count")
    st.plotly_chart(fig, use_container_width=True)



    st.subheader("Most Active Editors")
    most_active_editors = combined_data['LastEditorUserId'].value_counts().head(10)
    st.bar_chart(most_active_editors)

if search_results is not None:
    st.header("Search Results")
    st.dataframe(search_results[['Title', 'Body']])
    # st.dataframe(search_results)

# Footer
st.markdown("---")
st.write("Post Analysis")