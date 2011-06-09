

import urllib
from BeautifulSoup import BeautifulSoup
import logging
from BeautifulNoodle import Chef
import sys

strm_out = logging.StreamHandler(sys.stdout)
log = logging.getLogger('console')
log.setLevel(logging.INFO)
log.addHandler(strm_out)


valid_tags = {
    'div': [],
    'p': [],
    'a': ['href'],
    'img': ['src'],
    'b': [],
    'i': []
}
forbidden_tags = [
    'script'
]


def cook(data_url, wanted_tags_selector):
    chef = Chef(wanted_tags_selector, valid_tags, forbidden_tags)
    chef.log = log

    log.info('Fetching %s' % data_url)
    data_file = urllib.urlopen(data_url)
    content = data_file.read()

    soup = BeautifulSoup(content)

    soup = chef.find_wanted_content(soup)
    soup = chef.remove_tags(soup)
    soup = chef.remove_comments(soup)
    soup = chef.strip_tags(soup)

    return soup.prettify()



data_url = 'http://www.tyinternety.cz/reklama/top-viraly-tydne-slepec-hovno-vidi1-3904'
wanted_tags_selector = [
    'div.article_opener detail',
    'div#main',
]
noodle = cook(data_url, wanted_tags_selector)
open('out/tyinternety.html', 'w').write(noodle)



data_url = 'http://www.zive.cz/clanky/proc-nase-stranky-nejedou-na-adrese-wwwzivecr/sc-3-a-157435/default.aspx'
wanted_tags_selector = [
    'div#article-main-data',
]
noodle = cook(data_url, wanted_tags_selector)
open('out/zive.html', 'w').write(noodle)



data_url = 'http://ekonom.ihned.cz/c1-52054790-ekonom-cz-majitele-skupiny-eltodo-prodavaji-firmu-nabidku-podal-i-cez'
wanted_tags_selector = [
    'div.d-perex',
    'div.d-text',
]
noodle = cook(data_url, wanted_tags_selector)
open('out/ekonom.html', 'w').write(noodle)





