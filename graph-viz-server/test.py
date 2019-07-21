import requests

r = requests.post('https://us-central1-graph-intelligence.cloudfunctions.net/graph-viz-server', json={
    "data_set": "techcrunch"
})

print(r.text)