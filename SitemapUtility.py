import newspaper
import json
import re
import requests
import time


class SitemapUtility:
    """
    Takes a site map and parses all the links.
    Can apply filters for which links to download.

    Most sites will have a /sitemap.xml file, which contains the sitemap files
    Get the XML which contains all the links to the posts on the site.

    Can also use https://xmlsitemapgenerator.org to generate a sitemap

    Can use Utility to print all links or to scrape links and save to JSON file
    """

    # Need to create agent or sites block your reqeust
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW32)'}

    def __init__(self, xml_sitemap_link, required_substrings, parse_sitemaps=False,
                 number_articles_to_save=5):

        """
        :param xml_sitemap: Link to XML sitemap
        :param number_articles_to_save:
        :param parse_sitemaps: If sitemap link composed of more sitemaps (can load and parse each of those sub-maps individually)
        """

        # Links must contain one of these substrings to be considered for insertion
        self.required_article_substrings = required_substrings

        self.black_listed_substrings = ["#respond", "pinterest.com", "plus.google", "facebook.com", "/comment",
                                        "/email", "#comment", "share=", "wp-admin", ".jpeg", ".png", ".jpg", ".mp4",
                                        ".mp3", '.gif', '/tag/']

        self.content = []

        self.visited = []

        self.filtered_links = []

        self.xml_sitemap_link = xml_sitemap_link

        self.number_articles_to_save = number_articles_to_save

        # Download 20 at a time
        self.async_download = 50

        if parse_sitemaps:
            maps = self.load_site_maps()

            for map in maps:
                try:
                    xml = requests.get(map).text
                    self.load_links_xml(xml)
                    print('Downloaded sitemap: {0}'.format(map))
                except:
                    print('Failed sitemap: {0}'.format(map))
        else:
            map = requests.get(self.xml_sitemap_link).text
            self.load_links_xml(map)

    def get_parsed_links(self):

        for link in self.filtered_links:
            print(link)

        print('Number links: {0}'.format(len(self.filtered_links)))
        return self.filtered_links

    def save_parsed_links(self, save_file):
        """
        Saves the parsed links to file. Useful for creating list of links to be send to API for analysis.
        :return:
        """

        with open(save_file, 'w+') as file:
            for link in self.filtered_links:
                file.write(link + '\n')

        print('Number links: {0}'.format(len(self.filtered_links)))
        return self.filtered_links

    def save_scraped_links(self, json_save_file, timeout=5):

        """
        :param timeout: How long to wait in between scraping links
        Save the content from scraped links into JSON file
        :return:
        """

        for i, link in enumerate(self.filtered_links):

            if i < self.number_articles_to_save:
                self.scrape_link(link)
                time.sleep(timeout)

            if i % 100 == 0:
                self.save_json(json_save_file)

        self.save_json(json_save_file)

    def check_required_substrings(self, link, substrings):

        is_valid = False
        for sub in substrings:
            if sub in link:
                is_valid = True
                break

        return is_valid

    def check_blacklist_substrings(self, link, substrings):

        is_valid = True
        for sub in substrings:
            if sub in link:
                is_valid = False
                break

        return is_valid

    def save_json(self, json_save_file):
        """
        Saves the scraped content to JSON file
        :return:
        """

        with open(json_save_file, 'w+') as outfile:
            json.dump(self.content, outfile)

    def load_site_maps(self):
        """
        Used to parse sitemap for more site map links
        :return:
        """

        xml = requests.get(self.xml_sitemap_link).text
        site_map_links = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', xml)

        return site_map_links

    def load_links_xml(self, xml_map):
        """
        Use regex to parse out the urls from the xml sitemap (Treat as text)
        :return:
        """

        links = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', xml_map)

        for link in links:

            if self.check_required_substrings(link, self.required_article_substrings):
                if self.check_blacklist_substrings(link, self.black_listed_substrings):
                    self.filtered_links.append(link)

    def scrape_link(self, link):

        """
        Tries to scrape the article from link
        :return:
        Success T/F
        """

        if link not in self.visited:
            is_valid = True

            # Parse the article url
            try:
                article = newspaper.Article(link)
                url = article.url

                self.visited.append(url)
                print(article.url)

                article.download()
            except:
                print("Download error")
                is_valid = False

            if is_valid:
                try:
                    article.parse()
                except newspaper.article.ArticleException:
                    is_valid = False
                    print('Failed parsing article: {0}'.format(url))

                if is_valid:
                    text = article.text
                    title = article.title
                    date = article.publish_date
                    img = article.top_image
                    meta_data = article.meta_data

                    a_content = dict()
                    a_content["text"] = text
                    a_content["title"] = title
                    a_content["url"] = url
                    a_content["img"] = img
                    a_content["date"] = str(date)

                    # try:
                    #     a_content["meta_data"] = json.dumps(meta_data)
                    #     a_content["keywords"] = meta_data['citation_keywords']
                    #     a_content["citation_abstract"] = meta_data['citation_abstract']
                    #     a_content["citation_author_email"] = meta_data['citation_author_email']
                    # except KeyError:
                    #     print('No meta data')

                    self.content.append(a_content)

                    return True

        return False


if __name__ == "__main__":
    sitemap_url = 'https://techcrunch.com/sitemap-97.xml'

    required_substrings = ['techcrunch']

    parse_sitemaps = False

    articles_to_save = 10

    sitemap = SitemapUtility(sitemap_url, required_substrings, parse_sitemaps, articles_to_save)

    links_save_file = "save-links.txt"
    sitemap.save_parsed_links(links_save_file)

    # content_save_file = "test-utility.json"
    # sitemap.save_scraped_links(content_save_file, timeout=0)
