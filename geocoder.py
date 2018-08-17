from geocode_yandex import fetch_geocode_yandex_json
from geocode_yandex import parse_geocode_yandex_to_geoobjects


def format_address(raw_address, country='Россия', province='Кировская область',
                   city='Киров'):
    return ', '.join((country, province, city, raw_address))


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
