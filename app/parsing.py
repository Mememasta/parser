import asyncio
import aiohttp
import os
import time
import logging
import lxml.html

from lxml.cssselect import CSSSelector as cssselect
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

#limit = asyncio.Semaphore(5)  #Количество одновременных запросов


url_test = []
url_list = []
char_list = []

#Асинхронный метод для отправки http-запросов
async def request(client, url):
    #global limit
    #with await limit:
    async with client.get(url) as r:
        return await r.text()

def parsing_uri(request):
    # return lxml.html.fromstring(request)
    soup = BeautifulSoup(request, 'lxml')
    cars = soup.find_all("div", {"class": "snippet-horizontal"})
    for car in cars:
        uri = car.find("a", {"class": "snippet-link"}).get("href")
        url = f"https://www.avito.ru{uri}"
        url_list.append(url)
    data = url_list
    return data

def parsing_category(request):
    soup = BeautifulSoup(request, 'lxml')
    data = {}
    char_cars = soup.find_all('li', {"class": "item-params-list-item"})
    for car in char_cars:
        key, item = car.text.strip().split(":")
        data[str(key)] = str(item)
    char_list.append(data)
    return char_list

async def get_text_with_urls(func, urls):
    """
    Создет группу сопрограмм и ожидает их завершения
    """
    # создаем экземпляр клиента
    results = []
    async with aiohttp.ClientSession() as client:
        # создаем корутины
        coroutines_category = [request(client, url) for url in urls]
        completed, pending = await asyncio.wait(coroutines_category)
        for item in completed:
            results.append(item.result())
    with ThreadPoolExecutor(8) as executor:
        for data in executor.map(func, results):
            return data

async def main(urls):
    #"""
    #Создет группу сопрограмм и ожидает их завершения
    #"""
    # создаем экземпляр клиента
    #results = []
    #async with aiohttp.ClientSession() as client:
        # создаем корутины
    #    coroutines_category = [request(client, url) for url in urls]
    #    completed, pending = await asyncio.wait(coroutines_category)
    #    for item in completed:
    #        results.append(item.result())

    #with ThreadPoolExecutor(2) as executor:
    #    for uri_list in executor.map(parsing_uri, results):
    #        return uri_list
    data = await get_text_with_urls(parsing_uri, urls)
    print(data)
    if data:
        car = await get_text_with_urls(parsing_category, data)
        print(car)
        print(len(car))
        return car
    else:
        print("IP временно заблокирован")


async def call_parsing_data():
    for i in range(1):
        url_test.append(f"https://www.avito.ru/izhevsk/avtomobili?p={i+1}")
        data = await main(url_test)
    return data

if __name__ == '__main__':
    for i in range(1):
        url_test.append(f"https://www.avito.ru/izhevsk/avtomobili?p={i+1}")
    log.info("Start")

    # получаем экзепляр цикла событий
    event_loop = asyncio.get_event_loop()

    try:
        t_start = time.time()
        # запуск цикла  обработки событий
        event_loop.run_until_complete(main(url_test))
        t_end = time.time() 
        log.info("Time End: %s", t_end - t_start)
    finally:
        # обязательно закрываем
        event_loop.close()




