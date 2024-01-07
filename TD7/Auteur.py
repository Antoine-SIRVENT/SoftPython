class Auteur:
    def __init__(self, name):
        # Initialise un objet Auteur avec un nom, un compteur de documents (ndoc), et une collection de productions (documents).
        self.name = name
        self.ndoc = 0  # Initialise le compteur de documents à 0
        self.collection = []  # Initialise la collection de productions comme une liste vide

    def add(self, production):
        # Méthode pour ajouter une production à la collection de l'auteur
        self.ndoc += 1  # Incrémente le compteur de documents
        self.collection.append(production)  # Ajoute la production à la collection

    def __str__(self):
        # Méthode spéciale pour obtenir une représentation sous forme de chaîne de l'objet Auteur
        return f"Auteur : {self.name}\t# productions : {self.ndoc}"
        # Retourne une chaîne formatée avec le nom de l'auteur et le nombre de productions qu'il a
