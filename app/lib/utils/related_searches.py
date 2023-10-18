from bs4 import BeautifulSoup
import requests
import re

# def get_related_searches(query):
#     # Send a GET request to Google Search
#     google_search = requests.get("https://www.google.com/search?q=" + query)
#     soup = BeautifulSoup(google_search.text, "html.parser")

#     # Find the related searches section
#     related_search_section = soup.find_all("div", class_="BNeawe")
#     related_searches = []
#     found_related_searches = False

#     # Extract the related searches after the "Related searches" section
#     for relate in related_search_section:
#         if relate.get_text() == "Related searches":
#             found_related_searches = True
#         elif found_related_searches:
#             related_searches.append(relate.get_text())

#     return related_searches





def get_related_searches(keyword, language):
    
    api_volumes_dict = [
        {
            "keyword": keyword,
            "language": language.lower(),
            "check_api": "no",
            "api_volume": None
        }
    ]
        
    length = len(api_volumes_dict)
    search_options = ["","",""]
    # search_options = [""]
    api_and_google_volumes_dict_list = []
    for i,element in enumerate(api_volumes_dict,start=1):
        for search_option in search_options:
            language = element.get("language")
            # print(language,"@@@@@")
            keyword = element.get("keyword")
            if search_option == "exact-paragraph":
                keyword = f"{keyword}"
            
            search_term = search_option + keyword.replace(" ", "+")

            # url = f"https://www.google.com/search?q={search_term}&hl={language}"
            if language == 'polish':
                url = f"https://www.google.com/search?&q={search_term}&oq={search_term}&hl=pl&gl=pl"
                # url = f"https://www.google.com/search?q={search_term}&tbs=lr:lang_1pl&lr=lang_pl&hl=pl"
                headers = {
                    'authority': 'www.google.pl',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-US,en;q=0.9',
                    'referer': 'https://www.google.pl/',
                    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                    'sec-ch-ua-arch': '"x86"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-full-version': '"111.0.5563.112"',
                    'sec-ch-ua-full-version-list': '"Google Chrome";v="111.0.5563.112", "Not(A:Brand";v="8.0.0.0", "Chromium";v="111.0.5563.112"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                }
                
            else:
                url = f"https://www.google.com/search?q={search_term}&tbs=lr:lang_1en&lr=lang_en&hl=en"
                headers = {
                    'authority': 'www.google.com',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-US,en;q=0.9',
                    'referer': 'https://www.google.com/',
                    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
                    'sec-ch-ua-arch': '"x86"',
                    'sec-ch-ua-bitness': '"64"',
                    'sec-ch-ua-full-version': '"111.0.5563.112"',
                    'sec-ch-ua-full-version-list': '"Google Chrome";v="111.0.5563.112", "Not(A:Brand";v="8.0.0.0", "Chromium";v="111.0.5563.112"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-model': '""',
                    'sec-ch-ua-wow64': '?0',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                }
            payload={}

            response = requests.request("GET", url, headers=headers, data=payload)
            
            # html = response.content.decode('utf-8')
            
            html = BeautifulSoup(response.content, 'html.parser')

            related_search = html.find_all("div", class_="s75CSd")

            related_searches = [relate.get_text() for relate in related_search[:-1]]
            
            api_and_google_volumes_dict_list.append(related_searches)
            
            
    unpacked_list = [item for sublist in api_and_google_volumes_dict_list for item in sublist]

    related_searches = list(dict.fromkeys(unpacked_list))
    return related_searches
