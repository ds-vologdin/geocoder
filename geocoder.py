import requests


def format_address(raw_address):
    return raw_address


def fetch_geocode_yandex(address):
    url = 'https://geocode-maps.yandex.ru/1.x/?format=json&geocode='
    url += address
    response = requests.get(url)
    return response.text


def parse_geocode_yandex_to_geoobjects(geocode):
    return geocode


def output_result(geoobjects):
    print(geoobjects)


def main():
    raw_address = 'Кировская область, Киров, ул. Молодой Гвардии, д. 90'
    address = format_address(raw_address)
    geocode = fetch_geocode_yandex(address)
    geoobdjects = parse_geocode_yandex_to_geoobjects(geocode)
    output_result(geoobdjects)


if __name__ == '__main__':
    main()
