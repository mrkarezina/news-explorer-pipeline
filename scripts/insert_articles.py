from knowledge_graph.graph_insertion import ArticleInserter
from knowledge_graph.article_processor import article_processor
from neo4j.exceptions import ConstraintError
from py2neo import ClientError
import time

from knowledge_graph.config import DB_IDS, TIMEOUT, MAX_ARTICLES

# Becuase of weird connection to Neo4j
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

article_inserter = ArticleInserter(DB_IDS)


def process_article(request):
    # data_dict = request.get_json()
    data_dict = request

    try:
        url = data_dict["url"]
    except KeyError:
        return 'Bad params'

    article_dict, is_valid = article_processor(url=url)

    title = article_dict["title"]
    if is_valid:
        try:
            article_inserter.db_insert(article_dict)
        except (ConstraintError, ClientError):
            print(f"Error inserting article into DB: {title}")
    else:
        print(f"Article is not valid: {title}.")

    time.sleep(TIMEOUT)


# process_article({
#     'url': 'https://techcrunch.com/2019/07/21/lyft-e-bikes-san-francisco/'
# })

def load_articles(file):
    """
    Loads article urls from file
    :param file:
    :return:
    """

    with open(file, 'r') as urls:
        for i, url in enumerate(urls):
            if i < MAX_ARTICLES:
                process_article({
                    'url': url.rstrip()
                })
            else:
                break


load_articles('techcrunch_links.txt')
