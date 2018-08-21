import argparse
import logging
import csv
from typing import List, Dict, Tuple

from geocode_yandex import fetch_geocode_yandex_json
from geocode_yandex import fetch_geocode_yandex_json_from_addresses
from geocode_yandex import parse_geocode_yandex_to_geo_objects
from logger import convert_str_to_logging_level, logger


def parse_argv():
    description_program = '''Приложение для поиска координат объектов \
по адресу'''
    parser = argparse.ArgumentParser(description=description_program)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--address',
        help='''Если опция указана, поиск будет производиться по заданному \
адресу'''
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


def format_address(raw_address: str, country: str ='Россия',
                   province: str='Кировская область',
                   city: str='Киров') -> str:
    return ', '.join((country, province, city, raw_address))


def output_result(geo_objects: List[Dict[str, str]]) -> None:
    for geo_object in geo_objects:  # type: Dict[str, str]
        print('{};{}'.format(geo_object['point'], geo_object['address']))


def get_geo_objects_for_address(raw_address: str) -> List:
    address = format_address(raw_address)
    geocode = fetch_geocode_yandex_json(address)
    return parse_geocode_yandex_to_geo_objects(geocode)


def output_geocode_from_address(raw_address: str) -> None:
    geo_objects = get_geo_objects_for_address(raw_address)
    output_result(geo_objects)


def write_geo_objects_to_csv_writer(csv_writer,
                                    geo_objects: List[Dict[str, str]],
                                    row: List[str]) -> None:
    for geo_object in geo_objects:  # type: Dict[str, str]
        output_row = [geo_object['point'], geo_object['address']]
        output_row += row
        csv_writer.writerow(output_row)


def _set_geocode_to_csv(csv_file: str) -> None:
    with open(csv_file, newline='') as input_file, open('output_'+csv_file, 'w', newline='') as output_file:
        output_writer = csv.writer(output_file)
        for row in csv.reader(input_file):  # type: List[str]
            raw_address = row[0]  # type: str
            geo_objects = get_geo_objects_for_address(raw_address)  # type: list
            write_geo_objects_to_csv_writer(output_writer, geo_objects, row)


def read_csv(csv_file: str) -> List[List[str]]:
    try:
        with open(csv_file, newline='') as input_file:
            input_reader = csv.reader(input_file)
            input_data = [row for row in input_reader]  # type: List[List[str]]
    except IOError as e:
        logger.error(e)
        raise e
    return input_data


def write_geocode_to_csv(csv_file: str,
                         geo_objects_for_all_addresses: List,
                         addresses: Dict[str, List[str]]) -> None:
    try:
        with open(csv_file, 'w', newline='') as output_file:
            output_writer = csv.writer(output_file)
            for geo_objects, address in geo_objects_for_all_addresses:
                row = addresses.get(address, [])  # type: List[str]
                write_geo_objects_to_csv_writer(
                    output_writer, geo_objects, row
                )
    except IOError as e:
        logger.error(e)
        raise e


def _set_geocode_to_csv_for_async(csv_file: str) -> None:
    input_data = read_csv(csv_file)
    # Словарь используем для быстрого поиска! Асинхронные запросы возвращают в
    # ответы в случайном порядке, приходится искать к какому адресу относится
    # тот или иной ответ
    addresses = {
        format_address(address): [address]+_
        for address, *_ in input_data
    }  # type: Dict[str, List[str]]
    done, _ = fetch_geocode_yandex_json_from_addresses(addresses.keys())
    geo_objects_for_all_addresses = []  # type: List[Tuple[list, str]]
    for fut in done:
        response, address = fut.result()  # type: (dict, str)
        geo_objects = parse_geocode_yandex_to_geo_objects(response)  # type: list
        geo_objects_for_all_addresses.append((geo_objects, address))
    write_geocode_to_csv(
        'output_'+csv_file, geo_objects_for_all_addresses, addresses
    )


def set_geocode_to_csv(csv_file: str, is_async=True) -> None:
    try:
        if is_async:
            _set_geocode_to_csv_for_async(csv_file)
        else:
            _set_geocode_to_csv(csv_file)
    except IOError as e:
        logger.error(e)
        raise e


def main() -> None:
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
