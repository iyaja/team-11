import requests
from bs4 import BeautifulSoup
import time
import json

def get_html(url, post_number):
    # Fetch the HTML content
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the <article> tag with specific class name
    article = soup.find('article', class_=post_number)

    return article

def get_case_description(article):
    desc = article.find('div', class_='case-content').text
    return desc

def get_plaintiff_defedant(article):
    case_title = article.find('h1', class_="entry-title").text
    plaintiff = case_title.split('v.')[0].strip(' ')
    defendant = case_title.split('v.')[1].strip(' ')
    return plaintiff, defendant

def get_docket_number(article):
    docket_num = article.find('div', class_='case-meta').find('span', class_='data').text
    return docket_num

def get_table(article):
    table = article.find('div', class_='entry-documents')
    # Initialize a list to store the table data
    table_data = []

    # Extract table headers
    headers = []
    for th in table.find('thead').find_all('th'):
        headers.append(th.text.strip())
    table_data.append(headers)

    # Extract table rows
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        row_data = [cell.text.strip() for cell in cells]
        table_data.append(row_data)

    return table_data

def extract_complaint_order_info(table_data):
    # Print the extracted table data
    complaint_info = ""
    order_info = ""
    for row in table_data:
        if row[1] == 'Complaint':
            if row[4] == '':
                complaint_info = row[3] # Action taken

        if row[1] == 'Order':
            if row[4] == '':
                order_info = row[3] # Action taken


    return (complaint_info, order_info)

def get_lawsuit_features(url, post_number):
    features = {}

    article = get_html(url, post_number)
    features['description'] = get_case_description(article)
    # features['docket_number'] = get_docket_number(article)
    plaintiff, defendant = get_plaintiff_defedant(article)
    features['plaintiff'] = plaintiff
    features['defendant'] = defendant

    _table_data = get_table(article)
    complaint_info, order_info = extract_complaint_order_info(_table_data)
    features['complaint_info'] = complaint_info
    features['order_info'] = order_info

    return features


NUMBER_OF_PAGES = 21
URL = "https://climatecasechart.com/principle-law/national-environmental-policy-act-nepa/page/{}"
def get_page(page_number):
    url = URL.format(page_number)
     # Fetch the HTML content
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the <article> tag with specific class name
    page = soup.find('main', class_='content')

    return page

def get_all_lawsuits_on_page(page):
    lawsuits = []
    article = ""
    lawsuit_count = 0
    article = page.find('article')
    while article:
        lawsuit_count += 1
        print("Searching lawsuit {}/20".format(lawsuit_count))

        # Naively assume always the first class tag
        post_number = article.get('class')[0]

        url = article.find('a', class_='entry-title-link').get('href')

        lawsuits.append((url, post_number))
        article = article.find_next('article')

    return lawsuits

def get_all_lawsuits():
    lawsuits = []
    for page_num in range(NUMBER_OF_PAGES):
        print("Getting lawsuits from page {}/{}".format(page_num, NUMBER_OF_PAGES))
        page = get_page(page_num)
        lawsuits_on_page = get_all_lawsuits_on_page(page)
        lawsuits.append(lawsuits_on_page)

    return lawsuits

def write_all_lawsuits(lawsuits):
    with open('nepa_lawsuits.csv', 'a') as fp:
        for lawsuit in lawsuits:
            for spec in lawsuit:
                fp.write("{},{}\n".format(spec[0], spec[1]))

# all_nepa_pages = get_all_lawsuits()
# write_all_lawsuits(all_nepa_pages)

def generate_json(data):
    lawsuit_features = {}
    page_count = 0
    laws_count = 0
    for lawsuit in data:
        page_count += 1
        print("On lawsuits {}".format(laws_count))
        print("Specs: {}".format(lawsuit))
        url = lawsuit[0]
        post_number = lawsuit[1]
        lawsuit_features[url] = get_lawsuit_features(url, post_number)
        time.sleep(0.5)
        laws_count += 1

    return lawsuit_features

TOTAL_LAWSUITS = 420
data = []
with open('nepa_lawsuits.csv', 'r') as file:
    count = 376
    for specs in file:
        url, post_number = specs.strip('\n').split(',')
        data.append((url, post_number))
        count -= 1
        if count == 0:
            break

dump = generate_json(data)

with open('litigation.json', 'w') as json_file:
    json.dump(dump, json_file, indent=4)

# generate_json(all_nepa_pages)