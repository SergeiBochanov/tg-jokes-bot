import requests
import random
import aiohttp
from bs4 import BeautifulSoup, Tag
from aiogram.types import BufferedInputFile

def parser(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    anekdots = soup.find_all("div", class_="text")
    return [i.text for i in anekdots]

def image_parser(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    image = soup.find("a", href=url[:url.rfind("?")])
    if image is not None:
        style = image.get("style")
        if style is not None:
            src = style[style.find("http"):style.rfind("'")]
            return src
        else:
            return None

def video_parser(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    video = soup.find("video")
    if video is not None:
        src = video.get("src")
        return src

def good_morning_parser(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    selected_item: Tag = random.choice(soup.find_all("div", class_="card-image"))
    direct_page = requests.get(selected_item.findChild('a').get('href'))
    soup = BeautifulSoup(direct_page.text, "html.parser")
    item = soup.find("img", class_="cardContent")
    if item is not None:
        src = item.get("src")
        alt = item.get("alt").lower()
        file_extension = ""
        if "анимированная открытка" in alt:
            file_extension = "gif"
        else:
            file_extension = "img"
        return [src, file_extension]
    else:
        preview = soup.find(class_="cardContent").get("poster")
        item = soup.find("source", itemprop="contentUrl")
        if item is not None:
            src = item.get("src")
            return [src, "vid", preview]
        else:
            good_morning_parser(f"https://3d-galleru.ru/archive/cat/dobroe-utro-60/page-{random.randint(1, 1147)}/")

def nazhor_parser(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.find_all('a', class_='showcase__link js-detail-data-link')
    src = random.choice(links).findChild('img').get('data-src')
    return src

def get_tg_last_post_id(url, posts_type):
    if posts_type == 'video':
        parse_class = 'tgme_widget_message_video_player'
    elif posts_type == 'image':
        parse_class = 'tgme_widget_message_photo_wrap'
    else:
        return 1
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    block = soup.find_all('a', class_=parse_class)
    last_post_id = int(block[-1]['href'].split('/')[-1])
    return last_post_id

def generate_filename():
    alph = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789'
    text = ''.join([random.choice(alph) for _ in range(10)])
    return text

async def get_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            bin_image = await response.read()

        result_image = BufferedInputFile(file=bin_image, filename=f'{generate_filename()}.png')
        return result_image

async def get_video(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            bin_video = await response.read()

        result_video = BufferedInputFile(file=bin_video, filename=f'{generate_filename()}.mp4')
        return result_video