from flask import Flask, request
from flask_cors import CORS
import json, requests

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

"""
Route takes the url to analyze and the action to perform on the url:
Action can be: 'summary', 'related_articles', 'explore_title'

1. Call the appropriate API to perform the action
2. Format the response for FB messenger, ie: Carusel + quick replies

Return the FB messenger template
:return:
"""

wyzefind_api_base_url = 'http://127.0.0.1:5001'

default_article_img = '...'


def format_explore_card(article):
    relation = 'More on: '

    terms = []
    if len(article['entities']) > 0:
        terms.append(article['entities'][0]['label'])

    if len(article['concepts']) > 0:
        for concept in article['concepts']:
            terms.append(concept['label'])

    print(terms)
    terms = relation + ", ".join(terms[:4])
    print(terms)

    return {
        "title": terms,
        "image_url": article['img_url'],
        "subtitle": article['title'],
        "buttons": [
            {
                "type": "web_url",
                "url": article['url'],
                "title": "Read"
            },
            {
                "set_attributes":
                    {
                        "titleToExplore": article['title'],
                        "urlToExplore": article['url'],
                    },
                "block_names": ["Explore Article"],
                "type": "show_block",
                "title": "Explore"
            }
        ]
    }


@app.route('/explore', methods=['GET'])
def explore_article_template():
    """
    Returns explore list template for a title
    :param url:
    :return:
    """

    is_valid = True

    url = request.args.get('urlToExplore')
    if url is None:
        is_valid = False

    try:
        api_request = {
            "article_url": url
        }
        api_response = requests.post(wyzefind_api_base_url + '/explore', json=api_request).json()
    except Exception:
        is_valid = False

    if is_valid:
        template = {
            "messages": [
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "image_aspect_ratio": "square",
                            "elements": [format_explore_card(article) for article in api_response["related"]]
                        }
                    }
                }
            ]
        }

    if not is_valid:
        template = {
            "messages": [
                {
                    "text": "Sorry, I could not process that title."}
            ]
        }
        response = app.response_class(
            response=json.dumps(template),
            status=200,
            mimetype='application/json'
        )

        return response

    else:
        response = app.response_class(
            response=json.dumps(template),
            status=200,
            mimetype='application/json'
        )

        return response


def format_article_card(article):
    return {
        "title": article['title'],
        "image_url": article['img_url'],
        "subtitle": article['summary'][:80] + "...",
        "buttons": [
            {
                "type": "web_url",
                "url": article['url'],
                "title": "Read"
            },
            {
                "set_attributes":
                    {
                        "titleToExplore": article['title'],
                        "urlToExplore": article['url'],
                    },
                "block_names": ["Explore Article"],
                "type": "show_block",
                "title": "Explore"
            }
        ]
    }


@app.route('/related', methods=['GET'])
def related_article_template():
    """
    Returns related articles template for URL
    :return:
    """

    is_valid = True

    url = request.args.get('analyzeURL1')
    if url is None:
        is_valid = False

    try:
        api_request = {
            "article_url": url
        }
        api_response = requests.post(wyzefind_api_base_url, json=api_request).json()
        print(api_response)
    except Exception:
        is_valid = False

    if is_valid:
        original_title = api_response["initial"][0]["title"]

        template = {
            "messages": [
                {"text": "Related to {0}".format(original_title)},
                {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "image_aspect_ratio": "square",
                            "elements": [format_article_card(article) for article in api_response["related"]]
                        }
                    }
                }
            ]
        }

    # # TODO: call API
    # template = {
    #     "messages": [
    #         {
    #             "attachment": {
    #                 "type": "template",
    #                 "payload": {
    #                     "template_type": "button",
    #                     "text": title,
    #                     "buttons": [
    #                         {
    #                             "type": "web_url",
    #                             "url": "https://rockets.chatfuel.com",
    #                             "title": "Read"
    #                         },
    #                         {
    #                             "set_attributes":
    #                                 {
    #                                     "titleToAnalyze": title,
    #                                 },
    #                             "block_names": ["Explore Article"],
    #                             "type": "show_block",
    #                             "title": "Explore"
    #                         }
    #                     ]
    #                 }
    #             }
    #         }
    #     ]
    # }

    print(template)

    if not is_valid:
        template = {
            "messages": [
                {
                    "text": "Sorry, I could not process that URL."}
            ]
        }
        response = app.response_class(
            response=json.dumps(template),
            status=200,
            mimetype='application/json'
        )

        return response

    else:
        response = app.response_class(
            response=json.dumps(template),
            status=200,
            mimetype='application/json'
        )

        return response


@app.route('/summary', methods=['GET'])
def summary_template():
    """
    Returns summary template for URL
    :param url:
    :return:
    """

    is_valid = True

    url = request.args.get('analyzeURL1')
    if url is None:
        is_valid = False

    try:
        api_request = {
            "article_url": url
        }
        api_response = requests.post(wyzefind_api_base_url, json=api_request).json()
        initial_article = api_response["initial"][0]

    except Exception:
        is_valid = False

    if is_valid:
        # TODO: call API
        template = {
            "messages": [
                {
                    "text": "Here is a {0} word summary".format(len(initial_article["summary"].split()))},
                {
                    "text": initial_article["summary"]},
            ]
        }

    if not is_valid:
        template = {
            "messages": [
                {
                    "text": "Sorry, I could not process that URL."}
            ]
        }
        response = app.response_class(
            response=json.dumps(template),
            status=200,
            mimetype='application/json'
        )

        return response

    else:
        response = app.response_class(
            response=json.dumps(template),
            status=200,
            mimetype='application/json'
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
