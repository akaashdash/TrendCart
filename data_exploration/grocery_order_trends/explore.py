import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

def explore(sales_array, sales_data, products_df):
    # 1. Pick the ten most sold items and plot them over the weeks
    total_sales = sales_array.sum(axis=(0, 1))
    top_ten_items = total_sales.argsort()[-10:][::-1]
    top_ten_sales = sales_array[:, :, top_ten_items].sum(axis=0)
    
    plt.figure(figsize=(10, 6))
    for i, item_id in enumerate(top_ten_items):
        item_name = products_df.loc[products_df['product_id'] == item_id + 1, 'product_name'].values[0]
        plt.plot(top_ten_sales[:, i], label=item_name)
    plt.xlabel('Week')
    plt.ylabel('Quantity Sold')
    plt.title('Top 10 Most Sold Items')
    plt.legend()
    plt.show()

    # 2. Pick the ten least sold items and plot them over the weeks
    bottom_ten_items = total_sales.argsort()[:10]
    bottom_ten_sales = sales_array[:, :, bottom_ten_items].sum(axis=0)
    
    plt.figure(figsize=(10, 6))
    for i, item_id in enumerate(bottom_ten_items):
        item_name = products_df.loc[products_df['product_id'] == item_id + 1, 'product_name'].values[0]
        plt.plot(bottom_ten_sales[:, i], label=item_name)
    plt.xlabel('Week')
    plt.ylabel('Quantity Sold')
    plt.title('Bottom 10 Least Sold Items')
    plt.legend()
    plt.show()

    # 3. Plot all the items sold over the weeks
    total_sales_per_week = sales_array.sum(axis=(0, 2))
    
    plt.figure(figsize=(10, 6))
    plt.plot(total_sales_per_week)
    plt.xlabel('Week')
    plt.ylabel('Total Quantity Sold')
    plt.title('Total Items Sold per Week')
    plt.show()

    # Additional exploratory analysis 1: Plot the total sales per year
    total_sales_per_year = sales_array.sum(axis=(1, 2))
    years = range(sales_data['year'].min(), sales_data['year'].max() + 1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(years, total_sales_per_year)
    plt.xlabel('Year')
    plt.ylabel('Total Quantity Sold')
    plt.title('Total Sales per Year')
    plt.xticks(years)
    plt.show()

    # Additional exploratory analysis 2: Plot the seasonal trend of total sales
    weekly_sales = sales_array.sum(axis=(0, 2))
    weeks = range(1, len(weekly_sales) + 1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(weeks, weekly_sales)
    plt.xlabel('Week')
    plt.ylabel('Total Quantity Sold')
    plt.title('Seasonal Trend of Total Sales')
    plt.show()

def main():
    # Read the dataset into a DataFrame
    df = pd.read_csv('../grocery_data/groceries_dataset_original.csv')

    # Check if products.csv exists, otherwise create it
    if not os.path.exists('products.csv'):
        # Get the unique item descriptions and assign them product IDs
        product_names = df['itemDescription'].unique()
        product_ids = range(1, len(product_names) + 1)

        # Create a new DataFrame with product IDs and names
        products_df = pd.DataFrame({'product_id': product_ids, 'product_name': product_names})

        # Save the products DataFrame to a new CSV file
        products_df.to_csv('products.csv', index=False)
    else:
        # Load the existing products.csv
        products_df = pd.read_csv('products.csv')

    # Check if sales_data.csv exists, otherwise create it
    if not os.path.exists('sales_data.csv'):
        # Convert the date column to datetime format
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

        # Extract the year and week from the date column
        df['year'] = df['Date'].dt.year
        df['week'] = df['Date'].dt.isocalendar().week

        # Merge the original dataset with the products DataFrame to get the product IDs
        merged_df = pd.merge(df, products_df, left_on='itemDescription', right_on='product_name')

        # Group by year, week, and product_id, and sum the quantities
        sales_data = merged_df.groupby(['year', 'week', 'product_id']).size().reset_index(name='quantity')

        # Save the sales data to a new CSV file
        sales_data.to_csv('sales_data.csv', index=False)
    else:
        # Load the existing sales_data.csv
        sales_data = pd.read_csv('sales_data.csv')

    # Check if sales_array.npy exists, otherwise create it
    if not os.path.exists('sales_array.npy'):
        # Convert the sales data to a 3D numpy array
        num_years = sales_data['year'].max() - sales_data['year'].min() + 1
        num_weeks = sales_data['week'].max()
        num_products = products_df['product_id'].max()

        # Initialize the 3D array with zeros
        sales_array = np.zeros((num_years, num_weeks, num_products))

        # Fill the array with the quantity sold for each year, week, and product_id
        for _, row in sales_data.iterrows():
            year_index = row['year'] - sales_data['year'].min()
            week_index = row['week'] - 1
            product_index = row['product_id'] - 1
            sales_array[year_index, week_index, product_index] = row['quantity']

        # Save the sales_array to a .npy binary file
        np.save('sales_array.npy', sales_array)
    else:
        # Load the existing sales_array.npy
        sales_array = np.load('sales_array.npy')

    print(sales_array)
    print(sales_array.shape)

    explore(sales_array, sales_data, products_df)

if __name__ == '__main__':
    main()