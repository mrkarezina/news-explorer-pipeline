import pickle
import json
from google.cloud import storage
import nltk
import gc

from Summarizer import Summarizer, SummaryException

# Load nltk dependecies
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Load Doc2Vec model
storage_client = storage.Client.from_service_account_json(
    'service_account.json')

dataset_bucket = storage_client.get_bucket('gensim-models')

blob = dataset_bucket.blob("health_doc2vec")
data = blob.download_as_string()
model = pickle.loads(data)

# Ensure string data deleted to reduce memory
del blob
del data
gc.collect()

# model = pickle.load(open('/Users/milanarezina/PycharmProjects/Wyzefind/tech_doc2vec', 'rb'))

number_noun_phrase = 10
number_keywords = 50


def process_text(text):
    """
    Tries to get the summary, intro, keywords
    Return is_valid indicating if text was okay
    :param text:
    :param title:
    :return:
    """

    is_valid = True

    keywords = []
    summarizer = Summarizer(text)
    try:
        summary = summarizer.summarize()

        keywords = summarizer.keywords(number_keywords=number_keywords)
        phrases = summarizer.key_noun_phrases(number_noun_phrases=number_noun_phrase)
        phrases = [phrase.replace(" ", "_") for phrase in phrases]

        keywords = keywords + phrases

    except SummaryException:
        summary = [""]
        is_valid = False

    summary = " ".join(summary)

    return is_valid, summary, keywords


def get_embedding(keywords):
    """
    Dov2vec embedding from keywords
    :param keywords:
    :return:
    """

    embedding = model.infer_vector(keywords).tolist()

    return embedding


def process_language(request):
    """
    Route takes the Text data from the post request:
    1. NLP preprocessing to produce keywords
    2. Infer gensim vector

    Return a list formated vector in json
    Returns the number of tokens used in making the vector
    :return:
    """

    data_dict = request.get_json()
    # data_dict = request

    try:
        text = data_dict["text"]
    except KeyError:
        return 'Bad params'

    if len(text.split()) > 12000:
        return 'To many tokens, max 12000'

    is_valid, summary, keywords = process_text(text)

    if not is_valid:
        return 'Summary Error'

    else:
        embedding = get_embedding(keywords)

        response = {
            "summary": summary,
            "embedding": embedding,
        }

        response = json.dumps(response)
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        return response, headers
