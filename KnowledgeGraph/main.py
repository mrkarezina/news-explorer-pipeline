from GraphInsertion import ArticleInserter
from ArticleProcessor import article_processor
from neo4j.exceptions import ConstraintError
from py2neo import ClientError
import time

# TODO: change in index / insert files
# graph_url = "http://neo4j:Trebinje66@35.192.121.170:7474/db/data/"
graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"

# Becuase of weird connection to Neo4j
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

db_ids = {
    'cluster_id': 1,
    'user_id': 1
}
article_inserter = ArticleInserter(db_ids)


def process_article(request):
    # data_dict = request.get_json()
    data_dict = request

    try:
        url = data_dict["url"]
    except KeyError:
        return 'Bad params'

    # try:
    article_dict, watson_entities, is_valid = article_processor(url=url)
    print(article_dict)

    time.sleep(5)

    if is_valid:
        try:
            article_inserter.db_insert(article_dict, watson_entities)
        except (ConstraintError, ClientError):
            return 'Article already Exists in graph'

    # except Exception as e:
    #     print(e.__traceback__)
    #     print("Failed processing: {0}".format(url))
    #     time.sleep(31)


# process_article({
#     'url': 'https://www.health.harvard.edu/blog/scary-news-about-childhood-obesity-2018030613439'
# })

def load_articles(file):
    """
    Loads article urls from file
    :param file:
    :return:
    """

    with open(file, 'r') as urls:
        for url in urls:
            process_article({
                'url': url.rstrip()
            })

load_articles('/Users/milanarezina/PycharmProjects/Wyzefind/KnowledgeGraph/Articles.txt')
