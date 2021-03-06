from flaskr import dao_defsrc
import collections
import requests
import bs4
import re
import operator
import json
import psycopg2
import os
import logging
import spacy

logger = logging.getLogger(__name__)

nlp = spacy.load("fr_core_news_sm")

def get_articles_src_already_stored(word):
    src = dao_defsrc.get(word)
    if src is not None:
        return json.loads(src)


def has_class(tag, class_name):
    return isinstance(tag, bs4.element.Tag) and tag.has_attr("class") and class_name in tag["class"]


def to_raw_html(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    article = soup.find("div", id=re.compile("^art"))
    return "<br>".join(map(str, article)) if article else ""


def get_wordinfo(article):
    _word = article.find_all("div", class_="tlf_cvedette")
    if len(_word) != 1:
        raise ValueError(f"Expected to find exactly one word, found: {_word}")
    word = _word[0].find("span", class_="tlf_cmot")
    code = _word[0].find("span", class_="tlf_ccode")
    version = None
    if word:
        c = word.contents
        if c:
            word = c[0]
            if len(c) > 1:
                x = c[1]
                x = str(x).strip()
                match = re.compile("<sup>(.*)</sup>").fullmatch(x)
                if match:
                    version = int(match.group(1).strip()) # todo: can be more than int
            if word[-1] == ",":
                word = word[:-1]
        else:
            raise ValueError(f"No word content found for: {word}")
    else:
        word = None
    return word, version, code.text if code else None


Word = collections.namedtuple("Word", ["text", "link"])


def tok2word(token):
    return Word(
        text=token.text,
        link=token.pos_ == "NOUN"
    )


class Definition(collections.UserList):
    def __init__(self, tokens, word=None, synt=None):
        super().__init__(map(tok2word, tokens))
        self.word = word
        self.synt = synt

    @property
    def type(self):
        return "synt" if self.synt else "def"

    def to_dict(self):
        return {
            "type": self.type,
            "body": list(map(Word._asdict, self)),
            "synt": self.synt,
        }


class Group(collections.UserList):
    @classmethod
    def create(cls, parent=None):
        new = cls()
        new.parent = parent
        return new


def process_article_src(html) -> dict:
    soup = bs4.BeautifulSoup(html, "html.parser")
    article = soup.find("div", id=re.compile("^art"))

    if not article:
        return {}

    word, version, code = get_wordinfo(article)

    def getcls(t):
        return " ".join(t.get("class", ()))

    def_obj = {"word": word, "version": version, "code": code, "defs": []}
    for t_root in filter(lambda t: isinstance(t, bs4.Tag), article.children):
        group = []
        if getcls(t_root) == "tlf_parah":
            waiting = None
            for t in t_root.find_all("span"):
                cls = getcls(t)
                text = t.text
                if cls == "tlf_cdefinition":
                    group.append(Definition(nlp(text), synt=waiting).to_dict())
                    waiting = None
                elif cls == "tlf_csyntagme":
                    waiting = text
                else:
                    waiting = None
        elif getcls(t_root) == "tlf_cdefinition":
            group.append(Definition(nlp(t_root.text), synt=None).to_dict())

        def_obj["defs"].append(group)

    return def_obj


def get_definition(word, process_fn, raw):
    """For the given word, return code to embed: if raw, a string of html, else,
    a dict to be parsed by the client.
    :returns: (str|dict, str): definition, data source (local/remote)
    """
    word = word.lower()
    base_url = "https://www.cnrtl.fr/definition"
    url = f"https://www.cnrtl.fr/definition/{word}"
    articles_src = []
    source = "remote"

    _stored = get_articles_src_already_stored(word)
    if _stored is not None:
        articles_src = _stored
        source = "local"
    else:
        resp = requests.get(url)
        html_content = resp.content
        soup = bs4.BeautifulSoup(html_content, "html.parser")
        links = [link for link in soup("a") if link.has_attr("onclick")]
        re_num = re.compile(f"/definition/({word}//[0-9])")
        for suffix in map(lambda x: x.group(1),
                      filter(lambda x: x is not None,
                      map(re_num.search,
                      map(operator.itemgetter("onclick"), links)))):
            url = f"{base_url}/{suffix}"
            resp = requests.get(url)
            articles_src.append(resp.content.decode("utf8"))
        dao_defsrc.write(word, json.dumps(articles_src))

    if raw:
        return "<hr>".join(map(process_fn, articles_src)), source
    else:
        return list(map(process_fn, articles_src)), source


def check_input(word):
    return word.strip() != ""
