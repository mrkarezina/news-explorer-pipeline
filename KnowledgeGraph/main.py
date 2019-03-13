from GraphInsertion import ArticleInserter
from ArticleProcessor import article_processor
from neo4j.exceptions import ConstraintError
from py2neo import ClientError
import time

# TODO: change in index / insert files
graph_url = "http://neo4j:Trebinje66@35.202.226.197:7474/db/data/"
# graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"

# Becuase of weird connection to Neo4j
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

db_ids = {
    'cluster_id': 1,
    'user_id': "findhealthtips"
}
article_inserter = ArticleInserter(db_ids)


def process_article(request):
    # data_dict = request.get_json()
    data_dict = request

    try:
        url = data_dict["url"]
    except KeyError:
        return 'Bad params'

    article_dict, watson_entities, is_valid = article_processor(url=url)

    print(article_dict)

    if watson_entities == {}:
        is_valid = False
        print('Not inserted')

    if is_valid:
        try:
            article_inserter.db_insert(article_dict, watson_entities, insert_topics=False)
        except (ConstraintError, ClientError):
            return 'Article already Exists in graph'

    time.sleep(4)


# process_article({
#     'url': 'https://www.findhealthtips.com/the-ab-belt-review/'
# })

def load_articles(file):
    """
    Loads article urls from file
    :param file:
    :return:
    """

    with open(file, 'r') as urls:
        for i, url in enumerate(urls):
            if i < 2000:
                process_article({
                    'url': url.rstrip()
                })
            else:
                break


load_articles('/Users/milanarezina/PycharmProjects/Wyzefind/KnowledgeGraph/Articles.txt')
