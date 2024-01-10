class Document:
    def __init__(self, titre="", auteur="", date="", url="", texte="", type=""):
        # Constructeur de la classe Document
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = type

    def __repr__(self):
        # Méthode spéciale pour obtenir une représentation détaillée de l'objet Document
        return f"\n\nTitre : {self.titre}\nAuteur : {self.auteur}\nDate : {self.date}\nURL : {self.url}\nTexte : {self.texte}\nType : {self.type}\t"

    def __str__(self):
        # Méthode spéciale pour obtenir une représentation sous forme de chaîne de l'objet Document
        return f"{self.titre}, par {self.auteur}"

    def getType(self):
        # Méthode pour récupérer le type du document
        return self.type


class RedditDocument(Document):
    def __init__(self, titre="", auteur="", date="", url="", texte="", nb_commentaires=0):
        # Constructeur de la classe RedditDocument, héritant de Document
        super().__init__(titre, auteur, date, url, texte, type="Reddit")
        self.nb_commentaires = nb_commentaires

    def get_nb_commentaires(self):
        # Accesseur pour le nombre de commentaires
        return self.nb_commentaires

    def set_nb_commentaires(self, nb_commentaires):
        # Mutateur pour le nombre de commentaires
        self.nb_commentaires = nb_commentaires

    def __str__(self):
        # Méthode spéciale pour obtenir une représentation sous forme de chaîne de l'objet RedditDocument
        return f"{super().__str__()}, {self.nb_commentaires} commentaires"

    def getType(self):
        # Méthode pour récupérer le type spécifique du document Reddit
        return "Reddit"


class ArxivDocument(Document):
    def __init__(self, titre="", auteurs=None, date="", url="", texte=""):
        # Constructeur de la classe ArxivDocument, héritant de Document
        super().__init__(titre, "", date, url, texte, type="Arxiv")
        self.auteurs = auteurs if auteurs is not None else []

    def get_auteurs(self):
        # Accesseur pour la liste des co-auteurs
        return self.auteurs

    def ajouter_auteur(self, auteur):
        # Méthode pour ajouter un co-auteur à la liste
        self.auteurs.append(auteur)

    def __str__(self):
        # Méthode spéciale pour obtenir une représentation sous forme de chaîne de l'objet ArxivDocument
        liste_auteurs = ", ".join(self.auteurs)
        return f"{super().__str__()}, Co-auteurs : {liste_auteurs}"

    def getType(self):
        # Méthode pour récupérer le type spécifique du document Arxiv
        return "Arxiv"


class DocumentFactory:
    @staticmethod
    def create_document(doc_type, *args, **kwargs):
        # Méthode statique pour créer une instance de document en fonction du type spécifié
        if doc_type == "reddit":
            return RedditDocument(*args, **kwargs)
        elif doc_type == "arxiv":
            return ArxivDocument(*args, **kwargs)
        else:
            return Document(*args, **kwargs)
