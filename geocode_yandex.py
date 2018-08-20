import requests
import asyncio
from aiohttp import ClientSession
from typing import Dict, List

from logger import logger


async def fetch_geocode_yandex_json_async(address):
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&geocode={}'
    async with ClientSession() as session:
        async with session.get(url.format(address)) as response:
            response_json = await response.json()
            return (response_json, address)


def fetch_geocode_yandex_json_from_addresses(addresses):
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(fetch_geocode_yandex_json_async(address))
        for address in addresses
    ]
    return loop.run_until_complete(asyncio.wait(tasks))


def fetch_geocode_yandex_json(address: str) -> Dict:
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&geocode='
    url += address
    response = requests.get(url)
    return response.json()


def get_geoobjects_yandex(geocode: Dict) -> Dict:
    return geocode['response']['GeoObjectCollection']['featureMember']


def get_info_from_geoobjects_yandex(geoobject: Dict) -> Dict[str, str]:
    _geoobject = geoobject['GeoObject']
    meta_data_property = _geoobject['metaDataProperty']
    geocoder_meta_data = meta_data_property['GeocoderMetaData']
    address_yandex = geocoder_meta_data['text']

    point = _geoobject['Point']['pos']
    return {
        'address': address_yandex,
        'point': point,
    }


def parse_geocode_yandex_to_geoobjects(geocode: Dict) -> List:
    try:
        geoobjects_yandex = get_geoobjects_yandex(geocode)
    except AttributeError as e:
        logger.error(
            'Не удалось распарсить строку: {} ({})'.format(geocode, e)
        )
        return []

    geoobjects = []  # type: List[Dict[str, str]]
    for geoobject in geoobjects_yandex:
        try:
            object_info = get_info_from_geoobjects_yandex(geoobject)
        except AttributeError as e:
            logger.error(
                'Не удалось распарсить строку: {} ({})'.format(geocode, e)
            )
            continue
        geoobjects.append(object_info)
    return geoobjects
