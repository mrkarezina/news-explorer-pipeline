from KnowledgeGraph.ArticleDownloader import Article

# def tag_visible(element):
#     if element.parent.name in [
#             'span', 'p', 'br', 'strong', 'b',
#             'em', 'i', 'pre', 'blockquote', 'img',
#             'h2', 'h3', 'h4', 'h5', 'h6']:
#         return True
#     if isinstance(element, Comment):
#         return False
#     return False
#
# r = requests.get('http://www.physiciansnewsnetwork.com/ximed/study-hospital-physician-vertical-integration-has-little-impact-on-quality/article_257c41a0-3a11-11e9-952b-97cc981efd76.html')
# soup = bs4.BeautifulSoup(r.text)
# texts = soup.findAll(text=True)
# # print(texts)
# visible_texts = filter(tag_visible, texts)
# print(" ".join(t.strip() for t in visible_texts))

t = Article("http://www.physiciansnewsnetwork.com/ximed/study-hospital-physician-vertical-integration-has-little-impact-on-quality/article_257c41a0-3a11-11e9-952b-97cc981efd76.html", verbose=True, keep_article_html=True)
t.download()
t.parse(clean_doc=False)
print(t.title)
print(t.publish_date)
print(t.text)

# print(t.meta_data)
# print(t.meta_data['citation_keywords'])
# print(t.meta_data['citation_abstract'])
#
# print(t.text)
# print(t.top_image)