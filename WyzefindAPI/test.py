import requests

# r = requests.post("http://127.0.0.1:5001/summary-related", json={'article_url': 'https://www.cnn.com/2019/03/06/uk/acid-attack-3-year-old-father-guilty-scli-gbr-intl/'})
# print(r.status_code, r.reason)
# print(r.text)


url = 'http://127.0.0.1:5000/summary?analyzeURL1=https%3A%2F%2Fwww.cnn.com%2F2019%2F03%2F06%2Fuk%2Facid-attack-3-year-old-father-guilty-scli-gbr-intl%2F'
print(requests.get(url).json())