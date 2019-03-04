import newspaper
import requests
from KnowledgeGraph.WatsonEnrichment import watson_enricher

# Tech processor: language-processor
language_processor_api = 'https://us-central1-graph-intelligence.cloudfunctions.net/language-processor-health'

def fetch_article(url):
    """
    Downloads the article from URL
    :param url:
    :return:
    """

    is_valid = True

    try:
        article = newspaper.Article(url)
        article.download()
    except:
        print("Download error")
        is_valid = False

    if is_valid:
        try:
            article.parse()
        except newspaper.article.ArticleException:
            is_valid = False

        if is_valid:
            title = article.title
            text = article.text
            date = article.publish_date
            img = article.top_image

            return {
                'text': text,
                'title': title,
                'date': str(date),
                'img_url': img,
                'url': url,
            }


def process_language(text):
    """
    Fetch from language processing API (cloud function)
    :param text:
    :return:
    """

    # The language processing seems to fail without acsii decoding, ie remove emoji and chinese characters
    request = {
        'text': text.encode("ascii", errors="ignore").decode()
    }

    response = requests.post(language_processor_api,
                             json=request)

    return response.json()


def article_processor(url):
    """
    Used to process and enrich text to be suitable for knowledge graph
    :param text:
    :return:
        Returns dict containing enritched entites dict, document embedding, and summary
    """

    is_valid = True

    article_dict = fetch_article(url)
    enriched_knowledge = {}

    try:
        if len(article_dict['text'].split()) < 100:
            is_valid = False

        processed_language = process_language(article_dict['text'])
        enriched_knowledge = watson_enricher(article_dict['text'])

        article_dict['summary'] = processed_language['summary']
        article_dict['embedding'] = processed_language['embedding']
    except Exception as e:
        print(e)
        is_valid = False

    if not is_valid:
        print("Failed processing URL: {0}".format(url))

    return article_dict, enriched_knowledge, is_valid
