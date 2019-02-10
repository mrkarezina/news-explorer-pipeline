from LanguageProcessor import LanguageProcessor

from nltk.tokenize import sent_tokenize
from nltk.probability import FreqDist


class SummaryException(Exception):
    """
    If text could not meet summary requirments, lenght, content...
    TODO: from summa import summarizer, summarizer performs well, graph based
    """
    pass


class Summarizer(LanguageProcessor):
    """
    Freqeucy based summarizer
    Summarizes to the min/max number of tokens required in summary
    Use .summarize

    Frequency based keyword list
    Highest frequency noun_phrases
    """

    def __init__(self, text, include_intro=2):
        """

        :param text:
        :param title:
        :param include_intro:
            How many intro sentences to include in summary
        """

        LanguageProcessor.__init__(self)

        # Min/Max tokens in summary
        self.minimum_length = 110
        self.maximum_length = 180

        # Tokens that indicate sentence should not be in summary
        self.non_body_sentence_blacklist = ["Twitter\n", "Facebook\n", "Instagram\n", "Getty Images", "\n"]

        self.text = text

        self.include_intro = include_intro

        # All non-stopwords tokens
        self.tokens = []

        # All non-stopwords tokens
        self.noun_phrases = []

        # Dict of scentences and tokens
        self.sentence_dict = {}

        # The intro sentences
        self.intro = []
        self.summarized_body = []

        # Used for frequency based methods
        self.tokens_freq = FreqDist()
        self.noun_phrase_freq = FreqDist()

        # Must parse first
        self.parsed = False

    def parse(self):
        """
        Performs NLP methods
        :return:
        """

        self.refined_text_dict()
        self.all_tokens()
        self.all_noun_phrases()

        # Used for frequency based methods
        self.tokens_freq = FreqDist(self.tokens)

        self.noun_phrase_freq = FreqDist(self.noun_phrases)

        # Saves the intro sentences, and removes from dict
        self.remove_intro()

        self.parsed = True

    def keywords(self, number_keywords=15, get_all=False):
        """
        Gets tokens from freqeucny distribution
        :param number_keywords:
        :return:
        """

        if not self.parsed:
            raise SummaryException("Must call summarize first!")

        if get_all:
            keys = self.tokens_freq.most_common()
        else:
            keys = self.tokens_freq.most_common(number_keywords)

        # Loop to just get keywords not the counts
        keywords_list = []
        for word in keys:
            keywords_list.append(word[0])

        return keywords_list

    def key_noun_phrases(self, number_noun_phrases=5):
        """
        Gets tokens from freqeucny distribution
        :param number_noun_phrases:
        :return:
        """

        if not self.parsed:
            raise SummaryException("Must call summarize first!")

        keys = self.noun_phrase_freq.most_common(number_noun_phrases)

        # Loop to just get keywords not the counts
        noun_phrases_list = []
        for word in keys:
            noun_phrases_list.append(word[0])

        return noun_phrases_list

    def summarize(self):
        """
        Ajdusts the summary factor to meet the summary length requirements
        :return:
            Returns the summarized text
        """

        self.parse()

        max_attempts = 60

        summary_factor = 0.6

        success = False

        for i in range(max_attempts):
            self.summarize_body(summary_factor)

            size = (len(" ".join(self.summarized_body).split()) + len(" ".join(self.intro).split()))

            if size > self.maximum_length:
                summary_factor += 0.02

            if size < self.minimum_length:
                summary_factor -= 0.02

            if self.minimum_length <= size <= self.maximum_length:
                success = True
                break

        if success:
            return self.intro + self.summarized_body
        else:
            raise SummaryException("Could not summary meet length requirements after {0} attempts".format(max_attempts))

    def summarize_body(self, score_threshold_mulitplier):
        """
        Includes the first two scentences of the article
        Simple frequency summarizer takes a body of text to summarize using freqneucy counts
        :param stem:
            wether to stem words
        :param score_threshold_mulitplier:
            The avarage scentence score muliplier, so like 1.5 is like 1/4 of corpus
        :return:
            Summarized text as list of scentences
            Returns list of lemmatized keywords
            Returns [], [] on summary error, like no tokens in text
        """

        summarized = []

        # Scores given by occurences or non-stopwords divided by num words
        scentence_scores = {}
        for sentence, scentence_tokens in self.sentence_dict.items():
            score = 0
            for tok in scentence_tokens:
                score += self.tokens_freq[tok]

            if len(scentence_tokens) == 0:
                scentence_scores[sentence] = 0
            else:
                score = score / len(scentence_tokens)
                scentence_scores[sentence] = score

        avarage_score = 0  # Used as threshold
        for sent, score in scentence_scores.items():
            avarage_score += score

        # Some error casing zero scores
        if avarage_score == 0:
            raise SummaryException
        else:
            avarage_score = avarage_score / len(scentence_scores.keys())

            for sent, score in scentence_scores.items():
                if score > avarage_score * score_threshold_mulitplier:
                    summarized.append(sent)

            self.summarized_body = summarized

    def refined_text_dict(self, stem=True):
        """
        Creates a dict of the scentences and the processed tokens in the sentences
        Removes stopwords and can stem
        :return:
            Sets a dict of tokens of the sentences and tokens
        """

        sentence_tokenized = sent_tokenize(self.text)

        sentence_tokenized = self.remove_nonbody_scentences(sentence_tokenized)

        # Initilize dict from keys, with [ ] as initial value
        scentence_dict = dict([(key, []) for key in sentence_tokenized])

        all_tokens = []

        # Simple loop to tokenize and add words to the sent dict, hashed by the words in sent
        for sent in sentence_tokenized:
            tokens = self.get_non_stopwords(sent, stem=stem)
            scentence_dict[sent] = tokens

        # Returns all tokens, used for Freq Distribution
        for scentence, scentence_tokens in scentence_dict.items():
            for tok in scentence_tokens:
                all_tokens.append(tok)

        if len(" ".join(scentence_dict.keys()).split()) < self.minimum_length:
            raise SummaryException("Not enough text to summarize!")

        self.sentence_dict = scentence_dict

    def all_tokens(self):

        # Get all tokens
        for scentence, scentence_tokens in self.sentence_dict.items():
            for tok in scentence_tokens:
                if self.is_text_token(tok):
                    self.tokens.append(tok)

    def all_noun_phrases(self):

        # Get noun phrases, ensure length greater than 1
        noun_phrases = self.get_noun_phrases(self.text)
        self.noun_phrases = [phrase for phrase in noun_phrases if len(phrase.split()) > 1]

    def remove_nonbody_scentences(self, sentences):
        """
        Takes tokenized scentences list and remove things like headers, or substitiles.
        Checks sentences that resemble Social media captions or Getty images
        :param sentences:
        :return:
        """

        refined_sentences = []

        # Make sure things like tweet or intros not present
        # TODO: Improve first sentence extraction
        for index, sent in enumerate(sentences):

            sent = sent.rstrip()

            is_valid = True

            if index == 0:
                try:
                    intro = sent[(sent.index("\n\n") + 2):]
                except (IndexError, ValueError):
                    intro = sent

                # Check if refined intro is still bad
                for token in self.non_body_sentence_blacklist:
                    if token in intro:
                        is_valid = False
                        break

                if is_valid:
                    refined_sentences.append(intro)

            else:
                for token in self.non_body_sentence_blacklist:
                    if token in sent:
                        is_valid = False
                        break

                if is_valid:
                    refined_sentences.append(sent)

        return refined_sentences

    def remove_intro(self):
        # TODO: Improve method of including the first part of newpaper article, usally the most descriptive
        # TODO: Scraped text tends to include sales and stuff

        for i in range(self.include_intro):
            # Automatically includes first "n" scentences of text becuase it is descriptive

            try:
                first_scentence = list(self.sentence_dict.keys())[0]
            except IndexError:
                raise SummaryException("Not enough text for {0} intros".format(self.include_intro))

            self.intro.append(first_scentence)
            self.sentence_dict.pop(first_scentence)
