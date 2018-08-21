import requests
import asyncio
from aiohttp import ClientSession
from typing import Dict, List, Union, KeysView

from logger import logger


async def fetch_geocode_yandex_json_async(address: str):
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&geocode={}'
    async with ClientSession() as session:
        async with session.get(url.format(address)) as response:
            response_json = await response.json()
            return response_json, address


def fetch_geocode_yandex_json_from_addresses(
        addresses: Union[List[str], KeysView[str]]):
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


def get_geo_objects_yandex(geocode: Dict) -> List[Dict[str, dict]]:
    return geocode['response']['GeoObjectCollection']['featureMember']


def get_info_from_geo_objects_yandex(geo_object: Dict) -> Dict[str, str]:
    _geo_object = geo_object['GeoObject']
    meta_data_property = _geo_object['metaDataProperty']
    geocoder_meta_data = meta_data_property['GeocoderMetaData']
    address_yandex = geocoder_meta_data['text']

    point = _geo_object['Point']['pos']
    return {
        'address': address_yandex,
        'point': point,
    }


def parse_geocode_yandex_to_geo_objects(
        geocode: Dict[str, dict]) -> List[Dict[str, str]]:
    try:
        geo_objects_yandex = get_geo_objects_yandex(geocode)
    except AttributeError as e:
        logger.error(
            'Не удалось распарсить строку: {} ({})'.format(geocode, e)
        )
        return []

    geo_objects = []  # type: List[Dict[str, str]]
    for geo_object in geo_objects_yandex:
        try:
            object_info = get_info_from_geo_objects_yandex(geo_object)
        except AttributeError as e:
            logger.error(
                'Не удалось распарсить строку: {} ({})'.format(geocode, e)
            )
            continue
        geo_objects.append(object_info)
    return geo_objects
