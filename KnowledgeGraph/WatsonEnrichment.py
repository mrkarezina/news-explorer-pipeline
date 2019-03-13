import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, CategoriesOptions, \
    ConceptsOptions


"""
10000 NLU units a month free

10000 characters is one data unit
NLU units = data units * number features

"""

def watson_enricher(text):
    """
    Calls IBM watson Natural Langauage understading API to enrich text
    :param text:
    :return:
    """

    # First thousand characters only
    text = text[:9999]

    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey='20cMYNyna85jQb4zYUn68el7s_ur4N9XZEYreXgCFPru',
        url='https://gateway-wdc.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2018-03-19'
    )

    # response = natural_language_understanding.analyze(
    #     text=text,
    #     features=Features(entities=EntitiesOptions(sentiment=True), concepts=ConceptsOptions(),
    #                       categories=CategoriesOptions())).get_result()
    response = natural_language_understanding.analyze(
        text=text,
        features=Features(entities=EntitiesOptions(sentiment=True), concepts=ConceptsOptions())).get_result()

    print(json.dumps(response, indent=2))

    return response