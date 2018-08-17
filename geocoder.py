import requests
import json
import logging


logger = logging.getLogger(__file__)


def format_address(raw_address, country='Россия', province='Кировская область',
                   city='Киров'):
    return ', '.join((country, province, city, raw_address))


def fetch_geocode_yandex_json(address):
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&geocode='
    url += address
    response = requests.get(url)
    return response.text


def get_geoobjects_yandex(geocode):
    return geocode['response']['GeoObjectCollection']['featureMember']


def get_info_from_geoobjects_yandex(geoobject):
    _geoobject = geoobject['GeoObject']
    meta_data_property = _geoobject['metaDataProperty']
    geocoder_meta_data = meta_data_property['GeocoderMetaData']
    address_yandex = geocoder_meta_data['text']

    point = _geoobject['Point']['pos']
    return {
        'address': address_yandex,
        'point': point,
    }


def parse_geocode_yandex_to_geoobjects(geocode):
    geocode_dict = json.loads(geocode)
    try:
        geoobjects_yandex = get_geoobjects_yandex(geocode_dict)
    except AttributeError as e:
        logger.error(
            'Не удалось распарсить строку: {} ({})'.format(geocode, e)
        )
        return []

    geoobjects = []
    for geoobject in geoobjects_yandex:
        try:
            object_info = get_info_from_geoobjects_yandex(geoobject)
        except AttributeError:
            logger.error(
                'Не удалось распарсить строку: {} ({})'.format(geocode, e)
            )
            continue
        geoobjects.append(object_info)
    return geoobjects


def output_result(geoobjects):
    for geoobject in geoobjects:
        print('{};{}'.format(geoobject['point'], geoobject['address']))


def main():
    raw_address = 'Барамзы, Троицкая, 3'
    address = format_address(raw_address)
    geocode = fetch_geocode_yandex_json(address)
    geoobdjects = parse_geocode_yandex_to_geoobjects(geocode)
    output_result(geoobdjects)


if __name__ == '__main__':
    main()
