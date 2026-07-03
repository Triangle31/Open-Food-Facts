# OPEN FOOD FACTS

## Acquisition des données
Assurez-vous d'avoir les fichiers `products.bson`, `products.metadata.json` dans 
le dossiers `dump_staging` et le fichier `neo4j.dump` dans le dossier `dump_recettes` 
avant de démarrer le projet.

Vous pouvez les télécharger à partir du lien suivant: https://drive.google.com/drive/folders/1J_k_THGR2Lqr-zedXq59wOrOst0bbUg7?usp=sharing

## Configuration
L'application web est instanciée sur le port 80.

### Démarrage du projet
Pour partir le projet la première fois et lorsque que des dépendances sont ajoutées,
roulez la commande suivante:
```
docker compose up --build
```

Autrement, roulez cette commande-ci:
```
docker compose up
```

### Création de dumps de données
#### MongoDB
Dans le root de mongoDb, exécutez la commande suivante:

```
mongodump --db=db_mongo --collection=["la collection a dump"] --out /data/["nom de votre dossier dump"]
```

Ensuite, dans le docker container, exécutez la commande suivante:
```
docker cp db_mongo:/data/["nom de votre dossier dump"] ["Chemin dossier local sauvegarde"]
```

### Restaurations des données
Pour restaurer les données des bases de données, suivre les étapes suivantes.

#### MongoDB
Exécutez les commandes suivantes: 

```
docker cp ["Chemin dossier local pulled"] db_mongo:/data/dump_staging
docker exec -it db_mongo bash
```

Ensuite, dans le root de mongoDB, exécutez la commande suivante:
```
mongorestore  --db=db_mongo /data/dump_staging/
```

#### Neo4j
Depuis le dossier /dump_recettes du projet, exécutez la commande suivante:

```
docker run --rm --volumes-from db_neo4j -v ${PWD}:/backup neo4j:5 neo4j-admin database load neo4j --from-path=/backup --overwrite-destination
```

## Requêtes disponibles

### GET – Heartbeat (vérification du service)
Permet de vérifier que l’API est active et répond correctement.

#### Requête
```
GET /heartbeat
```

#### Réponse
200 - OK
```
{
  "nomApplication": "FoodFacts"
}
```

### GET – Données extraites (statistiques globales)
Retourne des statistiques agrégées calculées à partir :
- de la base de données MongoDB (Open Food Facts et FDC)
- de la base Neo4j (recettes de cuisine)

Ces données sont utilisées pour fournir une vue d’ensemble du contenu disponible dans l’application.

#### Requête
```
GET /extracted_data
```

#### Réponse
200 - OK
```
{
  "ndbProduitsAlimentairesScannes": int,
  "nbProduitsAlimentairesDeBases": int,
  "nbRecettesCuisine": int
}
```

### GET – Données transformées (statistiques globales)
Retourne des statistiques agrégées calculées à partir de notre bases de données MongoDB.
Ces données sont utilisées pour fournir une vue d’ensemble du contenu disponible dans l’application.

#### Requête
```
GET /transformed_data
```

#### Réponse
200 - OK
```
...
```

### GET – ReadMe
Retourne la fichier README.md.

#### Requête
```
GET /readme
```

#### Réponse
200 - OK
```
...
```

### GET – Types de plats
Retourne la liste de tous les types de plats disponibles dans la base de données des recettes.
Les types de plats sont récupérés à partir des nœuds `TypeDePlat` stockés dans Neo4j.

#### Requête
```
GET /type
```

#### Réponse
200 - OK
```
...
```

### POST – Recette selon type
Retourne une recette aléatoire qui répond aux types définis.

#### Paramètres
```
{
    "type": [
        str, 
        str,
        ...
    ]
}
```


#### Requête
```
POST /recette
```

#### Réponse
200 - OK
```
...
```

### POST – Recommandations de produits
Retourne pour chaque ingrédients d'une recette donnée une liste de recommandations de produits
selon les paramètres définis.

#### Paramètres
```
{
    "recette": {
        "nom": str,
        "ingredients": [
            ...
        ],
        "description": str,
        ...
    },
    "preferenceMarqueProduit": str,
    "indicateurDeQualiteSuperieurA": {
        "NutriScore": str,
        "Nova": str,
        "EcoScore": str
    },
}
```

#### Requête
```
POST /cuisiner
```

#### Réponse
200 - OK
```
...
```