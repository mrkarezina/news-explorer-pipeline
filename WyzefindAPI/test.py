import requests

r = requests.post("https://ai-labs-226917.appspot.com/", json={'cloud_function': 'lyrics-generator', 'args': {'artist': 'Bruce Springsteen', 'lyric_length': 200, 'max_syllables': 16}})

print(r.status_code, r.reason)
print(r.text)