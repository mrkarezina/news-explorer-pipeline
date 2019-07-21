from flask import Flask
import json
from google.cloud import storage
from google.api_core.exceptions import NotFound

app = Flask(__name__)


def fetch_dataset(request):
    """
    The Url parameter should contain the name of the dataset to get from the google storage
    :return:
    """

    data_dict = request.get_json()
    data_set = data_dict["data_set"]

    storage_client = storage.Client.from_service_account_json(
        'service_account.json')
    dataset_bucket = storage_client.get_bucket('vecgraph-demo')

    try:
        # Gets the graph dataset (json dump) from bucket
        blob = dataset_bucket.blob(data_set + ".json")
        data = blob.download_as_string()

    except NotFound:
        return 'Dataset not found'

    response = json.dumps(data)
    headers = {'Access-Control-Allow-Origin': '*'}

    return response, headers
