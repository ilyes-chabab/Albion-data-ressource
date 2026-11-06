# Albion Online – Pipeline Data Engineering

## 1. Présentation du projet

Ce projet consiste à concevoir et développer un pipeline Data Engineering permettant de collecter, transformer, stocker et publier des données de marché provenant du jeu vidéo **Albion Online**.

Les données sont récupérées à partir de l'API de l'**Albion Online Data Project**, qui fournit les prix des objets dans les différentes villes du serveur européen.

L'objectif est de mettre en place un processus automatisé permettant de passer des données brutes à un jeu de données structuré et exploitable pour des analyses.

## 2. Objectifs du projet

Le projet repose sur plusieurs objectifs :

- Collecter les données de marché depuis une API externe.
- Stocker les données brutes au format JSONL.
- Nettoyer, valider et transformer les données.
- Convertir les données au format Parquet.
- Stocker les données structurées dans une base PostgreSQL.
- Réaliser des analyses SQL.
- Publier le jeu de données sur Hugging Face.
- Mettre en place des tests automatisés pour vérifier la qualité des traitements.

## 3. Architecture du pipeline

Le pipeline est organisé autour de cinq grandes étapes :

```text
          API Albion Online Data Project
                       |
                       v
               INGESTION
             (Python / aiohttp)
                       |
                       v
                DONNÉES BRUTES
                   (JSONL)
                       |
                       v
              TRANSFORMATION
             (Python / Pandas)
                       |
                       v
                DONNÉES TRAITÉES
                  (Parquet)
                       |
              +--------+--------+
              |                 |
              v                 v
          PostgreSQL         Hugging Face
              |                 |
              v                 v
        Analyses SQL       Dataset publié
```

## 4. Organisation du projet

```text
Albion-data-ressource/
│
├── data/
│   ├── raw/
│   │   ├── items.json
│   │   ├── market_prices.jsonl
│   │   └── items_categories/
│   │
│   └── processed/
│       └── market_prices.parquet
│
├── scripts/
│   ├── ingest/
│   │   └── ingest.py
│   │
│   ├── transform/
│   │   ├── validation.py
│   │   ├── transform_prices.py
│   │   └── load_postgres.py
│   │
│   └── publish/
│       └── publish_hf.py
│
├── sql/
│   ├── schema.sql
│   └── analyses.sql
│
├── tests/
│   ├── test_validation.py
│   └── test_transform.py
│
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

## 5. Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Développement du pipeline |
| aiohttp | Requêtes HTTP asynchrones |
| Pandas | Manipulation des données |
| PyArrow | Création et lecture des fichiers Parquet |
| PostgreSQL | Stockage des données structurées |
| Docker | Exécution de PostgreSQL |
| SQL | Analyses et exploitation des données |
| Pytest | Tests automatisés |
| Hugging Face Hub | Publication du dataset |
| Git / GitHub | Gestion du code source et collaboration |

## 6. Installation et configuration

### Prérequis

- Python 3.9 ou supérieur
- Docker Desktop
- Git
- Un compte Hugging Face (pour la publication)

### Récupération du projet

```bash
git clone https://github.com/ilyes-chabab/Albion-data-ressource.git

cd Albion-data-ressource
```

### Installation des dépendances

```bash
python3 -m pip install -r requirements.txt
```

### Configuration des variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
POSTGRES_PASSWORD=votre_mot_de_passe
```

Le fichier `.env` contient les informations de connexion et ne doit jamais être envoyé sur GitHub.

## 7. Exécution du pipeline

### 7.1. Ingestion des données

Le script d'ingestion récupère les données de marché depuis l'API Albion Online Data Project.

```bash
python3 scripts/ingest/ingest.py
```

Les données collectées sont enregistrées au format JSONL dans :

```text
data/raw/market_prices.jsonl
```

Le script utilise notamment :
- Des requêtes HTTP asynchrones.
- Un traitement des erreurs et des nouvelles tentatives.
- Un système de checkpoint pour reprendre une collecte interrompue.

### 7.2. Transformation des données

Le script de transformation effectue plusieurs opérations :

- Validation des enregistrements.
- Vérification des colonnes obligatoires.
- Conversion des dates.
- Gestion des dates indisponibles.
- Suppression des doublons exacts.
- Écriture des données au format Parquet par lots.

Exécution :

```bash
python3 scripts/transform/transform_prices.py
```

Fichier généré :

```text
data/processed/market_prices.parquet
```

### 7.3. Mise en place de PostgreSQL

Démarrage du conteneur :

```bash
docker compose up -d
```

Création de la table à partir du schéma SQL :

```bash
docker exec -i albion_postgres psql -U albion_user -d albion_db < sql/schema.sql
```

Le schéma définit les colonnes, la clé primaire et une contrainte d'unicité permettant d'éviter les doublons.

### 7.4. Chargement des données dans PostgreSQL

Une fois le fichier Parquet généré et PostgreSQL démarré :

```bash
python3 scripts/transform/load_postgres.py
```

Le chargement est effectué par lots et utilise `ON CONFLICT DO NOTHING` pour ignorer les enregistrements déjà présents.

### 7.5. Analyses SQL

Les analyses sont regroupées dans :

```text
sql/analyses.sql
```

Elles permettent notamment :
- De comparer les prix moyens entre les villes.
- D'identifier les objets disponibles dans plusieurs villes.
- De comparer les prix d'un même objet.
- De classer les objets les plus chers par ville.
- D'identifier les plus grands écarts de prix entre les villes.

Le fichier contient également une comparaison des plans d'exécution avec et sans index à l'aide d'`EXPLAIN ANALYZE`.

## 8. Tests automatisés

Les tests sont réalisés avec Pytest.

Exécution de l'ensemble des tests :

```bash
python3 -m pytest -v
```

Les tests couvrent deux parties :

**Validation des données (`test_validation.py`)**
- Vérification des enregistrements.
- Vérification des colonnes obligatoires.
- Vérification des types.
- Vérification des prix et des dates.

**Transformation (`test_transform.py`)**
- Conversion des dates.
- Gestion des dates indisponibles.
- Transformation des enregistrements.
- Détection des doublons.
- Génération d'un fichier Parquet à partir de données de test.

Résultat obtenu lors de la dernière exécution :

- 14 tests exécutés.
- 14 tests réussis.

## 9. Publication sur Hugging Face

Le dataset est publié sur Hugging Face au format Parquet.

Dépôt :

https://huggingface.co/datasets/Sayli84/albion-online-market-prices

Le dépôt est actuellement privé.

La publication est réalisée avec le script :

```bash
python3 scripts/publish/publish_hf.py
```

Le script vérifie l'existence du fichier Parquet et la visibilité privée du dépôt avant de procéder à l'envoi.

Une première version du dataset a été créée avec le tag :

```text
v1.0.0
```

Une Dataset Card en français décrit la provenance des données, les colonnes, les traitements et les limites du jeu de données.

## 10. Informations sur le jeu de données

| Information | Valeur |
|---|---|
| Jeu | Albion Online |
| Région | Europe |
| Source | Albion Online Data Project |
| Format brut | JSONL |
| Format traité | Parquet |
| Nombre de colonnes | 11 |
| Nombre d'enregistrements après déduplication | 47 926 |

Les 11 colonnes correspondent aux identifiants des objets, aux villes, à leur qualité et aux différents prix d'achat et de vente, avec leurs dates de mise à jour.

### Limites des données

- Les données ne représentent pas nécessairement l'ensemble des transactions réalisées dans le jeu.
- Certains prix peuvent être indisponibles.
- Les dates correspondent aux mises à jour des prix fournies par l'API.
- Le dataset ne constitue pas un historique exhaustif des prix inchangés entre plusieurs collectes.

## 11. Source des données

Les données proviennent du projet :

[Albion Online Data Project](https://www.albion-online-data.com/)

API utilisée :

https://europe.albion-online-data.com/api/v2/stats/prices/

Albion Online est développé par Sandbox Interactive GmbH. Ce projet est indépendant et n'est ni affilié à ni approuvé par l'éditeur du jeu.
