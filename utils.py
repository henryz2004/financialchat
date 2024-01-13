from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
#chrome_prefs = {}
#chrome_options.experimental_options["prefs"] = chrome_prefs
#chrome_prefs["profile.default_content_settings"] = {"images": 2}
driver = webdriver.Chrome(options=chrome_options)

prompt = """
You are a financial advisor who helps users with analyzing the current state of the market and economy. It is critical that your answers be factual and nuanced.
"""

N_PARA_BEGIN = 7
N_PARA_END = 7
def grab_article_info(ft_url):

    try:
    
        q_string = urlencode({"url": ft_url})
        archive_url_req = "https://archive.ph/submit/?"+q_string
        driver.get(archive_url_req)
        
        title = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#o-topper > h1 > span"))
        ).text
    
        body = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "article-body"))
        )
    
        all_text = body.text #all_text = get_text_recursive(body)
        paragraphs = all_text.split("\n")
        trunc = []
        if len(paragraphs) <= N_PARA_BEGIN + N_PARA_END:
            trunc = paragraphs
        else:
            trunc = paragraphs[:N_PARA_BEGIN] + paragraphs[-N_PARA_END:]
        
        return {"title": title, "short":trunc}

    except TimeoutException as e:
        return {"title": "", "short":""}
    
def get_ft_search_url(query):
    query_string = urlencode({"sort":"relevance", "q":query})
    return f"https://www.ft.com/search?{query_string}"

def get_ft_urls(search_url):
    driver.get(search_url)
    search_results = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#site-content > div.search-results.o-teaser-collection > ul"))
    )
    
    header_links = search_results.find_elements(By.CLASS_NAME, "js-teaser-heading-link")
    
    ft_urls = []
    for res in header_links:
        ft_url = res.get_attribute("href")
        ft_urls.append(ft_url)
    return ft_urls

def get_article_infos(ft_urls, k=5):
    for i, ft_url in enumerate(ft_urls[:k]):
        print(f"fetching article {i+1}/{k}")
        info = grab_article_info(ft_url)
        yield info
    

def generate_article_rag(art_infos):
    ret = ""
    for art in art_infos:
        ret += "Title: "+art['title']+"\n"
        ret += "Excerpt:"+'\n'.join(art['short'])+"\n\n"
    return ret

def generate_prompt(question, rag):
    ret = question
    ret += "\n\n###\n\n"
    ret += "Here are some recent article snippets from the Financial Times found by searching up the question that can help inform your response:\n\n"
    ret += rag

    return ret

def generate_query_prompt(prompt, questions):
    formatted_questions = "\n".join(questions)
    return f"""
What is a good query to find useful articles on the Financial Times about the question:

"{prompt}"

Previous questions the user asked are:

{formatted_questions}

###

Please answer with just the search query that would be entered into the FT searchbar. For example, a good response for "How is the us economy doing?" is "US economy" with no quotation marks"""