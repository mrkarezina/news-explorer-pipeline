from flask import Flask, request
from google.cloud import storage
from google.api_core.exceptions import NotFound

app = Flask(__name__)

"""
App Engine server used to fetch a JSON Vis.js Graph file from cloud storage and return as it proper JSON response.
"""


@app.route('/demo', methods=['GET'])
def handle_graph_request():
    # The Url parameter should contain the name of the dataset to get from the google storage.
    demo_data_set = request.args.get("data_set")

    storage_client = storage.Client.from_service_account_json(
        'service_account.json')
    dataset_bucket = storage_client.get_bucket('vecgraph-demo')

    try:
        # Gets the graph dataset (json dump) from bucket
        blob = dataset_bucket.blob(demo_data_set + ".json")
        data = blob.download_as_string()

        response = app.response_class(
            response=data,
            status=200,
            mimetype='application/json'
        )

    except NotFound:

        response = app.response_class(
            status=404,
        )

    return response


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == '__main__':
    # Test: http://127.0.0.1:5000/demo?data_set=cnn

    app.run(debug=True)
