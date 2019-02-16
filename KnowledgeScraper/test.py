import newspaper

# n = newspaper.build("https://www.technologyreview.com", memoize_articles=False, dry=False)
#
# for article in n.articles:
#     print(article.url)



paper = newspaper.Article('https://www.health.harvard.edu/blog/parents-dont-always-realize-that-their-teen-is-suicidal-2019021315901')
paper.download()
paper.parse()
print(paper.url)
print(paper.text)