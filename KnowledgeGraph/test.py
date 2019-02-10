import newspaper

n = newspaper.build("https://www.infoworld.com/", memoize_articles=False, dry=False)

for article in n.articles:
    print(article.url)