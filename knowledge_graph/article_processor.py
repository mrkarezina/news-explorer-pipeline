from knowledge_graph.article_downloader import Article
from knowledge_graph.config import LANGUAGE_PROCESSOR_API

import newspaper
import requests


# If less than 100 tokens retry parsing the article not cleaning dom
retry_article_parse_tokens = 100


def download(url, clean_doc=True):
    """
    Tries to download + parse the article using newspaper
    :param url:
    :return:
    """

    article = Article(url)
    is_valid = True

    try:
        article.download()
        article.parse(clean_doc=clean_doc)
    except newspaper.article.ArticleException:
        print("Download error")
        is_valid = False

    return article, is_valid


def fetch_article(url):
    """
    Downloads the article from URL
    :param url:
    :return:
    """

    article, is_valid = download(url)

    if is_valid:

        # Retry downloading article without cleaning
        if len(article.text.split()) < retry_article_parse_tokens:
            article, is_valid = download(url, clean_doc=False)

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

    response = requests.post(LANGUAGE_PROCESSOR_API, request)
    if type(response) is str:
        print(f"Language processing error {response}")
        response = {}
    return response


def article_processor(url):
    """
    Used to process and enrich text to be suitable for knowledge graph
    :param text:
    :return:
        Returns dict containing enritched entites dict, document embedding, and summary
    """

    is_valid = True

    article_dict = fetch_article(url)

    try:
        if len(article_dict['text'].split()) > 100:
            processed_language = process_language(article_dict['text'])
            article_dict['summary'] = processed_language['summary']
            article_dict['embedding'] = processed_language['embedding']
        else:
            print('To short article, lenght: {0}'.format(
                len(article_dict['text'].split())))
            is_valid = False

    except KeyError as e:
        print(e)
        is_valid = False

    return article_dict, is_valid
