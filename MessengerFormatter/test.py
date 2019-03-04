

request={'url': ''}

import requests
# from main import process_language
# process_language(request)

r = requests.post("https://us-central1-graph-intelligence.cloudfunctions.net/language-processor", json=request)
print(r.json())
print(r.status_code, r.reason)
print(r.text)