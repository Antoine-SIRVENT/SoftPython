# Importation des classes nécessaires depuis différents modules
from Document import RedditDocument, ArxivDocument
from Auteur import Auteur
from Corpus import CorpusSingleton

import praw  # Bibliothèque pour accéder à l'API de Reddit
import urllib.request  # Bibliothèque pour effectuer des requêtes HTTP
import xmltodict  # Bibliothèque pour analyser des données XML
import datetime  # Bibliothèque pour manipuler des dates et des heures
import pickle  # Bibliothèque pour la sérialisation d'objets en format binaire

# Initialisation de variables globales
recherche = "cars"
nombre_articles_int = 100

textes = []  # Liste pour stocker le contenu textuel des documents
textes_bruts = []  # Liste pour stocker les documents bruts

# Paramètres de recherche pour Reddit
reddit = praw.Reddit(client_id='c1eSaIr6Je4F-XaS6I3MoQ', client_secret='vLx8I8NTqY6iYLxyo3bWnozbnSCPIQ', user_agent='Antoine')
subr = reddit.subreddit(recherche).hot(limit=nombre_articles_int)

# Récupération des posts Reddit
for post in subr:
    texte = post.title
    texte = texte.replace("\n", " ")
    textes.append(texte)
    textes_bruts.append(("Reddit", post))

# Paramètres de recherche pour Arxiv
url = 'http://export.arxiv.org/api/query?search_query=all:' + recherche + '&start=0&max_results=' + str(nombre_articles_int)
data = urllib.request.urlopen(url)
data = xmltodict.parse(data.read().decode('utf-8'))

# Récupération des documents Arxiv
for document in data['feed']['entry']:
    texte = document['title'] + ". " + document['summary']
    texte = texte.replace("\n", " ")
    textes.append(texte)
    textes_bruts.append(("ArXiv", document))

# Traitement sur les textes
for i, texte in enumerate(textes):
    print(f"Document {i} :\t# Nombre de caractères : {len(texte)}\t# Nombre de mots : {len(texte.split(' '))}\t# Nombre de phrases : {len(texte.split('.'))}")
    if len(texte) < 100:
        textes.remove(texte)

textes = " ".join(textes)

collection = []  # Liste pour stocker les documents après traitement

# Conversion des textes bruts en objets de classes spécifiques
for nature, texte in textes_bruts:
    if nature == "Reddit":
        titre = texte.title.replace("\n", '')
        auteur = str(texte.author)
        date = datetime.datetime.fromtimestamp(texte.created).strftime("%Y/%m/%d")
        url = "https://www.reddit.com/" + texte.permalink
        texte = texte.selftext.replace("\n", "")
        document = RedditDocument(titre, auteur, date, url, texte)
        collection.append(document)
    elif nature == "ArXiv":
        titre = texte["title"].replace('\n', '')
        try:
            auteurs = ", ".join([a["name"] for a in texte["author"]])
        except:
            auteurs = texte["author"]["name"]
        summary = texte["summary"].replace("\n", "")
        date = datetime.datetime.strptime(texte["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")
        document = ArxivDocument(titre, auteurs, date, texte["id"], summary)
        collection.append(document)

id2doc = {}  # Dictionnaire pour mapper les identifiants aux titres des documents

# Création d'un index de documents
for i, doc in enumerate(collection):
    id2doc[i] = doc.titre

auteurs = {}  # Dictionnaire pour stocker les auteurs
aut2id = {}  # Dictionnaire pour mapper les auteurs à leurs identifiants
nombre_auteurs = 0  # Variable pour compter le nombre d'auteurs

# Création de la liste+index des Auteurs
for texte in collection:
    if texte.auteur not in aut2id:
        nombre_auteurs += 1
        auteurs[nombre_auteurs] = Auteur(texte.auteur)
        aut2id[doc.auteur] = nombre_auteurs

    auteurs[aut2id[doc.auteur]].add(texte.texte)

# Utilisation du Singleton pour obtenir l'instance unique de Corpus
corpus_singleton = CorpusSingleton()
corpus = corpus_singleton.get_corpus()

# Nettoyage du corpus puis remplissage
corpus.clear()
for doc in collection:
    corpus.add(doc)

# Sauvegarde du corpus dans un fichier binaire avec pickle
with open("corpus.pkl", "wb") as f:
    pickle.dump(corpus, f)

# Suppression de la variable corpus
del corpus

# Récupération du corpus depuis le fichier binaire avec pickle
with open("corpus.pkl", "rb") as f:
    corpus = pickle.load(f)

# Affichage du corpus
corpus.show()
