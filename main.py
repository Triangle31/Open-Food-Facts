import os
import random
import logging
from flask import Flask, jsonify, request, Response
from pymongo import MongoClient, UpdateOne
from neo4j import GraphDatabase
from trouver_food_categories import trouver_categories
from food_classification import get_valid_category, category_map, collection
from rename_fdc import rename_food_groups_fdc
from trouver_produit_neo_equivalent_dans_mongo import trouver_liste_mongo
from collections import Counter

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = 27017
mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"

mongo_client = MongoClient(
    mongo_uri,
    connectTimeoutMS=60000,
    serverSelectionTimeoutMS=60000,
    socketTimeoutMS=60000,
)

mongo_db_names = mongo_client.list_database_names()
mongo_db_off = mongo_client["off"]
mongo_db_fdc = mongo_client["fdc"]
# depend de nos collections et si changement alors doit corriger les requetes
fdc = mongo_db_fdc["fdc"]
off = mongo_db_off["off"]

neo4j_uri = "bolt://db-neo4j:7687"
neo4j_user = "neo4j"
neo4j_pass = "equipe23"

neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))


def get_types_neo():
    with neo4j_driver.session() as session:
        result = session.run("MATCH (t:TypeDePlat) RETURN t.nom AS type")
        return [record["type"] for record in result]


types_neo = get_types_neo()


@app.route("/")
def home():
    return "Flask + PyMongo ready!"


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return {"nomApplication": "FoodFacts"}


@app.route("/extracted_data", methods=["GET"])
def extracted_data():
    neo4j_session = neo4j_driver.session()
    nb_products_off = off.count_documents({})
    nb_products_fdc = fdc.count_documents({})
    nb_products_off_code_start_200 = off.count_documents({"code": {"$regex": "^200"}})
    nb_products_off_code_start_999 = off.count_documents({"code": {"$regex": "^999"}})

    nb_products_off_base = off.count_documents({"nova_group": 1})
    nb_products_fdc_base = fdc.count_documents({"nova_group": 1})

    nb_produits_alimentaires_scannes: int = (nb_products_off + nb_products_fdc) - (
        nb_products_off_code_start_200
        + nb_products_off_code_start_999
        + nb_products_fdc_base
    )
    nb_produits_alimentaires_de_bases: int = nb_products_off_base + nb_products_fdc_base

    recette_query = neo4j_session.run(
        "MATCH(r:Recette) RETURN COUNT(r) AS nbRecettesCuisine", {}
    )
    nb_recettes_cuisine = list(recette_query.single().values())[0]
    neo4j_session.close()
    return {
        "ndbProduitsAlimentairesScannes": nb_produits_alimentaires_scannes,
        "nbProduitsAlimentairesDeBases": nb_produits_alimentaires_de_bases,
        "nbRecettesCuisine": nb_recettes_cuisine,
    }


@app.route("/transformed_data", methods=["GET"])
def transformed_data():

    nbNutriScore = off.count_documents(
        {"nutriscore_grade": {"$regex": "^[a-e]$", "$options": "i"}}
    )
    nbNova = off.count_documents({"nova_group": {"$gte": 1, "$lte": 4}})
    nbEcoScore = off.count_documents(
        {"ecoscore_grade": {"$regex": "^[a-e]$", "$options": "i"}}
    )
    nb_1120: int = off.count_documents(
        {"category_code_ca": "1120"}
    ) + fdc.count_documents({"category_code_ca": "1120"})
    nb_1210: int = off.count_documents(
        {"category_code_ca": "1210"}
    ) + fdc.count_documents({"category_code_ca": "1210"})
    nb_1220: int = off.count_documents(
        {"category_code_ca": "1220"}
    ) + fdc.count_documents({"category_code_ca": "1220"})
    nb_1230: int = off.count_documents(
        {"category_code_ca": "1230"}
    ) + fdc.count_documents({"category_code_ca": "1230"})
    nb_1240: int = off.count_documents(
        {"category_code_ca": "1240"}
    ) + fdc.count_documents({"category_code_ca": "1240"})
    nb_2100: int = off.count_documents(
        {"category_code_ca": "2100"}
    ) + fdc.count_documents({"category_code_ca": "2100"})
    nb_2210: int = off.count_documents(
        {"category_code_ca": "2210"}
    ) + fdc.count_documents({"category_code_ca": "2210"})
    nb_2220: int = off.count_documents(
        {"category_code_ca": "2220"}
    ) + fdc.count_documents({"category_code_ca": "2220"})
    nb_3200: int = off.count_documents(
        {"category_code_ca": "3200"}
    ) + fdc.count_documents({"category_code_ca": "3200"})
    nb_3300: int = off.count_documents(
        {"category_code_ca": "3300"}
    ) + fdc.count_documents({"category_code_ca": "3300"})
    nb_3400: int = off.count_documents(
        {"category_code_ca": "3400"}
    ) + fdc.count_documents({"category_code_ca": "3400"})
    nb_3500: int = off.count_documents(
        {"category_code_ca": "3500"}
    ) + fdc.count_documents({"category_code_ca": "3500"})
    nb_3600: int = off.count_documents(
        {"category_code_ca": "3600"}
    ) + fdc.count_documents({"category_code_ca": "3600"})
    nb_3700: int = off.count_documents(
        {"category_code_ca": "3700"}
    ) + fdc.count_documents({"category_code_ca": "3700"})
    nb_4200: int = off.count_documents(
        {"category_code_ca": "4200"}
    ) + fdc.count_documents({"category_code_ca": "4200"})
    nb_4300: int = off.count_documents(
        {"category_code_ca": "4300"}
    ) + fdc.count_documents({"category_code_ca": "4300"})
    nb_4400: int = off.count_documents(
        {"category_code_ca": "4400"}
    ) + fdc.count_documents({"category_code_ca": "4400"})
    nb_4500: int = off.count_documents(
        {"category_code_ca": "4500"}
    ) + fdc.count_documents({"category_code_ca": "4500"})
    nb_4600: int = off.count_documents(
        {"category_code_ca": "4600"}
    ) + fdc.count_documents({"category_code_ca": "4600"})
    nb_4700: int = off.count_documents(
        {"category_code_ca": "4700"}
    ) + fdc.count_documents({"category_code_ca": "4700"})
    nb_4710: int = off.count_documents(
        {"category_code_ca": "4710"}
    ) + fdc.count_documents({"category_code_ca": "4710"})
    nb_4800: int = off.count_documents(
        {"category_code_ca": "4800"}
    ) + fdc.count_documents({"category_code_ca": "4800"})
    nb_4900: int = off.count_documents(
        {"category_code_ca": "4900"}
    ) + fdc.count_documents({"category_code_ca": "4900"})
    nb_5110: int = off.count_documents(
        {"category_code_ca": "5110"}
    ) + fdc.count_documents({"category_code_ca": "5110"})
    nb_5120: int = off.count_documents(
        {"category_code_ca": "5120"}
    ) + fdc.count_documents({"category_code_ca": "5120"})
    nb_5130: int = off.count_documents(
        {"category_code_ca": "5130"}
    ) + fdc.count_documents({"category_code_ca": "5130"})
    nb_5140: int = off.count_documents(
        {"category_code_ca": "5140"}
    ) + fdc.count_documents({"category_code_ca": "5140"})
    nb_5150: int = off.count_documents(
        {"category_code_ca": "5150"}
    ) + fdc.count_documents({"category_code_ca": "5150"})
    nb_5160: int = off.count_documents(
        {"category_code_ca": "5160"}
    ) + fdc.count_documents({"category_code_ca": "5160"})
    nb_5170: int = off.count_documents(
        {"category_code_ca": "5170"}
    ) + fdc.count_documents({"category_code_ca": "5170"})
    nb_5180: int = off.count_documents(
        {"category_code_ca": "5180"}
    ) + fdc.count_documents({"category_code_ca": "5180"})
    nb_6100: int = off.count_documents(
        {"category_code_ca": "6100"}
    ) + fdc.count_documents({"category_code_ca": "6100"})
    nb_6200: int = off.count_documents(
        {"category_code_ca": "6200"}
    ) + fdc.count_documents({"category_code_ca": "6200"})
    nb_6300: int = off.count_documents(
        {"category_code_ca": "6300"}
    ) + fdc.count_documents({"category_code_ca": "6300"})
    nb_6400: int = off.count_documents(
        {"category_code_ca": "6400"}
    ) + fdc.count_documents({"category_code_ca": "6400"})
    nb_6510: int = off.count_documents(
        {"category_code_ca": "6510"}
    ) + fdc.count_documents({"category_code_ca": "6510"})
    nb_6520: int = off.count_documents(
        {"category_code_ca": "6520"}
    ) + fdc.count_documents({"category_code_ca": "6520"})
    nb_6600: int = off.count_documents(
        {"category_code_ca": "6600"}
    ) + fdc.count_documents({"category_code_ca": "6600"})
    nb_7110: int = off.count_documents(
        {"category_code_ca": "7110"}
    ) + fdc.count_documents({"category_code_ca": "7110"})
    nb_7120: int = off.count_documents(
        {"category_code_ca": "7120"}
    ) + fdc.count_documents({"category_code_ca": "7120"})
    nb_8100: int = off.count_documents(
        {"category_code_ca": "8100"}
    ) + fdc.count_documents({"category_code_ca": "8100"})
    nb_8200: int = off.count_documents(
        {"category_code_ca": "8200"}
    ) + fdc.count_documents({"category_code_ca": "8200"})
    nb_8300: int = off.count_documents(
        {"category_code_ca": "8300"}
    ) + fdc.count_documents({"category_code_ca": "8300"})
    nb_8500: int = off.count_documents(
        {"category_code_ca": "8500"}
    ) + fdc.count_documents({"category_code_ca": "8500"})
    nb_9990: int = off.count_documents(
        {"category_code_ca": "9990"}
    ) + fdc.count_documents({"category_code_ca": "9990"})

    categories_dict_return = {
        "1120 - Fruits": nb_1120,
        "1210 - Légumes vert foncé": nb_1210,
        "1220 - Légumes jaune foncé ou orange": nb_1220,
        "1230 - Légumes féculents": nb_1230,
        "1240 - Autres légumes": nb_1240,
        "2100 - Grains entiers (100%)": nb_2100,
        "2210 - Aliments à grains entiers": nb_2210,
        "2220 - Aliments de blé entier": nb_2220,
        "3200 - Yogourts végétaux": nb_3200,
        "3300 - Fromages végétaux enrichis (qui contiennent suffisamment de protéines)": nb_3300,
        "3400 - Légumineuses": nb_3400,
        "3500 - Similis-viandes": nb_3500,
        "3600 - Noix et graines": nb_3600,
        "3700 - Autres aliments d'origine végétale (qui contiennent suffisamment de protéines)": nb_3700,
        "4200 - Yogourts et kéfir": nb_4200,
        "4300 - Fromages": nb_4300,
        "4400 - Autres aliments à base de lait": nb_4400,
        "4500 - Viandes rouges": nb_4500,
        "4600 - Viandes de gibier": nb_4600,
        "4700 - Volaille et oiseaux sauvages": nb_4700,
        "4710 - Oeufs": nb_4710,
        "4800 - Poisson et fruits de mer": nb_4800,
        "4900 - Abats": nb_4900,
        "5110 - Eau": nb_5110,
        "5120 - Boissons végétales enrichies (qui contiennent suffisamment de protéines)": nb_5120,
        "5130 - Boissons végétales non enrichies (qui contiennent suffisamment de protéines)": nb_5130,
        "5140 - Boissons végétales enrichies (qui ne contiennent pas suffisamment de protéines)": nb_5140,
        "5150 - Laits": nb_5150,
        "5160 - Jus de fruits": nb_5160,
        "5170 - Jus de légumes": nb_5170,
        "5180 - Autres boissons": nb_5180,
        "6100 - Autres aliments d’origine végétale (qui ne contiennent pas suffisamment de protéines)": nb_6100,
        "6200 - Condiments, sauces et vinaigrettes à faible teneur en matières grasses": nb_6200,
        "6300 - Autres grignotines": nb_6300,
        "6400 - Aliments à teneur plus élevée en sucre et/ou en gras": nb_6400,
        "6510 - Aliments enrichis qui ne sont pas à grains entiers et de blé entier": nb_6510,
        "6520 - Aliments non enrichis qui ne sont pas à grains entiers et de blé entier": nb_6520,
        "6600 - Viandes transformées": nb_6600,
        "7110 - Graisses et huiles non saturées": nb_7110,
        "7120 - Graisses et huiles saturées et trans": nb_7120,
        "8100 - Aliments pour bébés": nb_8100,
        "8200 - Substituts de repas et suppléments": nb_8200,
        "8300 - Boissons alcooliques": nb_8300,
        "8500 - Aliments divers (les ingrédients, les fines herbes, les épices, les bonbons sans sucre, les mélanges non préparés)": nb_8500,
        "9990 - Aliments et boissons non classés (en raison de données manquantes)": nb_9990,
    }

    return {
        "indicateursDeQualite": {
            "NutriScore": nbNutriScore,
            "Nova": nbNova,
            "EcoScore": nbEcoScore,
        },
        "categoriesProduitAlimentaire": categories_dict_return,
    }

@app.route("/readme", methods=["GET"])
def get_readme():
    if not os.path.exists("README.md"):
        return jsonify({"error": "README.md introuvable"}), 404

    with open("README.md", "r", encoding="utf-8") as file:
        content = file.read()

    return Response(content, mimetype="text/markdown")

@app.route("/type", methods=["GET"])
def types():
    neo4j_session = neo4j_driver.session()
    neo_query = neo4j_session.run(
        """
    MATCH(t:TypeDePlat) 
    RETURN t.nom AS type
    """
    )
    results = [record["type"] for record in neo_query]
    neo4j_session.close()
    return jsonify(results)


@app.route("/recette", methods=["POST", "GET"])
def recette():
    if request.method == "POST":
        data = request.get_json()
        types = data.get("type", [])
        types_accepte = [t for t in types if t in types_neo]
        neo4j_session = neo4j_driver.session()
        if types_accepte:
            random_skips = 0  # todo?
            neo_query = neo4j_session.run(
                """
            MATCH (r:Recette)-[:EST_DE_TYPE]->(t:TypeDePlat) 
            WHERE t.nom IN $type_accepte 
            WITH r, collect(DISTINCT t.nom) AS matched_types 
            WHERE size(matched_types) = size($type_accepte) 
            RETURN r {
                name: r.name,
                description: r.description2,
                ingredients: r.ingredients_bruts,
                instructions: r.instructions,
                portions: r.portions,
                temps_cuisson: r.temps_cuisson,
                temps_preparation: r.temps_preparation
            } AS recette
            SKIP $random_skips
            LIMIT 1
            """,
                type_accepte=types_accepte,
                random_skips=random_skips,
            )
            results = [record["recette"] for record in neo_query]
            neo4j_session.close()
            return jsonify({"recette": results})
        else:
            random_skips = random.randrange(100)
            neo_query = neo4j_session.run(
                """
            MATCH(r:Recette)                           
            RETURN r {
                name: r.name,
                description: r.description2,
                ingredients: r.ingredients_bruts,
                instructions: r.instructions,
                portions: r.portions,
                temps_cuisson: r.temps_cuisson,
                temps_preparation: r.temps_preparation                            
            } AS recette
            SKIP $random_skips 
            LIMIT 1
            """,
                random_skips=random_skips,
            )
            results = [record["recette"] for record in neo_query]
            neo4j_session.close()
            return jsonify({"recette": results})

    elif request.method == "GET":
        return {"noPOST": "noRECETTE"}


@app.route("/cuisiner", methods=["POST", "GET"])
def cuisiner():
    if request.method == "POST":
        data = request.get_json()
        nom_recette = data.get("recette", {}).get("nom", None)
        neo4j_session1 = neo4j_driver.session()
        ingredients_query = neo4j_session1.run(
            """
            MATCH (p:Produit)<-[UTILISE]-(:Recette {name: $nom_recette})
            RETURN DISTINCT p.nom AS ingredient
            """,
            nom_recette=nom_recette,
        )
        ingredients = [record["ingredient"] for record in ingredients_query]
        neo4j_session1.close()
        preference_marque = data.get("preferenceMarqueProduit", [""])
        liste_marques = [marque.lower() for marque in preference_marque]
        nutriscore = data.get("indicateursDeQualiteSuperieurA", {}).get(
            "NutriScore", None
        )
        novascore_str = data.get("indicateursDeQualiteSuperieurA", {}).get("Nova", None)

        if novascore_str.isdigit():
            novascore = int(novascore_str)
        ecoscore = data.get("indicateursDeQualiteSuperieurA", {}).get("EcoScore", None)
        liste_nutriscore = ["a", "b", "c", "d", "e"]
        liste_novascore = [1, 2, 3, 4]
        liste_ecoscore = ["a", "b", "c", "d", "e", "f"]

        neo4j_session = neo4j_driver.session()
        liste_all_recommendations = {}
        ingredient_counter = 1

        for ingredient in ingredients:
            liste_recomandation = []
            equivalent_query = neo4j_session.run(
                """
            MATCH(p:Produit)-[EQUIVALENT]->(m:MongoProduit) 
            WHERE p.nom CONTAINS $ingredient
            RETURN collect(DISTINCT m.mongo_id) AS mongo_ids                                     
            """,
                ingredient=ingredient,
            )
            mongo_ids = equivalent_query.single()["mongo_ids"]
            for mongo_id in mongo_ids:
                counter = 4
                produit_de_base = False
                current_equivalent = off.find_one({"_id": mongo_id})
                if not current_equivalent:
                    current_equivalent = fdc.find_one({"_id": mongo_id})
                if not current_equivalent:

                    continue

                current_product_name = current_equivalent.get("product_name", "")
                current_brand = current_equivalent.get("brands", "")
                current_novascore = current_equivalent.get("nova_group", 4)
                current_nutriscore = current_equivalent.get("nutriscore_grade", "e")
                current_ecoscore = current_equivalent.get("ecoscore_grade", "e")
                current_category = current_equivalent.get("category_ca", "")

                if (
                    len(liste_marques) > 0
                    and current_brand.lower() not in liste_marques
                ):
                    if not (len(liste_marques) == 1 and liste_marques[0] == ""):
                        continue
                if not novascore or (
                    novascore in liste_novascore and current_novascore > novascore
                ):
                    if current_novascore == 1:
                        produit_de_base = True
                    continue
                if (
                    nutriscore.lower() in liste_nutriscore
                    and current_nutriscore.lower() > nutriscore.lower()
                ):
                    continue
                if (
                    ecoscore.lower() in liste_ecoscore
                    and current_ecoscore.lower() > ecoscore.lower()
                ):
                    continue

                current_equivalent_info = {
                    "nomProduit": current_product_name,
                    "marque": current_brand,
                    "indicateurDeQualite": {
                        "nutriscore_grade": current_nutriscore,
                        "Nova_group": current_novascore,
                        "ecoscore_grade": current_ecoscore,
                    },
                    "categorie": current_category,
                    "produitDeBase": produit_de_base,
                }

                liste_recomandation.append([current_equivalent_info, counter])

            liste_recomandation_trie = sorted(
                liste_recomandation, key=lambda x: x[1], reverse=True
            )

            liste_formate_trie = [
                {f"recommandationProduit{indx+1:02d}": item[0]}
                for indx, item in enumerate(liste_recomandation_trie)
            ]

            liste_all_recommendations[
                f"ingredientDeLaRecette{ingredient_counter:02d}"
            ] = liste_formate_trie
            ingredient_counter += 1

        neo4j_session.close()
        return jsonify(liste_all_recommendations)
    elif request.method == "GET":
        return {"noPOST": "noCUISINER"}


@app.route("/off_categorisation", methods=["GET"])
def off_categorisation():
    cursor = off.find({"category_ca": {"$exists": False}}).limit(100000)
    operations = []
    for product in cursor:
        new_fields = trouver_categories(product)
        if new_fields:
            operations.append(UpdateOne({"_id": product["_id"]}, {"$set": new_fields}))

    if operations:
        off.bulk_write(operations)
    return {"results": {}}


@app.route("/fdc_categorisation", methods=["GET"])
def fdc_categorisation():
    rename_food_groups_fdc(mongo_uri, mongo_db, fdc)
    return {"results": {}}


@app.route("/map_mexico_categories", methods=["POST"])
def map_mexico_categories():
    limit = int(request.args.get("limit", 8249))
    updated = []

    # regroupement lexical simplifié (extrait du JSON)
    lexical_map = {
        "puré": "fruit",
        "puré de tomate natural": "fruit",
        "purées": "fruit",
        "fruit-juices": "fruit juice",
        "orange-juices": "fruit juice",
        "squeezed-orange-juices": "fruit juice",
        "pure apple compotes": "fruit",
        "chiles": "other vegetables",
        "chiles chipotles": "other vegetables",
        "chiles en conserva": "other vegetables",
        "chiles en vinagre": "other vegetables",
        "tomates": "other vegetables",
        "vegetable juice": "vegetable juice",
        "aromatic-herbs": "other vegetables",
        "spice-mix": "other vegetables",
        "pickles - relishes - chutneys - olives variety packs": "other vegetables",
        "sweet potato crisps": "Starchy vegetables",
        "corn flatbreads": "Starchy vegetables",
        "corn-chips": "Starchy vegetables",
        "espaguetis": "Starchy vegetables",
        "fusilli": "Starchy vegetables",
        "dry durum wheat pasta": "Starchy vegetables",
        "mixed cereal flakes": "whole grain foods",
        "barres de céréales aux fruits et chocolat": "whole grain foods",
        "céréales préparées": "whole grain foods",
        "mueslis with nuts": "whole grain foods",
        "biscuits and crackers": "enriched grain foods",
        "galletas": "enriched grain foods",
        "da:crackers": "enriched grain foods",
        "chips and fries": "snack foods",
        "chips-and-fries": "snack foods",
        "small-crackers": "snack foods",
        "puffed-rice-cakes": "snack foods",
        "pan dulce": "enriched grain foods",
        "panes": "enriched grain foods",
        "panes de leche": "enriched grain foods",
        "dietary supplements": "protein shake",
        "compléments alimentaires": "protein shake",
        "suplements": "protein shake",
        "suplemento": "protein shake",
        "capsulas isoflavone": "protein shake",
        "soybean oils": "unsaturated",
        "legumes": "legumes",
        "lentils": "legumes",
        "tofu": "legumes",
        "cashew nuts": "nuts and seeds",
        "nuts cereal bars": "nuts and seeds",
        "meats and their products": "red meats",
        "prepared meats": "processed meats",
        "ground-meat-preparations": "red meats",
        "cured-ham": "processed meats",
        "poultry broth": "poultry and wild birds",
        "turkey preparations": "poultry and wild birds",
        "egg-white-raw": "eggs",
        "fish and shellfish": "fish and shellfish",
        "patés de origen animal": "organ meats",
        "leche": "milks",
        "leches": "milks",
        "leche en polvo": "milks",
        "leche semidesnatada": "milks",
        "whole milks": "milks",
        "milks (liquid and powder)": "milks",
        "leche de chocolate": "milks",
        "leche light": "milks",
        "leche de bebé": "baby foods",
        "fermented dairy desserts": "yogurts and kefir",
        "fermented dairy desserts with fruits": "yogurts and kefir",
        "plain fermented dairy desserts": "yogurts and kefir",
        "yogurt de durazno": "yogurts and kefir",
        "yogurt with strawberries": "yogurts and kefir",
        "plant-based foods and beverages": "other plant-based foods",
        "plant-based-foods-and-beverages": "other plant-based foods",
        "aliments et boissons à base de végétaux": "other plant-based foods",
        "aliments-et-boissons-à-base-de-végétaux": "other plant-based foods",
        "dairy substitutes": "other plant-based foods",
        "dairy-spread": "other plant-based foods",
        "dairy-spreads": "other plant-based foods",
        "coconut-based drinks": "Forti plant-b bev (low protein)",
        "water": "water",
        "coffe": "other beverages",
        "café": "other beverages",
        "café con leche con azúcar": "other beverages",
        "café méxico": "other beverages",
        "marsh-mallow tea": "other beverages",
        "té de matcha": "other beverages",
        "té hierbabuena": "other beverages",
        "tés con hierbabuena": "other beverages",
        "carbonated drinks": "other beverages",
        "artificially sweetened beverages": "other beverages",
        "artificially-sweetened-beverages": "other beverages",
        "fruit juices": "fruit juice",
        "juices": "fruit juice",
        "iced-teas": "other beverages",
        "horchata": "other beverages",
        "non-alcoholic beverages": "other beverages",
        "non alcoholic beverages ready to drink": "other beverages",
        "alcoholic beverages": "alcoholic beverages ",
        "cervezas sin alcohol": "alcoholic beverages ",
        "hard liquors": "alcoholic beverages ",
        "liqueurs": "alcoholic beverages ",
        "white wine": "alcoholic beverages ",
        "rum-based alcoholic beverages": "alcoholic beverages ",
        "biscuits and cakes": "high sugar foods",
        "biscuits et gâteaux": "high sugar foods",
        "cookies con chocolate": "high sugar foods",
        "chocolate chip cookies": "high sugar foods",
        "chocolate covered almonds": "high sugar foods",
        "chocolates": "high sugar foods",
        "chocolates con leche": "high sugar foods",
        "dulces de chocolate": "high sugar foods",
        "snacks dulces": "high sugar foods",
        "snacks sucrés": "high sugar foods",
        "untables dulces": "high sugar foods",
        "confectioneries": "high sugar foods",
        "dessert sauces": "high sugar foods",
        "bombones": "high sugar foods",
        "hot sauces": "condiments",
        "sauces chili": "condiments",
        "sauces worcestershire": "condiments",
        "mayonnaise": "condiments",
        "creams": "condiments",
        "crema de leche": "condiments",
        "mustards": "condiments",
        "moutardes": "condiments",
        "dip con sabor chipotle": "condiments",
        "baby foods": "baby foods",
        "non food product": "misc foods",
        "non food products": "misc foods",
        "open food facts": "misc foods",
        "miscellaneous foods": "misc foods",
        "meal replacements": "protein shake",
        "products for specific diets": "protein shake",
        "CNF recipes": "cnf recipes",
    }

    query = {
        "countries": {"$regex": "mexico", "$options": "i"},
        "categories": {"$exists": True, "$type": "string"},
        "can_categories": {"$exists": False},  # ← évite les doublons
    }

    for doc in collection.find(query).limit(limit):
        raw = doc["categories"]
        matched_key = None
        matched_value = None

        for cat in raw.split(","):
            cat_clean = cat.strip().lower()
            if cat_clean in lexical_map:
                matched_key = lexical_map[cat_clean]
                matched_value = category_map.get(matched_key)
                break

        if matched_value:
            collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"can_categories": matched_value}}
            )
            updated.append(
                {
                    "_id": str(doc["_id"]),
                    "used_category": cat_clean,
                    "mapped_to": matched_key,
                    "can_categories": matched_value,
                }
            )

    return jsonify(
        {
            "status": "Mapping completed",
            "country": "Mexico",
            "documents_updated": len(updated),
            "updated_documents": updated,  # ← liste complète des documents modifiés
        }
    )


@app.route("/map_usa_categories", methods=["POST"])
def map_usa_categories():
    limit = int(request.args.get("limit", 10000))
    updated = []

    lexical_map = {
        "fruit puree": "fruit",
        "fruit-puree": "fruit",
        "fruit-pouch": "fruit",
        "applesauce": "fruit",
        "apple sauce pouch": "fruit",
        "apple pies": "fruit",
        "apples": "fruit",
        "fruit": "fruit",
        "fruit-roll": "fruit",
        "fruit-leather": "fruit",
        "fruit-preserves": "fruit",
        "fruit-pulp": "fruit",
        "fruit-sauce": "fruit",
        "romaine lettuce": "dark green vegetables",
        "lettuce": "dark green vegetables",
        "fresh broccoli": "dark green vegetables",
        "fresh green beans": "other vegetables",
        "fresh sweet peppers": "deep yellow or orange vegetables",
        "yellow potatoes": "Starchy vegetables",
        "sweet corn": "Starchy vegetables",
        "plantain-chips": "Starchy vegetables",
        "corn chips": "Starchy vegetables",
        "rolled oats": "whole grain foods",
        "raisin bran": "whole grain foods",
        "whole wheat buns": "whole wheat foods",
        "whole or semi-whole durum wheat pasta": "whole wheat foods",
        "mueslis with nuts": "whole grain foods",
        "cereal bars with nuts": "whole grain foods",
        "cereal clusters with nuts": "whole grain foods",
        "cereals with fruits": "whole grain foods",
        "plant-based foods and beverages": "other plant-based foods",
        "plant-based-foods-and-beverages": "other plant-based foods",
        "aliments et boissons à base de végétaux": "other plant-based foods",
        "dairy substitutes": "other plant-based foods",
        "dairy-spread": "other plant-based foods",
        "coconut-based drinks": "Forti plant-b bev (low protein)",
        "coconut water": "Forti plant-b bev (low protein)",
        "coffee": "other beverages",
        "iced tea": "other beverages",
        "carbonated drinks": "other beverages",
        "artificially sweetened beverages": "other beverages",
        "fruit juice": "fruit juice",
        "apple juice concentrates": "fruit juice",
        "fruit-juice": "fruit juice",
        "fruit-juices": "fruit juice",
        "baby food": "baby foods",
        "baby foods": "baby foods",
        "baby-food": "baby foods",
        "baby-food-puree": "baby foods",
        "meats and their products": "red meats",
        "beef stick": "red meats",
        "hamburger patties": "red meats",
        "chicken breast": "poultry and wild birds",
        "chicken thighs": "poultry and wild birds",
        "turkey breasts": "poultry and wild birds",
        "eggs": "eggs",
        "fish fingers": "fish and shellfish",
        "seafood": "fish and shellfish",
        "shrimp cracker": "fish and shellfish",
        "milk chocolate": "milks",
        "whole milks": "milks",
        "milk chocolate bar": "milks",
        "low-fat yogurts": "yogurts and kefir",
        "whole milk yogurts": "yogurts and kefir",
        "yogurt pouch": "yogurts and kefir",
        "yogurt smoothie": "yogurts and kefir",
        "yogurt mixed berry": "yogurts and kefir",
        "cheese colby jack": "cheeses",
        "cheese spreads": "cheeses",
        "cream cheese": "cheeses",
        "processed-cheese": "cheeses",
        "chocolate chip cookies": "high sugar foods",
        "chocolates": "high sugar foods",
        "candy chocolate bars": "high sugar foods",
        "confectioneries": "high sugar foods",
        "ice creams": "high sugar foods",
        "ice cream bars": "high sugar foods",
        "ice cream cones": "high sugar foods",
        "ice cream sandwich": "high sugar foods",
        "ice cream topping": "high sugar foods",
        "sugar-free chewing gum": "high sugar foods",
        "snack-food": "snack foods",
        "chips and fries": "snack foods",
        "chips-and-fries": "snack foods",
        "crisps": "snack foods",
        "puffed-snack": "snack foods",
        "puffed-corn-snacks": "snack foods",
        "seasoning": "condiments",
        "spice-mix": "condiments",
        "sauces and condiments variety packs": "condiments",
        "worcestershire sauces": "condiments",
        "hot sauces": "condiments",
        "soy sauces": "condiments",
        "meal replacements": "protein shake",
        "dietary supplements": "protein shake",
        "nutritional supplement": "protein shake",
        "protein-supplement": "protein shake",
        "vitamin-supplement": "protein shake",
        "alcoholic beverages": "alcoholic beverages ",
        "red wines": "alcoholic beverages ",
        "whiskey": "alcoholic beverages ",
        "non alcoholic beer": "alcoholic beverages ",
        "open food facts": "misc foods",
        "non food product": "misc foods",
        "baby item": "misc foods",
        "cat food": "misc foods",
    }

    query = {
        "$or": [
            {"countries": {"$regex": "usa", "$options": "i"}},
            {"countries": {"$regex": "united[- ]states", "$options": "i"}},
        ],
        "categories": {"$exists": True, "$type": "string"},
        "can_categories": {"$exists": False},
    }

    for doc in collection.find(query).limit(limit):
        raw = doc["categories"]
        matched_key = None
        matched_value = None

        for cat in raw.split(","):
            cat_clean = cat.strip().lower()
            if cat_clean in lexical_map:
                matched_key = lexical_map[cat_clean]
                matched_value = category_map.get(matched_key)
                break

        if matched_value:
            collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"can_categories": matched_value}}
            )
            updated.append(
                {
                    "_id": str(doc["_id"]),
                    "used_category": cat_clean,
                    "mapped_to": matched_key,
                    "can_categories": matched_value,
                }
            )

    return jsonify(
        {
            "status": "Mapping completed",
            "country": "usa + united-states",
            "documents_updated": len(updated),
            "updated_documents": updated[:10],  # aperçu
        }
    )


@app.route("/map_canada_categories", methods=["POST"])
def map_canada_categories():
    limit = int(request.args.get("limit", 10000))
    updated = []

    lexical_map = {
        "apple pies": "fruit",
        "apples": "fruit",
        "applesauces": "fruit",
        "fruit leather": "fruit",
        "fruit smoothies": "fruit",
        "fresh fruit": "fruit",
        "fresh bananas": "fruit",
        "fresh clementine oranges": "fruit",
        "fresh organic apples": "fruit",
        "romaine lettuce": "dark green vegetables",
        "spinach young leaves": "dark green vegetables",
        "sweet corn": "Starchy vegetables",
        "potato preparations": "Starchy vegetables",
        "corn chips": "Starchy vegetables",
        "rolled oats": "whole grain foods",
        "whole wheat bread": "whole wheat foods",
        "whole grain bread": "whole grains",
        "mueslis with nuts": "whole grain foods",
        "plant-based foods and beverages": "other plant-based foods",
        "aliments et boissons à base de végétaux": "other plant-based foods",
        "dairy substitutes": "other plant-based foods",
        "coconut-based drinks": "Forti plant-b bev (low protein)",
        "coconut water": "Forti plant-b bev (low protein)",
        "coffee": "other beverages",
        "iced tea": "other beverages",
        "carbonated drinks": "other beverages",
        "fruit juice": "fruit juice",
        "apple juice concentrates": "fruit juice",
        "baby foods": "baby foods",
        "meats and their products": "red meats",
        "chicken breast": "poultry and wild birds",
        "turkey preparations": "poultry and wild birds",
        "eggs from caged hens": "eggs",
        "seafood": "fish and shellfish",
        "whole milks": "milks",
        "low-fat yogurts": "yogurts and kefir",
        "cheese spreads": "cheeses",
        "cream cheese": "cheeses",
        "chocolate chip cookies": "high sugar foods",
        "chocolates": "high sugar foods",
        "ice creams": "high sugar foods",
        "ice creams and sorbets": "high sugar foods",
        "snack food": "snack foods",
        "chips and fries": "snack foods",
        "seasoning": "condiments",
        "spice-mix": "condiments",
        "hot sauces": "condiments",
        "soy sauces": "condiments",
        "meal replacements": "protein shake",
        "dietary supplements": "protein shake",
        "protein supplement": "protein shake",
        "alcoholic beverages": "alcoholic beverages ",
        "red wines": "alcoholic beverages ",
        "non food product": "misc foods",
        "open food facts": "misc foods",
    }

    query = {
        "$or": [
            {"countries": {"$regex": "canada", "$options": "i"}},
            {"countries": {"$regex": "canadian", "$options": "i"}},
        ],
        "categories": {"$exists": True, "$type": "string"},
        "can_categories": {"$exists": False},
    }

    for doc in collection.find(query).limit(limit):
        raw = doc["categories"]
        matched_key = None
        matched_value = None

        for cat in raw.split(","):
            cat_clean = cat.strip().lower()
            if cat_clean in lexical_map:
                matched_key = lexical_map[cat_clean]
                matched_value = category_map.get(matched_key)
                break

        if matched_value:
            collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"can_categories": matched_value}}
            )
            updated.append(
                {
                    "_id": str(doc["_id"]),
                    "used_category": cat_clean,
                    "mapped_to": matched_key,
                    "can_categories": matched_value,
                }
            )

    return jsonify(
        {
            "status": "Mapping completed",
            "country": "Canada",
            "documents_updated": len(updated),
            "updated_documents": updated[:10],
        }
    )


@app.route("/export_used_category_mexico", methods=["GET"])
def export_used_category_mexico():
    limit = int(request.args.get("limit", 10000))
    counter = Counter()

    query = {
        "countries": {"$regex": "mexico", "$options": "i"},
        "categories": {"$exists": True, "$type": "string"},
    }

    for doc in collection.find(query).limit(limit):
        used = get_valid_category(doc)
        if used:
            counter[used] += 1

    sorted_counts = dict(counter.most_common())
    return jsonify(
        {
            "country": "Mexico",
            "total_documents": sum(counter.values()),
            "used_categories": sorted_counts,
        }
    )


@app.route("/export_used_category_usa", methods=["GET"])
def export_used_category_usa():
    limit = int(request.args.get("limit", 10000))  # 16425
    counter = Counter()

    query = {
        "$or": [
            {"countries": {"$regex": "usa", "$options": "i"}},
            {"countries": {"$regex": "united-states", "$options": "i"}},
        ],
        "categories": {"$exists": True, "$type": "string"},
    }

    for doc in collection.find(query).limit(limit):
        used = get_valid_category(doc)
        if used:
            counter[used] += 1

    sorted_counts = dict(counter.most_common())
    return jsonify(
        {
            "country": "usa + united-states",
            "total_documents": sum(counter.values()),
            "used_categories": sorted_counts,
        }
    )


@app.route("/export_used_category_canada", methods=["GET"])
def export_used_category_canada():
    limit = int(request.args.get("limit", 10000))
    counter = Counter()

    query = {
        "countries": {"$regex": "canada", "$options": "i"},
        "categories": {"$exists": True, "$type": "string"},
    }

    for doc in collection.find(query).limit(limit):
        used = get_valid_category(doc)
        if used:
            counter[used] += 1

    sorted_counts = dict(counter.most_common())
    return jsonify(
        {
            "country": "Canada",
            "total_documents": sum(counter.values()),
            "used_categories": sorted_counts,
        }
    )


@app.route("/equivalent_mongo", methods=["GET"])
def trouver_neo_equivalent_dans_mongo():
    neo4j_session1 = neo4j_driver.session()
    neo4j_session2 = neo4j_driver.session()
    produit_neo_query = neo4j_session1.run("MATCH(p:Produit) RETURN p")
    liste_produit_neo = [record["p"] for record in produit_neo_query]
    for produit in liste_produit_neo:
        equivalents_produit = trouver_liste_mongo(produit)
        # update neo
        neo4j_session2.run(
            """
        MATCH (p:Produit {nom: $nom_produit})
        UNWIND $equivalents AS eq
        MERGE (m:MongoProduit {mongo_id: eq.id})
        MERGE (p)-[s:EQUIVALENT]->(m)
        SET s.score = eq.score
        """,
            nom_produit=produit["nom"],
            equivalents=[
                {"id": mongo_id, "score": score}
                for mongo_id, score in equivalents_produit
            ],
        )

    neo4j_session1.close()
    neo4j_session2.close()
    return jsonify({"test": "test2"})
