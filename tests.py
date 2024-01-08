import unittest
from Document import Document, RedditDocument, ArxivDocument, DocumentFactory
from Auteur import Auteur
from Corpus import Corpus, CorpusSingleton

class TestDocumentMethods(unittest.TestCase):
    def setUp(self):
        self.reddit_doc = RedditDocument(titre="Titre Reddit", auteur="Auteur Reddit", date="2022/01/01", nb_commentaires=10)
        self.arxiv_doc = ArxivDocument(titre="Titre ArXiv", auteurs=["Auteur1", "Auteur2"], date="2022/01/02", url="http://example.com", texte="Contenu ArXiv")

    def test_get_type(self):
        self.assertEqual(self.reddit_doc.getType(), "Reddit")
        self.assertEqual(self.arxiv_doc.getType(), "Arxiv")

    def test_arxiv_add_auteur(self):
        self.arxiv_doc.ajouter_auteur("Nouvel Auteur")
        self.assertEqual(len(self.arxiv_doc.get_auteurs()), 3)

class TestAuteurMethods(unittest.TestCase):
    def setUp(self):
        self.auteur = Auteur("Auteur Test")

    def test_add_production(self):
        self.auteur.add("Contenu Document")
        self.assertEqual(self.auteur.ndoc, 1)
        self.assertEqual(len(self.auteur.collection), 1)

class TestCorpusMethods(unittest.TestCase):
    def setUp(self):
        self.corpus = Corpus("Mon Corpus")

    def test_add_document(self):
        doc = Document(titre="Titre Document", auteur="Auteur Document", date="2022/01/01", texte="Contenu Document", type="Test")
        self.corpus.add(doc)
        self.assertEqual(self.corpus.ndoc, 1)

    def test_build_concatenated_text(self):
        doc1 = Document(titre="Doc1", texte="Contenu 1")
        doc2 = Document(titre="Doc2", texte="Contenu 2")
        self.corpus.add(doc1)
        self.corpus.add(doc2)
        self.corpus.build_concatenated_text()
        self.assertIn("Contenu 1", self.corpus.concatenated_text)
        self.assertIn("Contenu 2", self.corpus.concatenated_text)

class TestCorpusSingletonMethods(unittest.TestCase):
    def test_singleton_instance(self):
        corpus1 = CorpusSingleton().get_corpus()
        corpus2 = CorpusSingleton().get_corpus()
        self.assertIs(corpus1, corpus2)

if __name__ == '__main__':
    unittest.main()