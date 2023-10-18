import requests
from bs4 import BeautifulSoup
import hashlib
import uuid

proxies = {
    'http1': 'http://61.7.146.7:80',
    'http2': 'http://207.2.120.19:80',
    'http3': 'http://103.216.48.242:8080',
    'http4': 'http://168.187.72.71:80',
    'http5': 'http://168.187.72.71:8080',
    'http6': 'http://177.93.45.156:999',
}

class WebScraper:
    def __init__(self, proxies=None):
        self.headings = []
        self.proxies = proxies

    def scrape_headings(self, urls):
        for url in urls:
            try:
                headings_tree = self.get_headings_tree(url)
                self.add_headings(headings_tree)
                # print(f"Headings extracted from {url}")
            except Exception as e:
                # print(f"Error scraping headings from {url}: {e}")
                pass

    def get_headings_tree(self, url):
        response = requests.get(url, proxies=self.proxies)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        headings = []
        stack = []

        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = heading.get_text().strip()
            heading_level = int(heading.name[1])
            # heading_id = hashlib.sha1(heading_text.encode('utf-8')).hexdigest()
            heading_id = str(uuid.uuid4())
            
            # for check the incoming header tag text comes or not
            # print(heading_text)
            
            while stack and stack[-1]['level'] >= heading_level:
                stack.pop()

            current_heading = {
                'text': heading_text,
                'level': heading_level,
                'id': heading_id,
                'children': [],
                'prompt_id': None,
                'response': '',
                'keywords': '',
                'expanded': True,
                'is_completed': False,
                'more_info': '',
                'length': 500,
                'tag': 0
            }

            if stack:
                this_level = int(stack[-1]['tag']) + 1
                if this_level >= 6:
                    this_level = 5
                current_heading['tag'] = this_level
                stack[-1]['children'].append(current_heading)
            else:
                headings.append(current_heading)

            stack.append(current_heading)

        return headings

    # def get_headings_tree(self, url):
    #     response = requests.get(url, proxies=self.proxies)
    #     response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
    #     soup = BeautifulSoup(response.content, 'html.parser')

    #     headings = []
    #     existing_headings_text = set()
    #     stack = []

    #     for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    #         heading_text = heading.get_text().strip()
    #         heading_level = int(heading.name[1])
    #         heading_id = hashlib.sha1(heading_text.encode('utf-8')).hexdigest()

    #         if heading_text not in existing_headings_text:  # Check if the heading text is not already in the set
    #             existing_headings_text.add(heading_text)  # Add the heading text to the set to avoid duplicates

    #             while stack and stack[-1]['level'] >= heading_level:
    #                 stack.pop()

    #             current_heading = {
    #                 'tag': heading.name,
    #                 'text': heading_text,
    #                 'level': heading_level,
    #                 'id': heading_id,
    #                 'children': [],
    #                 'prompt_id': None,
    #                 'response': '',
    #                 'keywords': '',
    #                 'expanded': True,
    #                 'is_completed': False,
    #                 'more_info': '',
    #                 'length': 500,
    #                 'parent': 0
    #             }

    #             if stack:
    #                 this_level = int(stack[-1]['parent']) + 1
    #                 if this_level >= 6:
    #                     this_level = 5
    #                 current_heading['parent'] = this_level
    #                 stack[-1]['children'].append(current_heading)
    #             else:
    #                 headings.append(current_heading)

    #             stack.append(current_heading)

    #     return headings

    def add_headings(self, headings):
        self.headings.extend(headings)

    def get_headings(self):
        return self.headings

# Example usage (commented out for use in other code):

# s = WebScraper(proxies=proxies)
# urls_to_scrape = ["https://intymnapolska.pl/jak-znalezc-kogos-na-tinderze/", "https://www.wikihow.com/Find-Someone-on-Tinder"]
# s.scrape_headings(urls_to_scrape)
