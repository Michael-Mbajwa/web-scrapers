import re
from urllib.request import urlopen
from urllib.request import urlretrieve
import geopandas
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import certifi
import ssl
import datetime
import random
import requests
import csv
import re
import json
import pandas as pd
import plotly.express as px


# Remember to add exception handling
def get_links(articleurl):
    """
    A single function that takes in a wikipedia article URL of the form /wiki/<Article_name>
    and returns a list of all linked article URLs in the same form.
    :param articleurl: A wikipedia article URL of the form /wiki/<Article_name>
    :return:
    """
    try:
        html = urlopen('http://en.wikipedia.org{0}'.format(articleurl),
                       context=ssl.create_default_context(cafile=certifi.where()))
    except HTTPError:
        print('URL could not be found. Check URL.')
    except URLError:
        print('Server could not be found.')
    else:
        print('\nCorrect. Continuing...')

    bs = BeautifulSoup(html.read(), 'html.parser')
    try:
        getlinks = bs.find('div', {'id': 'bodyContent'}).find_all('a',
                                                                  href=re.compile('^(/wiki/)((?!:).)*$'))
    except AttributeError as e:
        print(e)
    else:
        return getlinks


links = get_links('/wiki/Kevin_Bacon')

# Chooses a random link from get_links and calls get_links again continuously until you stop the program.
while len(links) > 0:
    newArticle = links[random.randint(0, len(links) - 1)].attrs['href']
    print(newArticle)
    links = get_links(newArticle)
'''



'''
# A webcrawler that can go anywhere on the internet
random.seed(datetime.datetime.now())
pages = set()


# Retrieves a list of all internal links found on a page
def get_internal_links(bs, include_url):
    include_url = '{0}://{1}'.format(urlparse(include_url).scheme,
                                     urlparse(include_url).netloc)
    # The above code combines foe example both http:// with oreilly.com.
    # This is a bit redundant as lines 94-95 already do this before passing it to the get internal links function
    internal_links = []
    # finds all links that begin with a /
    links = bs.find_all('a', href=re.compile('^(/|.*' + include_url + ')'))
    for link in links:
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internal_links:
                if link.attrs['href'].startswith('/'):
                    internal_links.append(include_url + link.attrs['href'])
                else:
                    internal_links.append(link.attrs['href'])

    return internal_links


# Retrieves a list of all external links found in a page
def get_external_links(bs, exclude_url):
    external_links = []  # You could use a set and avoid code in line 42
    links = bs.find_all('a', href=re.compile('^(http|wwww)((?!' + exclude_url + ').)*$'))
    for link in links:
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in external_links:
                external_links.append(link.attrs['href'])

    return external_links


# To get a random external link
def random_external_link(starting_page):
    html = urlopen(starting_page, context=ssl.create_default_context(cafile=certifi.where()))
    bs = BeautifulSoup(html.read(), 'html.parser')
    external_links = get_external_links(bs, urlparse(starting_page).netloc)
    # netloc removes http and returns only x.com e.g http://oreilly.com becomes just oreilly.com
    if len(external_links) == 0:
        print('No external links found, looking around the site for one.')
        domain = '{0}://{1}'.format(urlparse(starting_page).scheme,
                                    urlparse(starting_page).netloc)
        # The above code combines for example both http:// with oreilly.com
        # It is now sent to the internal links function so more internal links can be found
        internal_links = get_internal_links(bs, domain)
        # internal_links returns a list of internal links
        return random_external_link(internal_links[random.randint(0, len(internal_links) - 1)])
        # a random internal link is selected and sent to random external link in order to
        # see if this page has an external link
    else:
        # if external links were previously found, a random external link is returned by the function
        return external_links[random.randint(0, len(external_links) - 1)]


def follow_external_only(starting_site):
    external_link = random_external_link(starting_site)
    print('Random external link is: {}'.format(external_link))
    follow_external_only(external_link)  # Recursive function.


"""


"""


# Code that collects data from NYTimes and brookings
class Content:
    def __init__(self, url, title, body):
        self.url = url
        self.title = title
        self.body = body


def get_page(url):
    req = requests.get(url)
    return BeautifulSoup(req.text, 'html.parser')


def scrape_ny_times(url):
    bs = get_page(url)
    title = bs.find('h1').text
    lines = bs.find_all('p', {'class': 'story_content'})
    body = '\n'.join([line.text for line in lines])
    return Content(url, title, body)


def scrape_brookings(url):
    bs = get_page(url)
    title = bs.find('h1').text
    body = bs.find('div', {'class': 'post-body'}).text
    return Content(url, title, body)


url1 = 'https://www.brookings.edu/blog/future-development/' \
      '2018/01/26/delivering-inclusive-urban-access-3-uncomfortable-truths/'
content = scrape_brookings(url1)

url2 = 'https://www.nytimes.com/2018/01/25/opinion/sunday/silicon-valley-immortality.html'
content2 = scrape_ny_times(url2)
"""



"""


# Organized news scraping function
class Content:
    """
    Common base class for all articles
    """
    def __init__(self, url, title, body):
        self.url = url
        self.title = title
        self.body = body

    def print(self):
        """
        flexible printing option
        """
        print('URL: {0}'.format(self.url))
        print('TITLE: {0}'.format(self.title))
        print('BODY: \n{0}'.format(self.body))


class Website:
    """
    Contains information about the website structure and nothing more.
    """
    def __init__(self, name, url, title_tag, body_tag):
        self.name = name
        self.url = url
        self.title_tag = title_tag
        self.body_tag = body_tag


class Crawler:
    """
    This class collects no parameters.
    This is where the main work is done by the crawler.
    """
    def get_page(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'html.parser')

    def safe_get(self, page_obj, selector):
        """
        Utility function used to get a content string from a Beautiful Soup object and a selector.
        Returns an empty string if no object is found for the given selector """
        selected_elems = page_obj.select(selector)
        # The page_obj is the bs produced from using BeautifulSoup
        # The selector is any information required from the Website class
        if selected_elems is not None and len(selected_elems) > 0:
            return '\n'.join([elem.get_text() for elem in selected_elems])
        # Because selector returns your information as a list, you have to loop through the list,
        # pick your text and join it to a string which can be ''.
        else:
            return ""

    def parse(self, site, url):
        """
        Extracts content from a given webpage.
        Parse method takes the information stored about the website in the Website class,
        and also takes the URL to be crawled.
        """
        bs = self.get_page(url)  # The get_page method is called.
        if bs is not None:
            title = self.safe_get(bs, site.title_tag)
            # When you say site.title_tag, you are calling the title_tag parameter in the Website class
            body = self.safe_get(bs, site.body_tag)
            # When you say site.body_tag, you are calling the body_tag parameter in the Website class
            if title != '' and body != '':
                content = Content(url, title, body)
                # In the code above, you now call the Content class and pass it the three required arguments.
                content.print()


crawler = Crawler()  # The Crawler class is called. Remember that class requires no arguments.

site_data = [['O\'Reilly Media', 'http://oreilly.com', 'h1', 'section#product-description'],
             ['Reuters', 'http://reuters.com', 'h1', 'div.StandardArticleBody_body_1gnLA'],
             ['Brookings', 'http://www.brookings.edu', 'h1', 'div.post-body'],
             ['New York Times', 'http://nytimes.com', 'h1', 'p.story-content']]

websites = []
for data in site_data:
    websites.append(Website(data[0], data[1], data[2], data[3]))
    # Based on the four lists in the site_data list, a class of Website is formed from each list
    # Each list has four items which is passed to the website class as [name, url, title_tag, body_tag]
    # Each class formed is now stored in the empty websites list on line 238

web_links = ['http://shop.oreilly.com/product/0636920028154.do',
             'http://www.reuters.com/article/us-usa-epa-pruitt-idUSKBN19W2D0',
             'https://www.brookings.edu/blog/techtank/2016/03/01/idea-to-retire-old-methods-of-policy-education/',
             'https://www.nytimes.com/2018/01/28/business/energy-environment/oil-boom.html']
# Each weblink to be crawled is stored in the web_links list.
# A good point to note is web_links and websites must have the same length else,
# the code won't effectively work

if len(websites) == len(web_links):
    for i in range(len(websites)):
        crawler.parse(websites[i], web_links[i])  # To start the code, we pass the website class and
        # it's associated weblink to the .parse() method in the Crawler class.

"""



"""
# A well structured and expandable website crawler that can gather links and discover data in an automated way
class Content:
    """
    Common base class for all articles/pages
    """

    def __init__(self, topic, url, title, body):
        self.topic = topic
        self.url = url
        self.title = title
        self.body = body

    def print(self):
        """
        flexible printing method
        """
        print('New article found for topic: {0}'.format(self.topic))
        print('URL: {0}'.format(self.url))
        print('TITLE: {0}'.format(self.title))
        print('BODY: \n{0}'.format(self.body))


class Website:
    """
    Contains information about the website structure
    """

    def __init__(self, name, url, search_url, result_listing, result_url,
                 absolute_url, title_tag, body_tag):
        self.name = name
        self.url = url
        self.search_url = search_url
        self.result_listing = result_listing
        self.result_url = result_url
        self.absolute_url = absolute_url
        self.title_tag = title_tag
        self.body_tag = body_tag


class Crawler:

    def get_page(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'html.parser')

    def safe_get(self, page_obj, selector):
        """
        Utility function used to get a content string from a Beautiful Soup object and a selector.
        Returns an empty string if no object is found for the given selector """
        child_obj = page_obj.select(selector)
        if child_obj is not None and len(child_obj) > 0:
            return child_obj[0].get_text()
        else:
            return ""

    def search(self, topic, site):
        """Searches a given website for a given topic and records all pages found"""
        bs = self.get_page(site.search_url + topic)
        search_results = bs.select(site.result_listing)
        for result in search_results:
            url = result.select(site.result_url)[0].attrs['href']
            # Let's check to see if it's a relative or absolute url
            if (site.absolute_url):
                bs = self.get_page(url)
            else:
                bs = self.get_page(site.url + url)
            if bs is None:
                print('Something is wrong with that page or url. Skipping')
                return
            title = self.safe_get(bs, site.title_tag)
            body = self.safe_get(bs, site.body_tag)
            if title != '' or body != '':
                content = Content(url, title, body)
                content.print()


crawler = Crawler()

site_data = [['O\'Reilly Media', 'http://oreilly.com', 'https://ssearch.oreilly.com/?q=',
              'article.product-result', 'p.title a', True, 'h1', 'section#product-description'],

             ['Reuters', 'http://reuters.com', 'http://www.reuters.com/search/news?blob=',
              'div.search-result-content','h3.search-result-title a', False, 'h1',
              'div.StandardArticleBody_body_1gnLA'],

             ['Brookings', 'http://www.brookings.edu', 'https://www.brookings.edu/search/?s=',
              'div.list-content article', 'h4.title a', True, 'h1','div.post-body']]

sites = []
for row in site_data:
    sites.append(Website(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

topics = ['python', 'data science']
for topic in topics:
    print('GETTING INFO ABOUT: ' + topic)
    for target_site in sites:
        crawler.search(topic, target_site)


# A scraper that scraps a table from wikipedia
url = 'https://en.wikipedia.org/wiki/Comparison_of_text_editors'
html = urlopen(url)
bs = BeautifulSoup(html.read(), 'html.parser')
tables = bs.find('table', {'class': 'wikitable'})
rows = tables.find_all('tr')

csv_file = open('editors.csv', 'w+')
writer = csv.writer(csv_file)
for row in rows:
    csv_row = []
    cells = row.find_all(['td', 'th'])
    for cell in cells:
        csv_row.append(cell.get_text())
    writer.writerow(csv_row)

csv_file.close()



# Let’s look at one example of how data from APIs can be used in conjunction with web scraping to see
# which parts of the world contribute the most to Wikipedia.
# Gather many points of geographic data about Wikipedia edits and where they occur?

# Let's first get all links
url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
html_read = urlopen(url)
bs = BeautifulSoup(html_read.read(), 'html.parser')
all_links = bs.find('div', {'id': 'bodyContent'}).find_all('a', href=re.compile('^(/wiki/)((?!:).)*$'))
# After running Links, I picked a random link called '/wiki/History_of_Python'

# Let's get history IPs for /wiki/History_of_Python
link = '/wiki/History_of_Python'
page_url = re.sub('/wiki/', '', link)
history_url = 'http://en.wikipedia.org/w/index.php?title={}&action=history'.format(page_url)
html = urlopen(history_url)
bs = BeautifulSoup(html.read(), 'html.parser')

ip_addresses = bs.find_all('a', {'class': 'mw-anonuserlink'})
address_list = set(ip_address.get_text() for ip_address in ip_addresses)


# Let's get countries associated with each IP
countries = []
for ip in address_list:
    try:
        response = urlopen('https://api.ipgeolocation.io/ipgeo?apiKey=963aafbffe4d4f7f9cbefdafad2002bb&ip={0}'.
                           format(ip))
    except HTTPError:
         response is None
    if response is not None:
        response = response.read().decode('utf-8')
        response_json = json.loads(response)
        countries.append([response_json['country_name'], response_json['latitude'], response_json['longitude'],
                           response_json['continent_name'], response_json['country_code2']])


world = pd.DataFrame(countries, columns=['country_name', 'latitude', 'longitude', 'continent_name', 'country_code2'])


fig = px.scatter_geo(world, lat='latitude', lon='longitude',
                     locations='country_code2', color='country_name',
                     projection='natural earth', hover_name='country_name')
fig.show()