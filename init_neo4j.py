import os

from neo4j import GraphDatabase
import json
import re
import time

# Connexion à Neo4j
driver = GraphDatabase.driver("bolt://db_neo:7687", auth=("neo4j", "equipe23"))

for attempt in range(30):
    try:
        driver.verify_connectivity()
        break
    except:
        print(f"⏳ Waiting for Neo4j... ({attempt})")
        time.sleep(2)
else:
    raise RuntimeError("Neo4j did not become available in time.")

# Fonction pour nettoyer les ingrédients
def nettoyer_ingredient(texte):
    texte = re.sub(r"¼|½|¾", "", texte)
    texte = re.sub(r"\|", "", texte)
    texte = re.sub(r"\d+\/\d+|\d+", "", texte)
    texte = re.sub(r"\bc\.?\s*à\s*(soupe|thé|café|table)\b", "", texte, flags=re.IGNORECASE)
    texte = re.sub(
        r"\b(ml|l|g|kg|oz|boîte|conserve|paquet|tasse|œuf|gousse|environ|tbsp|pincées?|litres?|feuilles?|feuille)\b",
        "", texte, flags=re.IGNORECASE)
    texte = re.sub(r"\(.*?\)", "", texte)
    texte = re.sub(r"\b(de|d’|d'|du|le|la|les|un|une|au|aux)\b", "", texte, flags=re.IGNORECASE)
    texte = re.sub(
        r"\b(émincé|émincées?|haché|hachée?s?|pelé|pelée?s?|coupé|coupée?s?|dégelé|dégelée?s?|divisé|divisée?s?|égoutté|égouttée?s?|rincé|rincée?s?|ajouté|ajoutée?s?|au goût)\b",
        "", texte, flags=re.IGNORECASE)
    texte = re.sub(r"\ben\s+(dés|cubes?|tranches?|lamelles?|morceaux?|julienne|rondelles?)\b", "", texte,
                   flags=re.IGNORECASE)
    texte = re.sub(r",\s*$", "", texte)
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()

def nettoyer_et_split(texte):
    morceaux = re.split(r"\s+(et|ou)\s+", texte, flags=re.IGNORECASE)
    ingredients = [nettoyer_ingredient(m) for m in morceaux if m.lower() not in ["et", "ou"] and m.strip()]
    if len(ingredients) == 1:
        return ingredients[0]
    return ingredients

# Fonction d'import d'une recette
def importer_recette(tx, recette):
    # Nettoyage des champs
    nom_recette = recette.get("titre")
    if not nom_recette:
        print("⚠️ Recette ignorée : titre manquant")
        return  # on ignore cette recette

    auteur = recette.get("auteur")
    if not auteur:
        auteur = "Inconnu"

    types = recette.get("type_de_plat", [])
    description = recette.get("description")
    url = recette.get("url")
    portions = recette.get("portions")
    temps_cuisson = recette.get("temps_cuisson")
    if not temps_cuisson:
        temps_cuisson = "0"

    temps_preparation = recette.get("temps_preparation")
    if not temps_preparation:
        temps_preparation = "0"

    ingredients_bruts = recette.get("ingredients", [])
    ingredients = recette.get("ingredients", [])
    instructions = recette.get("instructions", [])

    # Créer la recette
    tx.run("""
         MERGE (r:Recette {name: $nom_recette})
         SET r.name = $nom_recette,
             r.description = $nom_recette,
             r.description2 = $description,
             r.temps_cuisson = $temps_cuisson,
             r.temps_preparation = $temps_preparation,
             r.portions = $portions,
             r.ingredients_bruts = $ingredients,
             r.instructions = $instructions,
             r.url = $url
         """, nom_recette=nom_recette, description=description, temps_cuisson=temps_cuisson,
           temps_preparation=temps_preparation, url=url, portions=portions,
           ingredients=ingredients, instructions=instructions)

    # Auteur
    tx.run("""
        MERGE (a:Auteur {nom: $auteur})
        MERGE (r:Recette {name: $nom_recette})
        MERGE (r)-[:ECRITE_PAR]->(a)
        """, auteur=auteur, nom_recette=nom_recette)

    # Type de plat
    for type_plat in types:
        sous_types = [t.strip() for t in type_plat.split(",")]
        for st in sous_types:
            tx.run("""
                MERGE (t:TypeDePlat {nom: $type})
                MERGE (r:Recette {name: $nom_recette})
                MERGE (r)-[:EST_DE_TYPE]->(t)
                """, type=st, nom_recette=nom_recette)

    # Temps cuisson
    tx.run("""
        MERGE (tc:TempsCuisson {valeur: $temps})
        MERGE (r:Recette {name: $nom_recette})
        MERGE (r)-[:A_COMME_TEMPS_CUISSON]->(tc)
        """, temps=temps_cuisson, nom_recette=nom_recette)

    # Temps préparation
    tx.run("""
        MERGE (tp:TempsPreparation {valeur: $temps})
        MERGE (r:Recette {name: $nom_recette})
        MERGE (r)-[:A_COMME_TEMPS_PREPARATION]->(tp)
        """, temps=temps_preparation, nom_recette=nom_recette)

    for brut in ingredients:
        produits = nettoyer_et_split(brut)

        if isinstance(produits, str):
            produits = [produits]

        for nom_produit in produits:
            tx.run("""
                MERGE (p:Produit {nom: $nom_produit})
                MERGE (r:Recette {name: $nom_recette})
                MERGE (r)-[:UTILISE]->(p)
                """, nom_produit=nom_produit, nom_recette=nom_recette)

# Charger et importer toutes les recettes depuis tous les fichiers JSON du dossier
dossier = "dump_recettes"

with driver.session() as session:
    for nom_fichier in os.listdir(dossier):
        if nom_fichier.endswith(".json"):
            chemin = os.path.join(dossier, nom_fichier)
            with open(chemin, encoding="utf-8") as f:
                data = json.load(f)
                for recette in data:
                    session.execute_write(importer_recette, recette)

driver.close()
