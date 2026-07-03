from flask import Flask
from pymongo import MongoClient
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("fr_core_news_sm")

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["db_mongo"]
collection = db["off_backup"]

from langdetect import detect

def get_valid_category(doc):
    if "categories" not in doc or not isinstance(doc["categories"], str):
        return None

    for cat in doc["categories"].split(","):
        cat_clean = cat.strip().lower()
        if not cat_clean or cat_clean.isdigit():
            continue
        try:
            lang = detect(cat_clean)
            if lang in ["fr", "en"]:
                return cat_clean
        except:
            continue
    return None


def extract_keywords(limit=50):
    keywords_list = []
    for doc in collection.find({"_keywords.0": {"$exists": True}}).limit(limit):
        first_kw = doc["_keywords"][0]
        if first_kw.isalpha():  # ou ta logique de filtre
            keywords_list.append(first_kw.lower())
    return keywords_list


# Mapping simple basé sur mots-clés
category_map = {
    "fruit": {"high": "Vegetables and Fruit", "mid": "Fruit", "low": "Fruit", "code": "1120"},
    "dark green vegetables": {"high": "Vegetables and Fruit", "mid": "Vegetables", "low": "Dark green vegetables", "code": "1210"},
    "deep yellow or orange vegetables": {"high": "Vegetables and Fruit", "mid": "Vegetables", "low": "Deep yellow or orange vegetables", "code": "1220"},
    "Starchy vegetables": {"high": "Vegetables and Fruit", "mid": "Vegetables", "low": "Starchy vegetables", "code": "1230"},
    "other vegetables": {"high": "Vegetables and Fruit", "mid": "Vegetables", "low": "Other vegetables", "code": "1240"},
    "whole grains": {"high": "Whole Grain, whole grain foods and whole wheat foods", "mid": "Whole grains (100%)", "low": "Whole grains (100%)", "code": "2100"},
    "whole grain foods": {"high": "Whole Grain, whole grain foods and whole wheat foods", "mid": "Whole grain and whole wheat foods", "low": "Whole grain foods", "code": "2210"},
    "whole wheat foods": {"high": "Whole Grain, whole grain foods and whole wheat foods", "mid": "Whole grain and whole wheat foods", "low": "Whole wheat foods", "code": "2220"},
    "plant-based yogurts": {"high": "Protein foods", "mid": "Plant-based protein foods", "low": "Plant-based yogurts", "code": "3200"},
    "fortified plant-based cheeses": {"high": "Protein foods", "mid": "Plant-based protein foods", "low": "Fortified plant-based cheeses", "code": "3300"},
    "legumes": {"high": "Protein foods", "mid": "Plant-based protein foods", "low": "Legumes", "code": "3400"},
    "simulated meats": {"high": "Protein foods", "mid": "Plant-based protein foods", "low": "Simulated meats", "code": "3500"},
    "nuts and seeds": {"high": "Protein foods", "mid": "Plant-based protein foods", "low": "Nuts and seeds", "code": "3600"},
    "other plant-based foods": {"high": "Protein foods", "mid": "Plant-based protein foods", "low": "Other plant-based foods (sufficient protein)", "code": "3700"},
    "yogurts and kefir": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Yogurts and kefir", "code": "4200"},
    "cheeses": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Cheeses", "code": "4300"},
    "other milk-based foods": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Other milk-based foods", "code": "4400"},
    "red meats": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Red meats", "code": "4500"},
    "game meats": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Game meats", "code": "4600"},
    "poultry and wild birds": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Poultry and wild birds", "code": "4700"},
    "eggs": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Eggs", "code": "4710"},
    "fish and shellfish": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Fish and shellfish", "code": "4800"},
    "organ meats": {"high": "Protein foods", "mid": "Animal-based protein foods", "low": "Organ meats", "code": "4900"},
    "water": {"high": "Beverages", "mid": "Beverages", "low": "Water", "code": "5110"},
    "Forti plant-b bev (high protein)": {"high": "Beverages", "mid": "Beverages", "low": "Fortified plant-based beverages (sufficient protein)", "code": "5120"},
    "Non-Forti plant-b bev (high protein)": {"high": "Beverages", "mid": "Beverages", "low": "Non-Fortified plant-based beverages (sufficient protein)", "code": "5130"},
    "Forti plant-b bev (low protein)": {"high": "Beverages", "mid": "Beverages", "low": "Fortified plant-based beverages (insufficient protein)", "code": "5140"},
    "milks": {"high": "Beverages", "mid": "Beverages", "low": "Milks", "code": "5150"},
    "fruit juice": {"high": "Beverages", "mid": "Beverages", "low": "Fruit juice", "code": "5160"},
    "vegetable juice": {"high": "Beverages", "mid": "Beverages", "low": "Vegetable juice", "code": "5170"},
    "other beverages": {"high": "Beverages", "mid": "Beverages", "low": "Other beverages", "code": "5180"},
    "Other plant-b foods (low protein)": {"high": "Other foods", "mid": "Other plant-based foods (insufficient protein)", "low": "Other plant-based foods (insufficient protein)", "code": "6100"},
    "condiments": {"high": "Other foods", "mid": "Condiments, sauces and lower fat dressings", "low": "Condiments, sauces and lower fat dressings", "code": "6200"},
    "snack foods": {"high": "Other foods", "mid": "Other snack foods", "low": "Other snack foods", "code": "6300"},
    "high sugar foods": {"high": "Other foods", "mid": "Higher sugar and/or higher fat foods", "low": "Higher sugar and/or higher fat foods", "code": "6400"},
    "enriched grain foods": {"high": "Other foods", "mid": "Non-whole grain and non-whole wheat foods", "low": "Enriched non-whole grain and non-whole wheat foods", "code": "6510"},
    "unenriched grain foods": {"high": "Other foods", "mid": "Non-whole grain and non-whole wheat foods", "low": "Unenriched non-whole grain and non-whole wheat foods", "code": "6520"},
    "processed meats": {"high": "Other foods", "mid": "Processed meats", "low": "Processed meats", "code": "6600"},
    "unsaturated": {"high": "Fats and oils", "mid": "Unsaturated fats and oils", "low": "Unsaturated fats and oils", "code": "7110"},
    "saturated": {"high": "Fats and oils", "mid": "Saturated and trans fats and oils", "low": "Saturated and trans fats and oils", "code": "7120"},
    "baby foods": {"high": "Baby and toddler foods", "mid": "Baby and toddler foods", "low": "Baby and toddler foods", "code": "8100"},
    "protein shake": {"high": "Other foods that are not classified", "mid": "Meal replacements and supplements", "low": "Meal replacements and supplements", "code": "8200"},
    "alcoholic beverages ": {"high": "Other foods that are not classified", "mid": "Alcoholic beverages", "low": "Alcoholic beverages", "code": "8300"},
    "cnf recipes": {"high": "Other foods that are not classified", "mid": "CNF Recipes", "low": "CNF Recipes", "code": "8400"},
    "misc foods": {"high": "Other foods that are not classified", "mid": "Miscellaneous foods", "low": "Miscellaneous foods", "code": "8500"},
    "unclassified": {"high": "Foods and beverages missing data for classification", "mid": "Unclassified foods and beverages", "low": "Unclassified foods and beverages", "code": "9990"}
}




