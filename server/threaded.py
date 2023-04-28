import requests
from bs4 import BeautifulSoup
import time
import cloudscraper
import threading


# global links1
# global links2 
# global dictionary
# global homescrap_dictionary 


links1 = []
links2 = []
dictionary = {}
homescrap_dictionary = {}

def get_all_links(url):

    # global lin
    links = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        if soup.find('h3').text == 'Your search yielded no results.':
            return []
        else:
            link_div =  soup.find_all('div', class_="netlsearch-results")
            for a in link_div:
                links.append(a.find('a')['href'])
            # print(links)
            return links
            
    except:
        print("except netl error")
        return []
        


def get_related_links(links):

    related_links = links[19:49]
    return related_links


def scrap_p_tag_from_urls(urls):
    netl_dictionary = {}

    for url in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        h2 = soup.find('h2', class_='factsheetTitle')
        if h2 is None:
            continue
        # print(h2.text)
        heading = h2.text.replace('\n', '')
        # print(heading)
        content = ''
        for p in soup.find_all('p'):
            content += p.text
        dictionary[heading] = [content, url]
        netl_dictionary[heading] = [content, url]
    
        # print("Scrapped in netl : ", heading)
    # print("netl dictionary length : ", len(netl_dictionary))
    # print("netl dictionary : ", netl_dictionary)
    return 

def get_all_links1(url,page,n):
    # print("entered eep")

    try:
        keyword = n
        scrap_page = page
        next_url = 'https://electrical-engineering-portal.com/page/'+str(scrap_page)+'?s='+keyword+'&post_type_page=&post_type_post='
        for page in range(1, 3):
            scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})

            html = scraper.get(next_url).content

            soup = BeautifulSoup(html, 'html.parser')
                    
            if ((len(soup.find_all('body',class_='error404')) == 0) and (len(soup.find_all('body',class_='search-no-results')) ==0)):
                for a in soup.find_all('a', href=True,class_='feeds-articles__image'):
                    links1.append(a['href'])
                # print("Scrapped : ", len(links1))
                # print("Page : ", page)
                # print(links1)
                scrap_page+=1
                next_url = 'https://electrical-engineering-portal.com/page/'+str(scrap_page)+'?s='+keyword+'&post_type_page=&post_type_post='

                # get_all_links1(next_url,page,n)
            
            if (len(soup.find_all('body',class_='search-no-results')) !=0):
                print("No results found")
                return []
            print("eep running recursievely")
        
    except:
        print("except error in eep")
        
        return []
        
    return links1

def scrap_p_tag_from_urls1(urls):

    for url in urls:
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
        html1 = scraper.get(url).content
        soup1 = BeautifulSoup(html1, 'html.parser')
        h1 = soup1.find('h1', class_='pf-title')
        if h1 is None:
            continue
        heading = h1.text
        content = ''
        content_div = soup1.find('div', class_='entry')
        # print(content_div)
        for p in content_div.find_all('p'):
            content += p.text
        dictionary[heading] = [content, url]
        # print("Scrapped in eep : ", heading)

    return 

def homepage_scrap(page_url):

    # print("entered scrap")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    for i in range(3):
        url = page_url + f'?sort_bef_combine=created_DESC&sort_by=created&sort_order=DESC&page={i}'
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find_all('a', class_ = "field-group-link card-link")
        # link = link[0:5]
        for i in link:
            urls = 'https://climate.mit.edu'+i['href']
            responses = requests.get(urls,headers=headers)
            soup1 = BeautifulSoup(responses.text, 'html.parser')
            h1 = soup1.find('h1')
            heading = h1.text
            div = soup1.find('div',class_='clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item')
            p_tags = div.find_all('p')
            content = ''
            for p in p_tags:
                content+=p.text
            homescrap_dictionary[heading] = [content, urls]
    return 


def netl_website(input,no_of_articles):
    if no_of_articles > 10:
        no_of_articles = 10
    n = input
    n = n.replace(" ", '+')
    url_netl = 'https://netl.doe.gov/search/node?keys='+n
    # print(url_netl)
    # print(ALL_LINKS)

    ALL_LINKS = get_all_links(url_netl)
    ALL_LINKS = ALL_LINKS[:no_of_articles]

    # RELATED_LINKS = get_related_links(ALL_LINKS)
    # start = time.time()
    scrap_p_tag_from_urls(ALL_LINKS)
    # end = time.time()
    # print("The time of execution of netl program is :", end-start, "s")
    # print("Available Articles")
   
    # print("Total articles : ", len(ARTICLES))
    print("completed netl website")
    
def eepwebsite(input,no_of_articles):
    if no_of_articles > 15:
        no_of_articles = 15
    n = input
    n = n.replace(" ", '+')
    page = 1
    url = 'https://electrical-engineering-portal.com/page/'+str(page)+'?s='+n+'&post_type_page=&post_type_post='
    ALL_LINKS = get_all_links1(url,page,n)
    TO_BE_SCRAPED = ALL_LINKS[:no_of_articles]
    # no = 0
    # for link in ALL_LINKS:
    #     print(no,":",link)
    #     no +=1
    # start = time.time()
    scrap_p_tag_from_urls1(TO_BE_SCRAPED)
    # end = time.time()
    # print("The time of execution of eep program is :", end-start, "s")
    # print("Available Articles")
    # for i in ARTICLES.keys():
    #     print(i)
    # print("Total articles : ", len(ARTICLES))
    print("completed eep website")
    
    
def eep_homepage_scrap(url):

    links =[]
    scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
    html = scraper.get(url).content
    
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup)
    for articletag in soup.find_all('article',class_='feeds-articles__item'):
        link = articletag.find('a')['href']
        links.append(link)
    # print(len(links))
    
    return links

def scrap_eep_links(links):

    for url in links:
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
        html1 = scraper.get(url).content
        soup1 = BeautifulSoup(html1, 'html.parser')
        h1 = soup1.find('h1', class_='pf-title')
        if h1 is None:
            continue
        heading = h1.text
        content = ''
        content_div = soup1.find('div', class_='entry')
        # print(content_div)
        for p in content_div.find_all(['p','h3']):
            content += p.text
        homescrap_dictionary[heading] = [content, url]
        print("Scrapped in eep homepage : ", heading)
    # print(dictionary)
    return 
        
def get_all_links2(page,n):

    try:
        keyword = n
        # print("keyword",keyword)
        scrap_page = page
        next_url = 'https://www.carbonbrief.org/search/?_sf_s='+keyword+'&sf_paged='+str(scrap_page)
        for page in range(1, 3):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
            response = requests.get(next_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
          
            if (len(soup.find_all('tr',class_='no-result-wrap')) != 0):
                print("no results found")
                return []
            
            else:
                
                links_h3 = []
                link_div =  soup.find_all('div', class_="esubDtls")
                print("link_div in energy central",link_div)
               
                for h3 in link_div:
                    links_h3.append(h3.find('h3'))
                    
                    
                for a in links_h3:
                    links2.append(a.find('a')['href'])
                
                scrap_page += 1
                next_url = 'https://www.carbonbrief.org/search/?_sf_s='+keyword+'&sf_paged='+str(scrap_page)
                
                
        
    except:
        print("except error in energy  central")
        
        return []
    
    return links2


def scrap_p_tag_from_urls2(urls):

    for url in urls:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = soup.find('h1')
        if h1 is None:
            continue
        heading = h1.text
        content = ''
        content_div = soup.find('div', class_='innerArt')
        for p in content_div.find_all('p'):
            content += p.text
        dictionary[heading] = [content, url]
        # print("Scrapped in energy central : ", heading)
        
    # print("dictionary",dictionary)   
    return 
    
    

    
def energycentral_website(input,no_of_article):
    if no_of_article >15:
        no_of_article = 15

    n = input
    page = 1
    
    n = n.replace(" ", '+')
    
    
    ALL_LINKS = get_all_links2(page,n)
    ALL_LINKS = ALL_LINKS[:no_of_article]
    
    scrap_p_tag_from_urls2(ALL_LINKS)
    print("completed energy central website")
    
    
    


        
def mitwebsite(no_of_article):
    print("mit website",no_of_article)

    # start = time.time()
    url = f'https://climate.mit.edu/explainers'
    homepage_scrap(url)
    # print("mit website", len(d.keys()))
    # end = time.time()
    # print("The time of execution of mit program is :",end-start,"s")
    print("completed mit website")
 
def homepage_eepwebsite(no_of_article):

    url = 'https://electrical-engineering-portal.com/#'
    ALL_LINKS = eep_homepage_scrap(url)[:no_of_article]
    scrap_eep_links(ALL_LINKS)
    print("completed eep homepage website")

def scrape_threaded(input, no_of_article):
    # links1 = []
    # links2 = []
    # dictionary = {}
    # homescrap_dictionary = {}
    # no. of article query is not needed as i changed the code to scrap 30 articles from each website
    if input == '':
        t3 = threading.Thread(target=mitwebsite,args=(no_of_article,))
        t4 = threading.Thread(target=homepage_eepwebsite, args=(no_of_article,))
        t3.start()
        t4.start()
        t3.join()
        t4.join()


        return homescrap_dictionary
    
    else:
        t1 = threading.Thread(target=eepwebsite, args=(input,no_of_article,))
        t2 = threading.Thread(target=netl_website, args=(input,no_of_article,))
        t5 = threading.Thread(target=energycentral_website, args=(input,no_of_article,))
        

        t1.start()
        t2.start()
        t5.start()

        t1.join()
        t2.join()
        t5.join()  

        # print(len(dictionary.keys()))
        
        return dictionary




# a= scrape_threaded("energy")
# print(homescrap_dictionary)
# print("total length:",len(a.keys()))
