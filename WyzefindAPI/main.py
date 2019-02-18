from flask import Flask, request
from flask_cors import CORS
import json, requests

from ArticleProcessor import article_processor
from GraphFulfilment import GraphFulfilment

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

"""
Server for Wyzefind API:
-Analyzes document
-Performs Cypher queries
-
"""

# TODO: Add memcache
# TODO: Change TOPIC to Topic in cypher

db_ids = {
        'cluster_id': 1,
        'user_id': 1
    }

@app.route('/', methods=['POST'])
def get_related_articles():
    """
    Route takes the url of an article
    1. Downloads article
    2. Finds most similar articles by embedding
    3. Explain the relation between the most similar article and its most related articles
    :return:
    """

    data = request.data
    data_dict = json.loads(data)

    graph = GraphFulfilment(db_ids)

    try:
        article_url = data_dict["article_url"]
    except (KeyError):
        response = app.response_class(
            response='Proper parameter missing',
            status=400,
        )
        return response

    article_dict, is_valid = article_processor(url=article_url)
    if not is_valid:
        response = app.response_class(
            response='Error processing article',
            status=200,
        )
        return response

    most_related = graph.get_most_related_by_embedding(article_dict['embedding'])

    related_articles = {
        'initial': [{
            'title': article_dict['title'],
            'date': article_dict['date'],
            'url': article_dict['url'],
            'summary': article_dict['summary'],
        }],
        'related': []
    }

    for related in most_related:
        related_articles['related'].append(graph.get_article_data(related))

    print(json.dumps(related_articles, indent=2))

    response = app.response_class(
        response=json.dumps(related_articles),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/', methods=['GET'])
def nothing_here():
    """
    No resource to be returned on GET request
    :return:
    """

    response = app.response_class(
        status=200,
    )

    return response


if __name__ == '__main__':
    # Test:

    """
    curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"text":"Our Domestic Bliss is our way of having fun with the audience’s expectations of what they think this doggy doodle doo will be,” Feig told PEOPLE. “It’s a slice of Saturday Evening Post, a dollop of Bad Housekeeping and a generous sprinkling of the Haunted Mansion on top.Without Carter","password":"xyz"}' \
  https://graph-processing-server-dot-graph-intelligence.appspot.com/infer

    """

    # get_related_articles({
    #     'article_url': 'https://techcrunch.com/2019/02/18/apple-could-be-looking-for-its-next-big-revenue-model/'
    # })

    app.run(port=5000, debug=True)
