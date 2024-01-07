from Auteur import Auteur  # Importe la classe Auteur du module Auteur
import re
from nltk.corpus import stopwords
from scipy.sparse import csr_matrix
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class Corpus:
    def __init__(self, nom):
        # Initialise les attributs du corpus
        self.nom = nom
        self.authors = {}  # Dictionnaire pour stocker les auteurs du corpus
        self.aut2id = {}   # Dictionnaire de correspondance auteur vers ID
        self.id2doc = {}   # Dictionnaire de correspondance ID vers document
        self.ndoc = 0      # Compteur du nombre de documents dans le corpus
        self.naut = 0      # Compteur du nombre d'auteurs dans le corpus
        self.concatenated_text = None # Attribut supplémentaire pour stocker le texte concaténé


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

    def build_concatenated_text(self):
        # Construit le texte concaténé à partir de tous les documents du corpus
        self.concatenated_text = " ".join(doc.texte for doc in self.id2doc.values())

    def concordance(self, motif, taille_contexte=50):
        # Recherche des occurrences du motif dans le texte concaténé
        if self.concatenated_text is None:
            # Si concatenated_text n'est pas encore construit, le construire
            self.build_concatenated_text()

        # Utilise re.finditer pour trouver toutes les occurrences du motif dans le texte concaténé
        occurrences = [(match.start(), match.end()) for match in
                       re.finditer(r'\b(?:' + re.escape(motif) + r')\b', self.concatenated_text, flags=re.IGNORECASE)]

        # Construction du tableau de concordance avec contexte gauche et droit
        concordance_table = []
        for start, end in occurrences:
            debut_contexte = max(0, start - taille_contexte)
            fin_contexte = min(len(self.concatenated_text), end + taille_contexte)
            contexte_gauche = self.concatenated_text[debut_contexte:start]
            contexte_droit = self.concatenated_text[end:fin_contexte]

            concordance_table.append({
                'Contexte Gauche': contexte_gauche,
                'Motif Trouvé': self.concatenated_text[start:end],
                'Contexte Droit': contexte_droit
            })

        # Retourne le tableau de concordance en utilisant pandas DataFrame
        return pd.DataFrame(concordance_table)

    def construire_vocabulaire_et_freq(self):
        # Initialiser la liste des stop words
        stop_words = set(stopwords.words('english'))  # Pour l'anglais, ajustez si nécessaire

        # Initialiser un dictionnaire pour stocker les occurrences de chaque mot
        freq_dict = {}

        # Initialiser un ensemble pour stocker les mots uniques par document
        mots_par_document = {}

        # Boucler sur les documents du corpus
        for doc in self.id2doc.values():
            # Utiliser split avec différentes délimitations (espace, tabulation, ponctuation, etc.)
            mots = re.split(r'\s+|[.,;!?\'"()]', doc.texte)

            # Filtrer les mots pour exclure les stop words
            mots_filtres = [mot for mot in mots if mot.lower() not in stop_words]

            # Ajouter les mots à l'ensemble des mots par document
            mots_par_document[doc.titre] = set(mots_filtres)

            # Compter les occurrences de chaque mot
            for mot in mots_filtres:
                freq_dict[mot] = freq_dict.get(mot, 0) + 1

        # Initialiser un dictionnaire pour stocker le document frequency de chaque mot
        doc_freq_dict = {}

        # Calculer le document frequency de chaque mot
        for mot in freq_dict.keys():
            doc_freq_dict[mot] = sum(1 for mots in mots_par_document.values() if mot in mots)

        # Convertir l'ensemble en un dictionnaire avec des indices
        vocabulaire_dict = {mot: indice for indice, mot in enumerate(freq_dict.keys())}

        # Construire un DataFrame pandas pour stocker le vocabulaire, les fréquences, et le document frequency
        df_freq = pd.DataFrame(list(freq_dict.items()), columns=['Mot', 'Fréquence'])
        df_freq['Document Frequency'] = df_freq['Mot'].apply(lambda mot: doc_freq_dict.get(mot, 0))

        # Retourner le vocabulaire et le DataFrame de fréquences
        return vocabulaire_dict, df_freq

    def construire_vocab(self):
        # Initialiser la liste des stop words
        stop_words = set(stopwords.words('english'))

        # Initialiser un dictionnaire pour stocker les occurrences de chaque mot
        freq_dict = defaultdict(int)

        # Boucler sur les documents du corpus
        for doc in self.id2doc.values():
            # Utiliser split avec différentes délimitations (espace, tabulation, ponctuation, etc.)
            mots = re.split(r'\s+|[.,;!?\'"()]', doc.texte)

            # Filtrer les mots pour exclure les stop words
            mots_filtres = [mot.lower() for mot in mots if mot.lower() not in stop_words]

            # Compter les occurrences de chaque mot
            for mot in mots_filtres:
                freq_dict[mot] += 1

        # Retirer les doublons et trier par ordre alphabétique
        vocab = sorted(set(freq_dict.keys()))

        # Construire le dictionnaire final avec des informations supplémentaires
        vocab_dict = {mot: {'id': indice, 'occurrences': freq_dict[mot]} for indice, mot in enumerate(vocab)}

        # Retourner le dictionnaire vocab
        return vocab_dict

    def construire_matrice_tf(self, vocab):
        # Initialiser la liste des stop words
        stop_words = set(stopwords.words('english'))

        # Initialiser des listes pour les indices de ligne, de colonne et les données de la matrice creuse
        row_indices = []
        col_indices = []
        data = []

        # Boucler sur les documents du corpus
        for i, doc in enumerate(self.id2doc.values()):
            # Utiliser split avec différentes délimitations (espace, tabulation, ponctuation, etc.)
            mots = re.split(r'\s+|[.,;!?\'"()]', doc.texte)

            # Filtrer les mots pour exclure les stop words
            mots_filtres = [mot.lower() for mot in mots if mot.lower() not in stop_words]

            # Compter les occurrences de chaque mot
            freq_dict = defaultdict(int)
            for mot in mots_filtres:
                freq_dict[mot] += 1

            # Remplir les listes pour la matrice creuse
            for mot, info in vocab.items():
                if mot in freq_dict:
                    row_indices.append(i)
                    col_indices.append(info['id'])
                    data.append(freq_dict[mot])

        # Construire la matrice creuse avec scipy.sparse.csr_matrix
        mat_tf = csr_matrix((data, (row_indices, col_indices)), shape=(len(self.id2doc), len(vocab)))

        # Retourner la matrice creuse mat_tf
        return mat_tf

    def mettre_a_jour_vocab_avec_occurrences(self, vocab, mat_tf):
        # Calculer le nombre total d'occurrences et le nombre total de documents pour chaque mot
        total_occurrences = mat_tf.sum(axis=0)
        nombre_documents_contenant_mot = np.asarray((mat_tf > 0).sum(axis=0))

        # Mettre à jour le dictionnaire vocab avec ces informations
        for mot, info in vocab.items():
            indice_colonne = info['id']
            info['occurrences_corpus'] = total_occurrences[0, indice_colonne]
            info['nombre_documents_contenant'] = nombre_documents_contenant_mot[0, indice_colonne]

    def construire_matrice_tfidf(self, mat_tf):
        # Utiliser TfidfTransformer de scikit-learn pour calculer la matrice TF-IDF
        transformer = TfidfTransformer()
        mat_tfidf = transformer.fit_transform(mat_tf)

        # Retourner la matrice TF-IDF
        return mat_tfidf

    def moteur_de_recherche(self, requete, vocab, mat_tfidf):
        # Nettoyer et transformer la requête
        requete_traitee = self.nettoyer_texte(requete)
        vecteur_requete = self.transformer_requete_vers_vecteur(requete_traitee, vocab)

        # Calculer la similarité cosinus entre le vecteur requête et tous les documents
        similarites = cosine_similarity(vecteur_requete.reshape(1, -1), mat_tfidf)

        # Trier les résultats par similarité décroissante
        indices_tries = similarites.argsort()[0][::-1]

        # Afficher les meilleurs résultats (top 10)
        print("Top 10 des résultats de la recherche:")
        for indice in indices_tries[:10]:
            document = self.id2doc[indice]
            print(
                f"Titre : {document.titre}\nAuteur : {document.auteur}\nSimilarité : {similarites[0, indice]:.4f}\nURL : {document.url}\n---")

    def transformer_requete_vers_vecteur(self, requete, vocab):
        # Initialiser un vecteur avec des zéros
        vecteur = np.zeros(len(vocab))

        # Compter les occurrences des mots dans la requête
        mots_requete = re.split(r'\s+|[.,;!?\'"()]', requete)
        for mot in mots_requete:
            mot = mot.lower()
            if mot in vocab:
                indice_colonne = vocab[mot]['id']
                vecteur[indice_colonne] += 1

        # Retourner le vecteur de la requête
        return vecteur

    def nettoyer_texte(self, texte):
        # Appliquer différents traitements pour nettoyer le texte
        texte_nettoye = texte.lower()  # Mise en minuscules
        texte_nettoye = re.sub(r'\n', ' ', texte_nettoye)  # Remplacement des passages à la ligne
        texte_nettoye = re.sub(r'[^\w\s]', '', texte_nettoye)  # Suppression de la ponctuation

        return texte_nettoye


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
