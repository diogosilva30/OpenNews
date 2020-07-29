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
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
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

    path_to_extension = r'C:\Users\diogo\Documents\API-NEWS_EXTRACTOR\4.17.0_0'

    chrome_options = Options()
    # chrome_options.add_extension('adblocker.crx')
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get(
        "CHROME_DRIVER_PATH"), chrome_options=chrome_options)
    print("Opening chrome and installing adblocker!")
    # driver = webdriver.Chrome(
    #     r"C:\Users\diogo\Downloads\chromedriver.exe", chrome_options=chrome_options)
    print("Opening publico's website...")
    driver.get("https://www.publico.pt")
    driver.switch_to.window(window_name=driver.window_handles[0])
    # driver.close()
    driver.implicitly_wait(5)
    print("Accepting cookies...")
    driver.find_element_by_xpath('//*[@id="qcCmpButtons"]/button[2]').click()
    print("Starting the login process...")
    driver.find_element_by_xpath(
        '//*[@id="masthead-container"]/div[2]/ul/li[2]/button').click()
    print("Entering email...")
    driver.find_element_by_xpath(
        '//*[@id="login-email-input"]').send_keys("al62176@utad.eu")
    driver.find_element_by_xpath(
        '//*[@id="login-form-email"]/div/div[4]/input').click()
    print("Entering password...")
    driver.find_element_by_xpath(
        '//*[@id="login-password-input"]').send_keys("tnt5&@X21qX*")
    driver.find_element_by_xpath(
        '//*[@id="login-form-password"]/div/div[4]/input').click()
    print("Login completed!")
    driver.implicitly_wait(10)
    driver.refresh()
    print("Starting to pull the news corpus...")
    news_corpus = []
    for url in urls:
        driver.implicitly_wait(3)
        driver.get(url)
        news_html = driver.page_source
        tree = html.fromstring(news_html)
        news_text = ' '.join(tree.xpath(
            "//div[@class='story__body']//p//text() | //div[@class='story__body']//h2//text()"))
        # Remove in-text ads
        news_text.replace(
            "Subscreva gratuitamente as newsletters e receba o melhor da actualidade e os trabalhos mais profundos do Público.", "")
        news_corpus.append(news_text)

    print("Sucessuly pulled corpus from " + str(len(urls)) + " news!")
    print("Closing Chrome!")
    driver.quit()
    return news_corpus
