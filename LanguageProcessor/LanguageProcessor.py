from string import punctuation

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from Contractions import substitute_contraction


class LanguageProcessor:
    def __init__(self):
        """
        All of the natural processing functionality
        """

        self.lemmatizer = WordNetLemmatizer()

        self.punctuation_list = [c for c in punctuation]

        # Loading stopwords
        r = open("Stopwords.txt", "r")
        self.STOPWORDS = []
        for word in r:
            self.STOPWORDS.append(word.replace("\n", ""))

        # TODO: Get more complete list and read it from file
        MORESTOP = ['will', 'thing', 'n\'t', '\'\'', '\'s', '``', '\'re', '\'', 'mr', 'mr.', '--', '...', '..', '->', '\'.',
                    '\' \'', ' .', '’',
                    '“', '”', "", "\n"]
        for m in MORESTOP:
            self.STOPWORDS.append(m)

    def substitute_contractions(self, text):
        """
        Loop through words and sub contractions
        :param text:
        :return:
        """
        subbed = []
        for word in text.split():
            subbed.append(substitute_contraction(word))
        return " ".join(subbed)

    def get_non_stopwords(self, text, substitute_contractions=True, stem=True):
        """
        Returns a list of lowercase non-stopwords in the text.
        non-stopwords are anything that is not punctuation or stopwords
        Numerical values are NOT FILTERED OUT
        :param text:
        :param stem:
        :return:
        """

        if substitute_contractions:
            subbed_text = self.substitute_contractions(text)
        else:
            subbed_text = text

        non_stop_words = []
        tokens = word_tokenize(subbed_text)

        # Loop through tokens
        for tok in tokens:
            t = tok.lower()
            token = self.remove_punctuation(t)
            if token not in self.STOPWORDS:
                # Check if token contains punctuation
                if token not in self.punctuation_list:
                    if stem:
                        non_stop_words.append(self.get_word_lemma(token))
                    else:
                        non_stop_words.append(token)

        return non_stop_words

    def get_noun_phrases(self, text, filter_stopwords=True):
        """
        Gets the noun phrases from a text, by parsing grammar POS tagged
        :param text:
        :param filter_stopwords"
            Filters the stopwords from noun-phrases
        :return:
            Returns a list of noun phrases with list for each scentence
        """

        sentences = nltk.sent_tokenize(text)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]

        grammar = """NP: {<DT>?<JJ>*<NN.*>+}
                  """

        # Alternative grammer structures that can be parsed, can add to the grammar string
        """
        RELATION: {<V.*>}
                  {<DT>?<JJ>*<NN.*>+}
        ENTITY: {<NN.*>}
        """

        cp = nltk.RegexpParser(grammar)
        noun_phrases_list = [[' '.join(leaf[0] for leaf in tree.leaves())
                              for tree in cp.parse(sent).subtrees()
                              if tree.label() == 'NP']
                             for sent in sentences]

        if not filter_stopwords:
            return noun_phrases_list

        # Filters the stopwords from the parsed noun phrases
        else:
            phrases = []
            for elem in noun_phrases_list:
                for noun_phrase in elem:

                    # Search each word in return phrase to remove stopwords
                    phrase = []
                    for word in noun_phrase.split():
                        w = word.lower()
                        if w not in self.STOPWORDS:
                            phrase.append(w)

                    if phrase != []:
                        phrases.append(" ".join(phrase))

            return phrases

    # TODO: Improve parsing speed with spacy
    def get_adjectives_list(self, text):
        """
        Uses the POS tagger to get all of the Adjectives, whose tags start with "j"
        :param text:
        :return:
        """

        tokens = nltk.word_tokenize(text)

        adjectives = []
        tagged = nltk.pos_tag(tokens)
        for t in tagged:
            # Check the first charcter if tag
            if t[1][0] == "J":
                adjectives.append(t[0])

        return adjectives

    # TODO: Improve parsing speed with spacy
    def get_nouns_list(self, text):
        """
        Uses the POS tagger to get all of the Adjectives, whose tags start with "j"
        :param text:
        :return:
        """

        tokens = nltk.word_tokenize(text)

        nouns = []
        tagged = nltk.pos_tag(tokens)
        for t in tagged:
            # Check the first charcter if tag
            if t[1][0] == "N":
                nouns.append(t[0])

        return nouns

    def get_word_lemma(self, word):
        """
        Helper to allows customization to stemming process, like checking for trailing e's
        :param word:
        :return:
        """
        lema = self.lemmatizer.lemmatize(word)
        return lema

    def remove_punctuation(self, text):
        """
        Helper function to remove all non-acsii charcters
        :param text:
        :return:
        """
        return ''.join([i if ord(i) < 128 else '' for i in text])

    def is_text_token(self, token):
        """
        Checks if not punc or numerical, or non-acsii
        :param token:
        :return:
        """

        if len(token) == 1:
            if ord(token) < 128 and token not in punctuation and not token.isdigit():
                return True
            else:
                return False

        else:
            if not token.isdigit():
                return True
            else:
                return False