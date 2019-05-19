#library setup
from flask import Flask,render_template,url_for,request,make_response
from bs4 import BeautifulSoup
from flask_bootstrap import Bootstrap
import requests
import re
import nltk
nltk.download('stopwords')
from selenium.webdriver.chrome.options import Options
from nltk.tokenize.toktok import ToktokTokenizer
import unicodedata
from selenium import webdriver
from time import sleep
import pandas as pd
from selenium.webdriver.common.keys import Keys

tokenizer = ToktokTokenizer()
stopword_list = nltk.corpus.stopwords.words('english')


app = Flask(__name__)
Bootstrap(app)
@app.route('/')
def index():
    return  render_template('index.html')

@app.route('/scrap',methods=['POST'])
def scrap():
    if request.method == 'POST':
       seed_url = request.form['news-category']
       news_category = seed_url.split('/')[-1]
       seed_urls = [str(seed_url)]
       df_to_display = build_dataset(seed_urls)
       resp = make_response(df_to_display.to_csv())
       resp.headers["Content-Disposition"] = "attachment; filename={}.csv".format(news_category)
       resp.headers["Content-Type"] = "text/csv"
       return resp


######################################################################################################
# main scraping functions

def build_dataset(seed_urls):
    print('inside build_dataset')
    div_soup, final_url,news_category_label = call_urls(seed_urls)
    post_data = extract_urls(div_soup, final_url,news_category_label)
    df = pd.DataFrame(post_data, columns=['post_title', 'post_text', 'post_date','category'])
    df.dropna()
    return df


def call_urls(seed_urls):
    for url in seed_urls:
        main_url = 'https://economictimes.indiatimes.com/'
        final_url = main_url + url
        news_category_label = url.split('/')[-1]
        if re.search(string=final_url, pattern='videoshow'):
            del (final_url)
        else:
            options = Options()
            options.headless = True
            browser = webdriver.Chrome('./assets/chromedriver.exe',chrome_options=options)
            browser.get(final_url)
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            match = False
            while (match == False):
                lastCount = lenOfPage
                sleep(1)
                lenOfPage = browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount == lenOfPage:
                    match = True
                #             loadMoreButton = browser.find_element_by_css_selector('div.autoload_continue')
            #             count=+ 1
            #             print("found it",type(loadMoreButton),count,"times")
            #             sleep(1.5)
            #             loadMoreButton.click()
            #             sleep(5)
            #             html = browser.find_element_by_tag_name('html')
            #             if html:
            #                 html.send_keys(Keys.END)
            #                 match=True

            # Now that the page is fully scrolled, grab the source code.
            source_data = browser.page_source
            browser.close()
            soup = BeautifulSoup(source_data, 'html.parser')
            div_soup = soup.find_all('div', {'class': 'eachStory'})
    return div_soup, main_url,news_category_label


def extract_urls(div_soup, main_url,news_category_label):
    post_data = []
    for div in div_soup:
        try:
            div_data = []
            post_url = main_url + div.find('a', href=True)['href']
            post = requests.get(post_url)
            post_soup = BeautifulSoup(post.text, 'html.parser')
            post_title = post_soup.find('h1', {'class': 'clearfix title'}).string
            div_data.append(post_title)
            post_text = post_soup.find('div', {'class': 'Normal'}).get_text()
            post_text = strip_html_tags(post_text)
            # remove accented characters
            post_text = remove_accented_chars(post_text)
            post_text = post_text.lower()
            post_text = re.sub(r'[\r|\n|\r\n]+', ' ', post_text)
            special_char_pattern = re.compile(r'([{.(-)!}])')
            post_text = special_char_pattern.sub(" \\1 ", post_text)
            post_text = remove_special_characters(post_text)
            # remove extra whitespace
            post_text = re.sub(' +', ' ', post_text)
            # remove stopwords
            post_text = remove_stopwords(post_text)
            div_data.append(post_text)

            try:
                # problem parsing date of updated blog post
                post_date = post_soup.find('div', {'class': 'publish_on flt'}).get_text()
                prcocessed_post_date = post_date.replace("Updated: ", "")
                div_data.append(prcocessed_post_date)
                post_category = news_category_label
                print("category is>",news_category_label)
                div_data.append(post_category)
            except IndexError:
                pass

        except AttributeError:
            pass
        post_data.append(div_data)

    return post_data


#nlp functions
def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    return stripped_text

def remove_accented_chars(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text

def remove_special_characters(text):
    pattern = r'[^a-zA-z0-9\s]'
    text = re.sub(pattern, '', text)
    return text

# def lemmatize_text(text):
#     text = nlp(text)
#     text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
#     return text

# def simple_stemmer(text):
#     ps = nltk.porter.PorterStemmer()
#     text = ' '.join([ps.stem(word) for word in text.split()])
#     return text

def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text


if __name__ == "__main__":
    app.run()