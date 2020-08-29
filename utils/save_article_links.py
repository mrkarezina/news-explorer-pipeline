import requests
import re


def check_susbstrings(link, substrings):
    """
    Checks if link contains one of the substrings.
    """
    is_valid = False
    for sub in substrings:
        if sub in link:
            is_valid = True
            break
    return is_valid


def save_parsed_links(links, save_file):
    with open(save_file, 'w+') as file:
        for link in links:
            file.write(link + '\n')

    print('Number of links: {0}'.format(len(links)))


def save_sitemap_links(sitemap, substrings, file):
    """
    Saves the parsed links to file. Useful for creating list of links to be send to API for analysis.
    """
    xml = requests.get(xml_sitemap_link).text
    site_map_links = re.findall(
        '(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', xml)
    site_map_links = [
        x for x in site_map_links if check_susbstrings(x, substrings)]
    save_parsed_links(site_map_links, file)
    

substrings = ["cnn.com/2020/08/29", "cnn.com/2020/08/28"]
xml_sitemap_link = "https://www.cnn.com/article/sitemap-2020-8.html"
save_file = "articles/cnn_links.txt"
save_sitemap_links(xml_sitemap_link, substrings, save_file)
