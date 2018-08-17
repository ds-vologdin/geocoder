import argparse
import logging
import csv

from geocode_yandex import fetch_geocode_yandex_json
from geocode_yandex import parse_geocode_yandex_to_geoobjects
from logger import convert_str_to_logging_level, logger


def parse_argv():
    description_programm = '''Приложение для поиска координат объектов \
по адресу'''
    parser = argparse.ArgumentParser(description=description_programm)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--address',
        help='Если опция указан, поиск будет производиться по заданному адресу'
    )
    group.add_argument(
        '--csv-file',
        help='''Найти координаты по адресам, указанным в первом столбце csv
файла. Результат сохраняется в файл с префиксом "output_" (первый столбец -
 координаты, второй - адрес из базы, следующие - содержимое входного файла).
  В случае, когда одному адресу найдено несколько адресов, сохраняются все.'''
    )
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='warning',
        help='Уровень вывода логов. По умолчанию warning.'
    )
    parser.add_argument(
        '--log-file', default='{}.log'.format(__file__.rstrip('.py')),
        help='Имя логфайла. По-умолчанию {}.log'.format(__file__.rstrip('.py'))
    )
    return parser.parse_args()


def format_address(raw_address, country='Россия', province='Кировская область',
                   city='Киров'):
    return ', '.join((country, province, city, raw_address))


def output_result(geoobjects):
    for geoobject in geoobjects:
        print('{};{}'.format(geoobject['point'], geoobject['address']))


def get_geoobdjects_for_address(raw_address):
    address = format_address(raw_address)
    geocode = fetch_geocode_yandex_json(address)
    return parse_geocode_yandex_to_geoobjects(geocode)


def output_geocode_from_address(raw_address):
    geoobdjects = get_geoobdjects_for_address(raw_address)
    output_result(geoobdjects)


def write_geoobjects_to_csv_writer(csv_writer, geoobdjects, row):
    for geoobdject in geoobdjects:
        output_row = [geoobdject['point'], geoobdject['address']]
        output_row += row
        csv_writer.writerow(output_row)


def _set_geocode_to_csv(csv_file):
    with open(csv_file, newline='') as input_file, open('output_'+csv_file, 'w', newline='') as output_file:
        output_writer = csv.writer(output_file)
        for row in csv.reader(input_file):
            raw_address = row[0]
            geoobdjects = get_geoobdjects_for_address(raw_address)
            write_geoobjects_to_csv_writer(output_writer, geoobdjects, row)


def set_geocode_to_csv(csv_file):
    try:
        _set_geocode_to_csv(csv_file)
    except IOError as e:
        logger.error(e)
        raise e


def main():
    args = parse_argv()

    logging.basicConfig(
        filename=args.log_file,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=convert_str_to_logging_level(args.log_level)
    )
    if args.address:
        output_geocode_from_address(args.address)

    if args.csv_file:
        set_geocode_to_csv(args.csv_file)


if __name__ == '__main__':
    main()
