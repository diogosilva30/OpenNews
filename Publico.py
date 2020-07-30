# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = jn_from_dict(json.loads(json_string))
import urllib
import requests
from lxml import html
import os
import json
from typing import Optional, Any, List, TypeVar, Type, cast, Callable
from datetime import datetime
import dateutil.parser

T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


class Publico:
    id: Optional[int]
    titulo: Optional[str]
    descricao: Optional[str]
    texto: None
    url: Optional[str]
    rubrica: Optional[str]
    tipo: Optional[str]
    is_opinion: Optional[bool]
    data: Optional[datetime]
    autores: Optional[List[str]]
    search_key: Optional[str]

    def __init__(self, titulo, descricao, texto, url, rubrica, tipo, data, autores, search_key) -> None:
        self.titulo = titulo
        self.descricao = descricao
        self.texto = texto
        self.url = url
        self.rubrica = rubrica
        self.tipo = tipo
        self.data = data
        self.autores = autores
        self.search_key = search_key

    """
    Method to get the news corpus. The jornal API resource does not include text.
    So here the corpus of a news is webscrapped from it's url
    """

    @classmethod
    def from_dict(cls, obj: Any, start_date, search_key):

        titulo = from_str(obj.get("titulo"))
        descricao = " " if obj.get(
            "descricao") is None else from_str(obj.get("descricao"))
        url = "https://www.publico.pt" + from_str(obj.get("fullUrl"))

        texto = ' '
        rubrica = from_str(obj.get("rubrica"))
        if "Entrevista" in rubrica or "Direito de Resposta" in rubrica:
            return None

        # Skip Opinion articles
        if from_bool(obj.get("isOpinion")) is True:
            return None

        tipo = from_str(obj.get("tipo"))
        if "NOTICIA" not in tipo:
            return None

        data = from_datetime(obj.get("data"))

        if start_date is not None:
            # Raise exception if data is older than start date, this will break the search
            if(data < from_datetime(start_date)):
                raise ValueError("Date is older than start date!")
        # Read the json array regarding authors
        autores = obj.get("autores")
        # Create new array
        authors = []
        for author in autores:
            # 'autores' is a list of dicts. Keep only the name for each dict
            author = {k: v for k, v in author.items() if k.startswith('nome')}
            # Add the author to authors array
            authors.append(author)

        return Publico(titulo=titulo, descricao=descricao, texto=texto, tipo=tipo, url=url, rubrica=rubrica, data=data, autores=authors, search_key=search_key)


def Publico_From_Dict(s: Any, start_date, search_key):
    return Publico.from_dict(s, start_date, search_key)


def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__,
                      sort_keys=True, indent=4)


def get_news_corpus(urls):

    news_corpus = []

    print("Now extracting news corpus!")
    payload = {"username": "al62176@utad.eu",
               "password": "tnt5&@X21qX*"}
    with requests.Session() as s:
        # set the user agent header, required for the jornal api to work
        s.headers.update(
            {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'})
        # send POST request to login
        res = s.post("https://www.publico.pt/api/user/login", data=payload)
        # Now we can extract the corpus from the news
        for url in urls:
            # GET request to read the html page
            res = s.get(url)
            # Load html page into a tree
            tree = html.fromstring(res.text)
            # Find the news text by XPATH
            news_text = ' '.join(tree.xpath(
                "//div[@class='story__body']//p//text() | //div[@class='story__body']//h2//text()"))
            # Remove in-text ads
            news_text.replace(
                "Subscreva gratuitamente as newsletters e receba o melhor da actualidade e os trabalhos mais profundos do Público.", "")
            news_corpus.append(news_text)

    print("Sucessuly pulled corpus from " + str(len(urls)) + " news!")

    return news_corpus
