import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import webbrowser

# Read the CSV file
df = pd.read_csv("cases.csv")

# Function str of int to int
def convert_listings(listings_str):
    if isinstance(listings_str, int) or isinstance(listings_str, float):
        return listings_str
    try:
        if ',' in listings_str:
            listings_str = listings_str.replace(',', '')
        return int(listings_str)
    except ValueError:
        if ',' in listings_str:
            listings_str = listings_str.replace(',', '')
        return float(listings_str)

df['Listings'] = df['Listings'].apply(convert_listings)
df['Price'] = df['Price'].apply(convert_listings)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

exchange_rate_cad_to_php = 41.82

php_prices = df[df['Currency'] == 'P']['Price']
cad_prices = php_prices / exchange_rate_cad_to_php
df.loc[df['Currency'] == 'P', 'Price'] = cad_prices

grouped = df.groupby(['Item Name', 'Currency', 'Timestamp']).agg({'Price': 'mean', 'Listings': 'sum'}).reset_index()
grouped['Listings Change'] = grouped.groupby(['Item Name', 'Currency'])['Listings'].diff()


# Calculate the latest CAD and P prices for each item
latest_prices = grouped.groupby(['Item Name', 'Currency'])['Price'].last().unstack().reset_index()
latest_prices['Arbitrage'] = latest_prices['CDN'] #- latest_prices['P']

# Sort the items by the biggest decrease in listings
sorted_items = grouped.groupby(['Item Name', 'Currency'])['Listings Change'].last().unstack().reset_index()
sorted_items['Listings Decrease'] = sorted_items['CDN'] #- sorted_items['P']
sorted_items = sorted_items.sort_values(by='Listings Decrease', ascending=False)[['Item Name', 'Listings Decrease']]
#sorted_items = grouped

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
index = 0

def update_plot(index):
    item_name = sorted_items.iloc[index]['Item Name']
    group_data = grouped[grouped['Item Name'] == item_name]
    ax1.clear()
    legend_labels = []
    currencies = group_data['Currency'].unique()
    for currency in currencies:
        currency_data = group_data[group_data['Currency'] == currency]
        ax1.plot(currency_data['Timestamp'], currency_data['Price'], label=f'Price ({currency})', marker='o')
        legend_labels.append(f'Price ({currency})')
    ax1.set_ylabel('Price')
    ax1.set_title(f'{item_name} - Price')
    ax1.legend(legend_labels)
    ax1.grid()
    ax1.tick_params(axis='x', rotation=45)
    ax2.clear()

    # Separate the lines for each currency
    for currency in currencies:
        currency_data = group_data[group_data['Currency'] == currency]
        ax2.plot(currency_data['Timestamp'], currency_data['Listings'], label=f'Listings ({currency})', marker='x')

    ax2.set_ylabel('Listings')
    ax2.set_title(f'{item_name} - Listings')
    ax2.legend()
    ax2.grid()
    ax2.tick_params(axis='x', rotation=45)
    plt.tight_layout()


def next_item(event):
    global index
    index = (index + 1) % len(sorted_items)
    update_plot(index)
    fig.canvas.draw()

def prev_item(event):
    global index
    index = (index - 1) % len(sorted_items)
    update_plot(index)
    fig.canvas.draw()

def open_link(event):
    item_name = sorted_items.iloc[index]['Item Name']
    url = f'https://steamcommunity.com/market/listings/730/{item_name}/CAD'
    webbrowser.open(url)

next_button = plt.axes([0.85, 0.02, 0.1, 0.05])
prev_button = plt.axes([0.72, 0.02, 0.1, 0.05])
next_button = plt.Button(next_button, 'Next')
prev_button = plt.Button(prev_button, 'Previous')
next_button.on_clicked(next_item)
prev_button.on_clicked(prev_item)

link_button = plt.axes([0.72, 0.08, 0.23, 0.05])
link_button = Button(link_button, 'Open Link')
link_button.on_clicked(open_link)

update_plot(index)
plt.show()
