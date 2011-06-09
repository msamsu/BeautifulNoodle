

import re
import urllib
from BeautifulSoup import BeautifulSoup, NavigableString


class List(list):
    """
    List, jez preposila volani vlastnosti, ktere sam nezna, na svoje polozky

    Pokud je volana vlastnost, je vracen List vlastnosti.
    Pokud je volana metoda polozek, je vracena loop funkce, ktera pri zavolani, vola metodu vsech na polozkach.
    """

    def __getattr__(self, name):
        if not self:
            return self
        if not hasattr(getattr(self[0], name), '__call__'):
            new_set = List()
            for item in self:
                new_set.append(getattr(item, name))
            return new_set
        else:
            def loop(*arg, **kwarg):
                new_set = List()
                for item in self:
                    new_set.append(getattr(item, name)(*arg, **kwarg))
                return new_set
            return loop



class SelectorList(List):
    """
    List objektu css selektoru
    """

    def __init__(self, l=[]):
        list.__init__(self, [])
        for chunk in list(l):
            self.append(Selector(chunk))



class Selector(object):
    """
    Objekt css selektoru
    """

    def __init__(self, selector):
        selector = selector.strip()
        match = re.match(r'^\w+', selector)
        self.tag = match.group(0) if match else ''
        match = re.search(r'\.[\w ]+', selector)
        self.cls = match.group(0).strip('.') if match else ''
        match = re.search(r'#\w+', selector)
        self.id = match.group(0).strip('#') if match else ''

    @property
    def soup(self):
        d = {}
        if self.tag: d['name'] = self.tag
        if self.id or self.cls: d['attrs'] = {}
        if self.id: d['attrs']['id'] = self.id
        if self.cls: d['attrs']['class'] = self.cls
        return d

    def out(self):
        return {'tag': self.tag, 'id': self.id, 'class': self.cls}




class SoupCook(object):
    """Kuchar"""

    wanted_tags_selector = SelectorList()
    valid_tags = []
    forbidden_tags = []


    def find_wanted_content(self, soup):
        """
        Najde pozadovane tagy.
        """
        assert isinstance(soup, BeautifulSoup)
        new_soup = BeautifulSoup()
        for selector in self.wanted_tags_selector:
            tag = soup.find(**selector.soup)
            print 'Looking for element %s...' % selector.out(),
            if tag:
                print 'found'
                new_soup.insert(0, tag)
            else:
                print 'NOT FOUND'
        return new_soup


    def remove_tags(self, soup):
        """
        Odmaze tag i s jeho obsahem.
        """
        assert isinstance(soup, BeautifulSoup)
        tags = soup.findAll(lambda tag: tag.name in self.forbidden_tags)
        list(tag.extract() for tag in tags)
        return soup


    def strip_tags(self, soup):
        """
        Odmaze vsechny tagy, krome validnich, ale ponecha jejich obsah.
        """
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup)
        for tag in soup.findAll(True):
            if tag.name in self.valid_tags:
                # kontrola atributu vyhovujicim tagum
                for attr in dict(tag.attrs).keys():
                    if attr not in self.valid_tags[tag.name]:
                        del tag[attr]
            else:
                # odstraneni nevyhovujicich tagu
                s = ""
                for c in tag.contents:
                    if not isinstance(c, NavigableString):
                        c = self.strip_tags(unicode(c))
                    s += unicode(c)
                tag.replaceWith(s)
        return soup




data_url = 'http://www.tyinternety.cz/reklama/top-viraly-tydne-slepec-hovno-vidi1-3904'
wanted_tags_selector = [
    'div.article_opener detail',
    'div#main',
    '#main',
    '.article_opener',
    '#main.article_opener',
    '#main#article_opener'
]
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

cook = SoupCook()
cook.wanted_tags_selector = SelectorList(wanted_tags_selector)
cook.valid_tags = valid_tags
cook.forbidden_tags = forbidden_tags

print 'Fetching %s' % data_url
data_file = urllib.urlopen(data_url)
content = data_file.read()

soup = BeautifulSoup(content)

soup = cook.find_wanted_content(soup)
soup = cook.remove_tags(soup)
soup = cook.strip_tags(soup)

soup.prettify()



