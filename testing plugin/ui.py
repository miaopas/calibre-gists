
from PyQt5.Qt import QToolButton, QMenu
if False:
    get_icons = get_resources = None
from calibre.gui2.actions import InterfaceAction
from lxml import etree
from calibre.ebooks.chardet import xml_to_unicode
class InterfacePlugin(InterfaceAction):

    name = 'testing'

    # Declare the main action associated with this plugin
    # The keyboard shortcut can be None if you dont want to use a keyboard
    # shortcut. Remember that currently calibre has no central management for
    # keyboard shortcuts, so try to use an unusual/unused shortcut.
    action_spec = ('testing', None,
            'testing', None)

    def genesis(self):
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.test)
    def get_header(self):
        import random
        user_agent_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Safari/537.36 OPR/26.0.1656.60',
            'Opera/8.0 (Windows NT 5.1; U; en)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
            'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 '
            '(maverick) Firefox/3.6.10',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/39.0.2171.71 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
            '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
        ]
        UserAgent = random.choice(user_agent_list)
        header = {'User-Agent': UserAgent}
        return header
    def parse_html(self,raw):
        try:
            from html5_parser import parse
        except ImportError:
            # Old versions of calibre
            import html5lib
            return html5lib.parse(raw, treebuilder='lxml', namespaceHTMLElements=False)
        else:
            return parse(raw)

    def get_html_page(self,url, br):
        raw = br.open_novisit(url).read().strip()
        raw = xml_to_unicode(raw, strip_encoding_pats=True,
                         resolve_entities=True)[0]
        tree = self.parse_html(raw)
        for a in tree.xpath('//a[@href]'):
            if ('black-curtain-redirect.html' in a.get('href')) or ('/black-curtain/save-eligibility/black-curtain' in a.get('href')):
                url = a.get('href')
                if url:
                    if url.startswith('/'):
                        url = 'https://amazon.co.jp' + a.get('href')
                    print(f'Black curtain found, new url {url}')
                    return self.get_html_page(url, br)
        return raw

    def test(self):
        from urllib.request import Request, urlopen
        from bs4 import BeautifulSoup
        from lxml import etree
        from calibre import browser
        asin = ('B01NAI0BJQ', 'B00DW6IAWY','B081DG8RSC', 'B09XM8PS4V')

        url = f'https://www.amazon.co.jp/gp/product/{asin[2]}'
        raw = self.get_html_page(url, browser())
        
        soup = BeautifulSoup(raw, 'lxml')
        def check_filter(s):
            FILTER = ['Amazon', '検索結果']
            for f in FILTER:
                if f in s:
                    return False
            return True
        authors = []
        for t in soup.select('.author .a-link-normal'):
            if len(t) > 1:
                raise Exception('Error found when getting authors')
            author = t.contents[0]
            if check_filter(author) and author not in authors:
                authors.append(author)
        print(authors)
