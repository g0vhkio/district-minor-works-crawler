import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from time import sleep
import scraperwiki
from datetime import datetime


def scrap_number_of_pages():
    url = 'https://www.dmw.gov.hk/tc_chi/results.php'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    last_page_div = soup.find_all('div', {'class': 'searchList_page'})[-1]
    return int(last_page_div.find('a').text)

def scrap_detail(project_id):
    qs = urlencode({'code': project_id})
    url = f'https://www.dmw.gov.hk/tc_chi/details.php?{qs}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    conts = soup.find_all('div', {'class': 'cont'})
    year = int(conts[1].text)
    details = conts[2].text.strip()
    contacts = conts[3].text
    return {'year': year, 'details': details, 'contact': contacts}

run_date = datetime.today().date()
n = scrap_number_of_pages()
print('Total number of pages: %d' % n)
for i in range(1, n + 1):
    url = f'https://www.dmw.gov.hk/tc_chi/results.php?district=&department=&type=&page={i}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    container = soup.find('div', {'class': 'styleDiv ToggleList styleFirstRow formDiv1'})
    for row in container.find_all('div', recursive=False)[1:]:
        columns = row.find_all('div')
        texts = [c.text for c in columns]
        href = columns[2].find('a')['href']
        project_id = href.replace('javascript:showDetail(\'', '').replace('\');', '')
        d = {
            'project_id': project_id,
            'category': texts[1],
            'location': texts[2],
            'department': texts[3],
            'run_date': run_date
        }
        d2 = scrap_detail(project_id)
        d.update(d2)
        scraperwiki.sqlite.save(unique_keys=['run_date', 'project_id'], data=d)
        sleep(0.2)
    print('Finished page %d.' % i)
    sleep(0.5)

