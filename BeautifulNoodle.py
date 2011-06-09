

import re
from BeautifulSoup import BeautifulSoup, NavigableString, Comment
import logging


class List(list):
    """
    List that proxies calls to unknown properties to his items

    If list empty, returns self.
    If called item's property, returns List of item's properties.
    If called item's method, returns loop function, that calls desired item's method on execution.
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
    List of CSS selector objects
    """

    def __init__(self, l=[]):
        list.__init__(self, [])
        for chunk in list(l):
            self.append(Selector(chunk))



class Selector(object):
    """
    CSS selector object
    """

    def __init__(self, selector):
        selector = selector.strip()
        match = re.match(r'^\w+', selector)
        self.tag = match.group(0) if match else ''
        match = re.search(r'\.[a-zA-Z0-9_ -]+', selector)
        self.cls = match.group(0).strip('.') if match else ''
        match = re.search(r'#[a-zA-Z0-9_ -]+', selector)
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




class Chef(object):
    """Chef"""

    log = logging

    def __init__(self, wanted_tags_selector=[], valid_tags = [], forbidden_tags = []):
        self.wanted_tags_selector = SelectorList(wanted_tags_selector)
        self.valid_tags = valid_tags
        self.forbidden_tags = forbidden_tags


    def find_wanted_content(self, soup):
        """
        Finds wanted elements.
        """
        assert isinstance(soup, BeautifulSoup)
        new_soup = BeautifulSoup()
        for selector in self.wanted_tags_selector:
            tag = soup.find(**selector.soup)
            self.log.info('Looking for element %s...' % selector.out())
            if tag:
                self.log.info('found')
                new_soup.insert(0, tag)
            else:
                self.log.info('NOT FOUND')
        return new_soup


    def remove_comments(self, soup):
        """
        Removes comments.
        """
        assert isinstance(soup, BeautifulSoup)
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        return soup


    def remove_tags(self, soup):
        """
        Removes forbidden elements.
        """
        assert isinstance(soup, BeautifulSoup)
        tags = soup.findAll(lambda tag: tag.name in self.forbidden_tags)
        [tag.extract() for tag in tags]
        return soup


    def strip_tags(self, soup):
        """
        Strip unwanted tags.
        """
        if not isinstance(soup, BeautifulSoup):
            soup = BeautifulSoup(soup)
        for tag in soup.findAll(True):
            if tag.name in self.valid_tags:
                # Check of valid element attributes
                for attr in dict(tag.attrs).keys():
                    if attr not in self.valid_tags[tag.name]:
                        del tag[attr]
            else:
                # Striping of invalid elements
                s = ""
                for c in tag.contents:
                    if not isinstance(c, NavigableString):
                        c = self.strip_tags(unicode(c))
                    s += unicode(c)
                tag.replaceWith(s)
        return soup

