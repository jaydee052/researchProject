from bs4 import BeautifulSoup
import requests, time
import os, csv
from urllib.parse import urljoin, urlparse


visited = set()
sites = ["https://www.politifact.com"]
csv_filename = 'misinformation.csv'


# Function to validate if the URL is within the same domain
def is_valid_url(url, base_url):
   parsed_base = urlparse(base_url)
   parsed_url = urlparse(url)
   return parsed_url.netloc == parsed_base.netloc


def log(title, personality, date, social_media, fact, factcheck_link, personality_link, to_visit_len):
   print("")
   print("<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>")
   print("Title:", title)
   print('Quoted by: ', personality)
   print('Posted on: ', date)
   print('Social Media used: ', social_media)
   print("Fact : ", fact)
   print("Fact check Url: ", factcheck_link)
   print("Personality Url: ", personality_link)
   print("Total links to visit: ", to_visit_len)
   print("<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>")
   print("")


def get_article_details(url):
   to_visit = [url]
   while to_visit:
       print("Total to visit: ", len(to_visit))
       current_url = to_visit.pop()
       if current_url not in visited:
           visited.add(current_url)
           try:
               response = requests.get(current_url)
               if response.status_code == 200:
                   soup = BeautifulSoup(response.text, 'html.parser')
                   personality = None
                   date = None
                   social_media = None
                   factcheck_link = None
                   personality_link = None
                   fact = None


                   section = soup.find('section', {'class': 'o-stage'})
                   if section:
                       print("---------------------------------------------------------")
                       for link in section.find_all("a"):
                           href = link.get("href")
                           if href:
                               #links.append(link)
                               if 'personalities' in href:
                                   personality = link.text.strip()
                                   personality_link = urljoin(url,href)
                                   if is_valid_url(personality_link, url) and personality_link not in visited and '#' not in personality_link:
                                       to_visit.append(personality_link)
                                   else:
                                       continue
                               if 'factchecks' in href:
                                   factcheck_link = urljoin(url,href)
                                   if is_valid_url(factcheck_link, url) and factcheck_link not in visited and '#' not in factcheck_link:
                                       to_visit.append(factcheck_link)
                                   else:
                                       continue


                       for divs in section.find_all('div', {"class": "m-statement__desc"}):
                           media = divs.text
                           if media:
                               date_arr = media.split()[2:5]
                               if date_arr:
                                   date = " ".join(date_arr).strip()
                               social_media_arr = media.split()[7:]
                               social_media = " ".join(social_media_arr).strip()




                       for divs in section.find_all('div', {"class": "m-statement__quote"}):
                           title = divs.text.strip()


                       # Extract image names
                       image_tags = section.find_all('img')
                       if image_tags:
                           image_names = [img['src'] for img in image_tags]
                           for image_name in image_names:
                               if 'https://static.politifact.com/politifact/rulings/' in image_name:
                                   if "true" in image_name:
                                       fact = 'True'
                                   elif 'meter-false.jpg' in image_name:
                                       fact = 'False'
                                   elif 'tom_ruling_pof.png' in image_name:
                                       fact = 'Pants on Fire'


                       log(title, personality, date, social_media, fact, factcheck_link, personality_link, len(to_visit))
                       add_to_csv(current_url, fact, title, personality, date, social_media)                           
                       print("---------------------------------------------------------")
                   else:
                       print("Section not found")


                   articles = soup.find_all('article')
                   print("Total number of articles: ", len(articles))
                   for article in articles:
                       for link in article.find_all("a"):
                           href = link.get("href")
                           if href:
                               #links.append(link)
                               if 'personalities' in href:
                                   if is_valid_url(personality_link, url) and personality_link not in visited and '#' not in personality_link:
                                       to_visit.append(personality_link)
                                   else:
                                       continue
                               if 'factchecks' in href:
                                   factcheck_link = urljoin(url,href)
                                   if is_valid_url(factcheck_link, url) and factcheck_link not in visited and '#' not in factcheck_link:
                                       to_visit.append(factcheck_link)
                                   else:
                                       continue
               time.sleep(1)  # Avoid overloading the server
           except requests.RequestException as e:
               print (f"Error access {url}: {e}")


def get_all_links(current_url):
   try:
       response = requests.get(current_url)
       if response.status_code == 200:
           soup = BeautifulSoup(response.text, 'html.parser')
           for link in soup.find_all('a', href=True):
               href = link['href']
               full_url = urljoin(current_url, href)
               # Process only links within the same domain
               if is_valid_url(full_url, current_url) and '#' not in full_url:
                   visited.add(full_url)
                   #print("Adding ", full_url, " to csv")
                   #check_if_fact_is_true_false(full_url, soup)
           time.sleep(1)  # Avoid overloading the server
   except requests.RequestException as e:
       print(f"Error accessing {current_url}: {e}")


def add_to_csv(url, fact, title, personality, date, social_media):
   fields=[personality, social_media, date, fact, title, url]
   with open(csv_filename, 'a') as f:
       writer = csv.writer(f)
       writer.writerow(fields)


for site in sites:
   if os.path.exists(csv_filename):
       os.remove(csv_filename)
   add_to_csv('url', 'fact', 'title', 'personality', 'date', 'social_media')
   get_article_details(site)