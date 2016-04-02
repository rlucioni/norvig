from concurrent.futures import ThreadPoolExecutor
import logging
import os
import time

from bs4 import BeautifulSoup
import requests
from slugify import slugify


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

readme = 'http://norvig.com/ipython/README.html'
extension = '.ipynb'


def main():
    logging.debug('Retrieving notebooks from [%s].', readme)

    soup = soupify(readme)

    search(soup)


def soupify(url):
    response = requests.get(readme)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    return soup


def search(soup):
    with ThreadPoolExecutor() as executor:
        for link in soup.find_all('a'):
            href = link.get('href')
            if not href.startswith('http://'):
                executor.submit(sync, href)


def sync(notebook):
    logging.debug('Syncing notebook [%s].', notebook)

    slug = slugify(notebook.split(extension)[0])
    path = 'notebooks/{slug}{extension}'.format(slug=slug, extension=extension)

    if os.path.isfile(path):
        logging.info('Notebook [%s] exists at [%s].', notebook, path)
    else:
        logging.info('Saving new notebook [%s].', notebook)
        save(notebook, path)



def save(notebook, path):
    start = now()

    response = requests.get('http://norvig.com/ipython/' + notebook)
    raw = response.text

    with open(path, 'w') as f:
        f.write(raw)

    end = now()
    elapsed = end - start
    logging.debug('Saved notebook [%s] to [%s] in [%.2f] seconds.', notebook, path, elapsed)


def now():
    return time.time()


if __name__ == '__main__':
    main()
