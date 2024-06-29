"""
Fetch relevant CFR (Code of Federal Regulations) for feature extraction
"""

import requests
from bs4 import BeautifulSoup

## Title 40 Chapter V Subchapter A Part 1500-1508
PARTS = {
    "Purpose, Policy, and Mandate" : 1500,
    "NEPA and Agency Planning" : 1501,
    "Environmental Impact Statement" : 1502,
    "Commenting" : 1503,
    "Predecision Referrals to the Council of Proposed Federal Actions Determined to Be Environmentally Unsatisfactory" : 1504,
    "NEPA and Agency Decision-Making" : 1505,
    "Other Requirements of NEPA" : 1506,
    "Agency Compliance" : 1507,
    "Terminology and Index" : 1508
}

# TITLE_40_PARTS = [1500]
TITLE_40_PARTS = [1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508]
TITLE_1_PART = 601

CHANGES_40 = ['2022-05-20', '2022-04-20', '2021-06-29', '2020-09-14', '2017-01-01']
CHANGES_1 = ['2017-10-30']

API = "https://www.ecfr.gov"
TITLE_40 = "/api/versioner/v1/full/{}/title-40.xml?subtitle=1&chapter=V&part={}"
TITLE_1 = "/api/versioner/v1/full/{}/title-1.xml?chapter=VI&part=601"
HEADERS= {'Accept': 'application/xml'}

# Send a get request to ecfr API for a provided endpoint
def get_ecfr(endpoint):
    url = API + endpoint
    print(url)
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        print('Request successful!')
        return response.text
    else:
        print('Request failed with status code:', response.status_code)


"""
Get relevant regulation data for Title 40 Chapter V Subchapter A Part 1500-1508
"""
def get_nepa40(date, part):
    return get_ecfr(TITLE_40.format(date, part))

def get_nepa40_parts(date):
    data = []
    for part in TITLE_40_PARTS:
        data.append(get_nepa40(date, part))

    return data

"""
Get relevant regulation data for Title 1 Chapter VI Part 601
"""
def get_nepa1(date):
    return get_ecfr(TITLE_1.format(date, TITLE_1_PART))

def get_regulatory_snapshot_title_40(date):
    nepa_parts = []
    for part in get_nepa40_parts(date):
        nepa_parts.append(process_xml(part))

    return nepa_parts

def get_regulatory_snapshot_title_1(date):
    return process_xml(get_nepa1(date))

def get_regulatory_snapshot(date):
    t1 = get_regulatory_snapshot_title_1(date)
    t40 = get_regulatory_snapshot_title_40(date)

    return t40.append(t1)

def process_xml(xml):
    processed_xml = []

    # Parse the XML data
    soup = BeautifulSoup(xml, features='lxml-xml')

    sections = soup.find_all('DIV8')
    for section in sections:
        # section_number = section.get('N')
        # section_head = section.find('HEAD').string
        section_text = ' '.join([p.get_text(strip=True) for p in section.find_all('P')])

        processed_xml.append(section_text)

        # print(f"Section {section_number} : {section_head}")
        # print(section_text)
        # print('=' * 80)
        # print('\n')

    return processed_xml

def write_snapshot(text, title, date):
    fn = title+date+".txt"
    with open(fn, 'w') as file:
        file.write(text)

def write_title_1_timeline():
    for date in CHANGES_1:
        snapshot = get_regulatory_snapshot_title_1(date)

        write_snapshot(snapshot[0], 'title_1_', date)

def write_title_40_timeline():
    for date in CHANGES_40:
        snapshots = get_regulatory_snapshot_title_40(date)

        print("Collecting text")
        text = ""
        for snapshot in snapshots:
            text += snapshot[0]
        print("Writing snapshot")
        write_snapshot(text, 'title_40_', date)

write_title_40_timeline()