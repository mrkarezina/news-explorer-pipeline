from knowledge_graph.visjs_formatter import GraphViz

app = Flask(__name__)

db_ids = dict()
db_ids["cluster_id"] = 1
db_ids["user_id"] = "cnn"
graph_db = GraphViz(db_ids)


@app.route('/demo', methods=['GET'])
def handle_graph_request():
    data = graph_db.format_graph_data()

    response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )

    return response


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run(debug=True)
