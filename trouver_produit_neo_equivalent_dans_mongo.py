import os

from itertools import chain
from rapidfuzz import fuzz
from pymongo import MongoClient
from transformers import MarianMTModel, MarianTokenizer

mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = 27017
mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"

mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=20000)
mongo_db_names = mongo_client.list_database_names()
mongo_db = mongo_client["db_mongo"]

model_name = "Helsinki-NLP/opus-mt-fr-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# depend de nos collections et si changement alors doit corriger les requetes
fdc = mongo_db["fdc"]
fcne = mongo_db["fcne"]
off = mongo_db["off"]


def translate(text):
    tokens = tokenizer([text], return_tensors="pt", padding=True)
    output = model.generate(**tokens)
    return tokenizer.decode(output[0], skip_special_tokens=True)


def trouver_liste_mongo(nom_produit_neo):
    product_name = nom_produit_neo["nom"]
    threshold = 80  # similarity threshold (0–100)
    liste = []
    nom_produit = translate(product_name)
    product_liste = chain(
        off.find({}, {"product_name": 1}),
        fdc.find({}, {"product_name": 1}),
    )
    for doc in product_liste:
        s = str(doc.get("product_name", ""))
        score = fuzz.ratio(str(nom_produit), s)
        if score >= threshold:
            id = doc.get("_id", "")
            liste.append((id, score))
    # trier liste selon score
    return liste
