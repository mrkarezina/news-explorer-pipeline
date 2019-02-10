from GraphInsertion import ArticleInserter
from ArticleProcessor import article_processor
from neo4j.exceptions import ConstraintError

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

    article_dict, watson_entities = article_processor(url=url)

    print(article_dict)
    print(watson_entities)

    try:
        article_inserter.db_insert(article_dict, watson_entities)
    except ConstraintError:
        return 'Article already Exists in graph'


process_article({
    'url': 'https://www.acefitness.org/education-and-resources/professional/expert-articles/5008/7-things-to-know-about-excess-post-exercise-oxygen-consumption-epoc'
})