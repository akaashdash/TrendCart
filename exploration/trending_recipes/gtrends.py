import requests
from pytrends.request import TrendReq
from spoonacular import API
import json
import time
import os
from brave import Brave
import pandas as pd
from difflib import SequenceMatcher

# Set up Spoonacular API client
spoonacular_api_key = "fc8b842b8b3149f98b9afed693af6aa1"
spoonacular_client = API(spoonacular_api_key)

# Set up Google Trends API client
pytrends = TrendReq()

brave = Brave('BSADtmC-nKi9ZSEhxeF-4Xui1ukH-AT')

def get_trending_recipes(timeframe="now 7-d"):
    """
    Retrieve rapidly rising recipe trends from Google Trends.
    
    Args:
        timeframe (str): The time range to analyze trends. Default is the past 7 days.
        
    Returns:
        list: A list of tuples containing the trending recipe keyword and its percentage change.
    """
    kw_list = ["recipe"]
    pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo="US")
    related_queries = pytrends.related_queries()
    
    trending_recipes = []
    rising_trends = related_queries["recipe"]["rising"]
    for index, row in rising_trends.iterrows():
        keyword = row["query"]
        percentage_change = row["value"]
        trending_recipes.append((keyword, percentage_change))
        
    return trending_recipes

def get_recipe_ingredients(recipe_name):
    """
    Extract ingredients from a recipe using the Spoonacular API.
    
    Args:
        recipe_name (str): The name of the recipe.
        
    Returns:
        list: A list of ingredients for the recipe.
    """
    try:
        # Check if the recipe exists in Spoonacular
        search_response = spoonacular_client.search_recipes_complex(recipe_name)
        time.sleep(1)
        if search_response.json()["totalResults"] > 0:
            # If the recipe exists, retrieve its ingredients directly
            recipe_id = search_response.json()["results"][0]["id"]
            ingredients_response = spoonacular_client.get_analyzed_recipe_instructions(recipe_id)
            time.sleep(1)
            steps = ingredients_response.json()[0]["steps"]
            ingredients = []
            for step in steps:
                ingredients.extend(step["ingredients"])
            ingredient_names = [ingredient["name"] for ingredient in ingredients]
            return ingredient_names
        else:
            pass
            # If the recipe doesn't exist, search for a website with the recipe using Brave Search API
            search_query = f"{recipe_name} recipe"
            search_response = brave.search(q=search_query, count=10).web_results
            if len(search_response) > 0:
                recipe_url = search_response[0]["url"]
                
                # Extract ingredients from the recipe URL using Spoonacular
                response = spoonacular_client.extract_recipe_from_website(recipe_url)
                time.sleep(1)
                ingredients = response.json()["extendedIngredients"]
                ingredient_names = [ingredient["name"] for ingredient in ingredients]
                return ingredient_names
    except Exception as e:
        print(f"Error retrieving ingredients for {recipe_name}: {str(e)}")
        return []

def save_to_file(data, filename):
    """
    Save data to a JSON file.
    
    Args:
        data (dict): The data to be saved.
        filename (str): The name of the file to save the data to.
    """
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_products(filename):
    df = pd.read_csv(filename)
    products = dict(zip(df['product_name'], df['product_id']))
    return products

def find_closest_product(ingredient, products):
    max_ratio = 0
    closest_product = None
    for product_name, product_id in products.items():
        ratio = SequenceMatcher(None, ingredient.lower(), product_name.lower()).ratio()
        if ratio > max_ratio:
            max_ratio = ratio
            closest_product = product_id
    return closest_product

def main():
    trending_recipe_file = "trending_recipes.json"
    if os.path.exists(trending_recipe_file):
        with open(trending_recipe_file) as f:
            data = json.load(f)
        trending_recipes = data["trending_recipes"]
    else:
        # Get trending recipe keywords and their percentage change from Google Trends
        trending_recipes = get_trending_recipes()
        # Save trending recipes to a file
        trending_recipes_data = {"trending_recipes": trending_recipes}
        save_to_file(trending_recipes_data, trending_recipe_file)

    recipe_ingredients_file = "recipe_ingredients.json"
    if os.path.exists(recipe_ingredients_file):
        with open(recipe_ingredients_file) as f:
            data = json.load(f)
        recipe_ingredients = data["recipe_ingredients"]
    else:
        # Extract ingredients for each trending recipe
        recipe_ingredients = {}
        for recipe, _ in trending_recipes:
            ingredients = get_recipe_ingredients(recipe)
            recipe_ingredients[recipe] = ingredients

        # Save recipe ingredients to a file
        recipe_ingredients_data = {"recipe_ingredients": recipe_ingredients}
        save_to_file(recipe_ingredients_data, recipe_ingredients_file)

    """
    # Load products from CSV file using pandas
    products = load_products("../instacart_data/products.csv")

    # Find the closest product for each ingredient and save with product ID
    recipe_product_ingredients = []
    for recipe, ingredients in recipe_ingredients.items():
        product_ingredients = set()
        for ingredient in ingredients:
            closest_product = find_closest_product(ingredient, products)
            if closest_product:
                product_ingredients.add(closest_product)
        recipe_product_ingredients.append({"recipe": recipe, "ingredients": list(product_ingredients)})

    # Save the recipes and their ingredients as product IDs to a new file
    recipe_product_ingredients_file = "recipe_product_ingredients.json"
    save_to_file(recipe_product_ingredients, recipe_product_ingredients_file)

    # Print the trending recipes and their ingredients (with product IDs)
    for recipe_data in recipe_product_ingredients:
        recipe = recipe_data["recipe"]
        product_ingredients = recipe_data["ingredients"]
        print(f"Recipe: {recipe}")
        print("Ingredients (Product IDs):")
        for product_id in product_ingredients:
            print(f"- {product_id}")
        print()
    """

if __name__ == "__main__":
    main()