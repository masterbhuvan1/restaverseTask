import sys
import pandas as pd
import requests


def fetch_menu_data(restaurant_id):
    """
    fetches the menu data for a specific restaurant using the Swiggy API.

    parameters:
    restaurant_id (str): Unique identifier for the restaurant.


    """

    api_url = f"https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat=18.56&lng=73.95&restaurantId={restaurant_id}"


    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Cookie": "__SW=reIzUIUpxKUQOazMLjKazOFhd1CKeg8o;  _is_logged_in=;  ",
        "If-None-Match": 'W/"3b90b-lEcMpD8OyTxSEolMlPFQTwg4uyI"',
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Opera";v="107", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
    }

    # sending the GET request to the API
    response = requests.get(api_url, headers=headers)

    # check if the response status is successful (200 OK)
    if response.status_code == 200:
        return response.json()  # Return the parsed JSON data
    else:
        print(f"Failed to fetch menu data for restaurant ID {restaurant_id}")
        return None


def extract_menu_items(menu_data):
    """
    extracts relevant details from the menu data.

    parameters:
    - menu_data (dict): The JSON response from the API.

    returns:
    - list: A list of dictionaries, each containing details about a menu item.
    """
    items = []  # initialize a list
    if 'data' in menu_data and 'cards' in menu_data['data']:
        # iterate through each card in the data to extract menu items
        for card_wrapper in menu_data['data']['cards']:
            if 'groupedCard' in card_wrapper:
                card_group = card_wrapper['groupedCard']['cardGroupMap']['REGULAR']['cards']
                for card in card_group:
                    item_info = card['card']['card']
                    for itemCard in item_info.get('itemCards', []):
                        item = itemCard['card']['info']
                        item_dict = {
                            'Item Name': item.get('name', ''),
                            'Category': item.get('category', ''),
                            'Description': item.get('description', ''),
                            'Price': item.get('price', 0) / 100,  # Convert price to a more standard format if needed
                            'Veg Classifier': item.get('itemAttribute', {}).get('vegClassifier', 'N/A'),
                            'Portion Size': item.get('itemAttribute', {}).get('portionSize', 'N/A'),
                            'Rating': item.get('ratings', {}).get('aggregatedRating', {}).get('rating', 'N/A'),
                        }
                        if 'addons' in item:
                            addons_list = [f"{choice['name']} ({choice['price'] / 100})" for addon in item['addons'] for
                                           choice in addon['choices']]
                            item_dict['Addons'] = '; '.join(addons_list)
                        items.append(item_dict)
    return items


def save_to_csv(menu_items, output_file):
    """
    saves the extracted menu items into a CSV file.

    parameters
    menu_items (list)= List of dictionaries with menu item details.
    output_file (str)= Path to the output CSV file.
    """
    df = pd.DataFrame(menu_items)  # Convert the list of dictionaries to a DataFrame
    df.to_csv(output_file, index=False)  # Save the DataFrame as a CSV file
    print(f"Menu data saved to {output_file}")


def main():

    # Ensure the script is called with the correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: python swiggy_menu_extractor.py <restaurant_id> <output_file.csv>")
        sys.exit(1)

    # extract command-line arguments
    restaurant_id = sys.argv[1]
    output_file = sys.argv[2]

    # fetch, extract, and save the menu data
    menu_data = fetch_menu_data(restaurant_id)
    if menu_data:
        menu_items = extract_menu_items(menu_data)
        if menu_items:
            save_to_csv(menu_items, output_file)


if __name__ == "__main__":
    main()
