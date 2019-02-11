import newspaper

n = newspaper.build("https://www.technologyreview.com", memoize_articles=False, dry=False)

for article in n.articles:
    print(article.url)