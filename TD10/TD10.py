# Importation des classes nécessaires depuis différents modules
from Document import RedditDocument, ArxivDocument
from Auteur import Auteur
from Corpus import CorpusSingleton

import praw  # Bibliothèque pour accéder à l'API de Reddit
import urllib.request  # Bibliothèque pour effectuer des requêtes HTTP
import xmltodict  # Bibliothèque pour analyser des données XML
import datetime  # Bibliothèque pour manipuler des dates et des heures
import pickle  # Bibliothèque pour la sérialisation d'objets en format binaire

################################################################

import tkinter as tk #pip install tk
import customtkinter #pip install customtkinter

customtkinter.set_appearance_mode("Light") 
customtkinter.set_default_color_theme("green")

root = customtkinter.CTk()
root.title("Poogle")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 1920) // 2
y = (screen_height - 1080) // 2

root.geometry(f"1920x1080+{x-10}+{y}")

################################################################

# Initialisation de variables globales
recherche = "car"
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
    #print(f"Document {i} :\t# Nombre de caractères : {len(texte)}\t# Nombre de mots : {len(texte.split(' '))}\t# Nombre de phrases : {len(texte.split('.'))}")
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
#corpus.show()

# Construction du dictionnaire vocab
vocab = corpus.construire_vocab()

# Construction de la matrice creuse TF
mat_tf = corpus.construire_matrice_tf(vocab)

# Construction de la matrice creuse TF-IDF
mat_tfidf = corpus.construire_matrice_tfidf(mat_tf)

################################ Affichage ################################

search_result = customtkinter.CTkTextbox(
    master = root, width = 1800, height = 720,
    text_color = "#555555", font = customtkinter.CTkFont(size = 24),
    fg_color = "#f9f9fa", wrap = "word", corner_radius = 8)
search_result.place(x = 60, y = 240)

def resultat_moteur_de_recherche():

    search_result.delete(1.0, tk.END)

    search_result.configure(font = customtkinter.CTkFont(size = 24))

    resultat = corpus.moteur_de_recherche(search_bar.get(), vocab, mat_tfidf)

    search_result.tag_config("titre", foreground = "black")
    search_result.tag_config("auteur", foreground = "gray")
    search_result.tag_config("sim", foreground = "lightblue")
    search_result.tag_config("url", foreground = "blue")

    for i in range(10):

        search_result.insert(tk.END,f"{resultat[i*4]}", tags = "titre")
        search_result.insert(tk.END,f"{resultat[1 + i*4]}", tags = "auteur")
        search_result.insert(tk.END,f"{resultat[2 + i*4]}", tags = "sim")
        search_result.insert(tk.END,f"{resultat[3 + i*4]}", tags = "url")


search_bar = customtkinter.CTkEntry(
    master = root, width = 550, height = 60,
    placeholder_text = "Effectuez une recherche...", placeholder_text_color = "#b6b6b6", text_color = "#555555",
    border_width = 2, font = customtkinter.CTkFont(size = 25))
search_bar.place(x = 665, y = 120)

search_button = customtkinter.CTkButton(
        master = root, width = 60, height = 60,
        text = "🔎", font = customtkinter.CTkFont(size = 35),
        corner_radius = 8, command = resultat_moteur_de_recherche)
search_button.place(x = 590, y = 120)

def show_corpus():

    search_result.delete(1.0, tk.END)
    search_result.configure(font = customtkinter.CTkFont(size = 14))

    tri_choix = corpus_box.get()
    if tri_choix == "Trié par Titre":
        tri = "abc"
    elif tri_choix == "Trié par Date":  
        tri = "123" 
    elif tri_choix == "Trié par Auteur":  
        tri = "auteur"
    elif tri_choix == "Trié par Type":  
        tri = "type"     

    search_result.insert(tk.END,corpus.show(tri))

    search_result.delete(1.0, 3.0)
    
corpus_box = customtkinter.CTkComboBox(
    master=root, width = 180, height = 40, state = "readonly", button_color = "#2cc985", button_hover_color = "#0c955a", border_color = "#2cc985",
    values=["Trié par Titre", "Trié par Auteur", "Trié par Date", "Trié par Type"])
corpus_box.place(x = 1420, y = 130)
corpus_box.set("Trié par Titre")

show_corpus_button = customtkinter.CTkButton(
        master = root, width = 60, height = 40,
        text = "Voir le corpus", font = customtkinter.CTkFont(size = 15),
        corner_radius = 8, command = show_corpus)
show_corpus_button.place(x = 1290, y = 130)

root.mainloop()

################################################################################################################################



