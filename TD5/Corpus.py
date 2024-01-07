from Auteur import Auteur  # Importe la classe Auteur du module Auteur

class Corpus:
    def __init__(self, nom):
        # Initialise les attributs du corpus
        self.nom = nom
        self.authors = {}  # Dictionnaire pour stocker les auteurs du corpus
        self.aut2id = {}   # Dictionnaire de correspondance auteur vers ID
        self.id2doc = {}   # Dictionnaire de correspondance ID vers document
        self.ndoc = 0      # Compteur du nombre de documents dans le corpus
        self.naut = 0      # Compteur du nombre d'auteurs dans le corpus

    def add(self, doc):
        # Ajoute un document au corpus
        if doc.auteur not in self.aut2id:
            # Si l'auteur n'est pas déjà dans le dictionnaire, crée une nouvelle entrée
            self.naut += 1
            self.authors[self.naut] = Auteur(doc.auteur)
            self.aut2id[doc.auteur] = self.naut
        # Ajoute le texte du document à l'auteur correspondant
        self.authors[self.aut2id[doc.auteur]].add(doc.texte)
        self.ndoc += 1
        self.id2doc[self.ndoc] = doc  # Ajoute le document au dictionnaire ID-vers-document

    def show(self, n_docs=-1, tri="abc"):
        # Affiche les documents du corpus en fonction des options spécifiées
        docs = list(self.id2doc.values())
        if tri == "abc":
            docs = sorted(docs, key=lambda x: x.titre.lower())[:n_docs]
        elif tri == "123":
            docs = sorted(docs, key=lambda x: x.date)[:n_docs]
        print("\n".join(map(repr, docs)))

    def __repr__(self):
        # Représentation sous forme de chaîne du corpus, triée par ordre alphabétique des titres
        docs = list(self.id2doc.values())
        docs = sorted(docs, key=lambda x: x.titre.lower())
        return "\n".join(map(str, docs))

    def clear(self):
        # Réinitialise la liste des documents du corpus
        self.id2doc = {}

class CorpusSingleton:
    _instance = None

    def __new__(cls):
        # Crée une instance unique de Corpus en utilisant le modèle singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.corpus = Corpus("Mon corpus")
        return cls._instance

    def get_corpus(self):
        # Renvoie l'unique instance de Corpus
        return self.corpus
