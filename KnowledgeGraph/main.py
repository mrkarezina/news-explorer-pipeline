from GraphInsertion import ArticleInserter
from ArticleProcessor import article_processor
from neo4j.exceptions import ConstraintError
from py2neo import ClientError
import time

graph_url = "http://neo4j:Trebinje66@localhost:7474/db/data/"

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
#     'url': 'https://www.technologyreview.com/s/609223/robots-arent-as-smart-as-you-think/'
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
