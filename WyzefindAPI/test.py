import requests

r = requests.post("http://127.0.0.1:5000/summary-related", json={'article_url': 'http://www.physiciansnewsnetwork.com/ximed/study-hospital-physician-vertical-integration-has-little-impact-on-quality/article_257c41a0-3a11-11e9-952b-97cc981efd76.html', 'user_id': 1})
print(r.status_code, r.reason)
print(r.text)


# url = 'https://messenger-formatter-dot-graph-intelligence.appspot.com/summary?analyzeURL1=https%3A%2F%2Fwww.cnn.com%2F2019%2F03%2F06%2Fuk%2Facid-attack-3-year-old-father-guilty-scli-gbr-intl%2F'
# print(requests.get(url).json())