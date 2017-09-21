import json

import pytest

from addok.batch import process_documents
from addok.core import search, Result
from addok.ds import get_document
from addok.helpers.text import Token
from addok_luxembourg.utils import (clean_query, extract_address, flag_housenumber,
                                fold_ordinal, glue_ordinal, make_labels,
                                remove_leading_zeros)


@pytest.mark.parametrize("input,expected", [
    ("283, route d'Arlon L-1150 Luxembourg",
     "283 route d'Arlon L-1150 Luxembourg"),
    ("2 Arelerstrooss L-8552 Oberpallen (Uewerpallen)",
     "2 Arelerstrooss L-8552 Oberpallen (Uewerpallen)"),
])
def test_clean_query(input, expected):
    assert clean_query(input) == expected


@pytest.mark.parametrize("input,expected", [
    ("Société MJM BP 1234 L-9874 REMICH",
     "L-9874 REMICH"),
    ('Monsieur Jean Mustermann 71, route du Vin L-1234 DUDELANGE',
     '71 route du Vin L-1234 DUDELANGE'),
])
def test_extract_address(input, expected):
    assert extract_address(input) == expected


@pytest.mark.parametrize("inputs,expected", [
    (['6', 'bis'], ['6bis']),
    (['6'], ['6']),
    (['6', 'avenue'], ['6', 'avenue']),
    (['60', 'bis', 'avenue'], ['60bis', 'avenue']),
    (['600', 'ter', 'avenue'], ['600ter', 'avenue']),
    (['6', 'quinquies', 'avenue'], ['6quinquies', 'avenue']),
    (['60', 'sexies', 'avenue'], ['60sexies', 'avenue']),
    (['600', 'quater', 'avenue'], ['600quater', 'avenue']),
    (['6', 's', 'avenue'], ['6s', 'avenue']),
    (['60b', 'avenue'], ['60b', 'avenue']),
    (['600', 'b', 'avenue'], ['600b', 'avenue']),
    (['241', 'r', 'de'], ['241', 'r', 'de']),
    (['120', 'r', 'renard'], ['120', 'r', 'renard']),
    (['241', 'r', 'rue'], ['241r', 'rue']),
    (['place', 'des', 'terreaux'], ['place', 'des', 'terreaux']),
    (['rue', 'du', 'bis'], ['rue', 'du', 'bis']),
])
def test_glue_ordinal(inputs, expected):
    tokens = [Token(input_) for input_ in inputs]
    assert list(glue_ordinal(tokens)) == expected


@pytest.mark.parametrize("inputs,expected", [
    (['6b'], True),
    (['6'], True),
    (['9303'], True),
    (['93031'], False),  # postcode
    (['6', 'avenue'], True),
    (['60b', 'avenue'], True),
    (['600t', 'avenue'], True),
    (['6c', 'avenue'], True),
    (['60s', 'avenue'], True),
    (['600q', 'avenue'], True),
    (['6s', 'avenue'], True),
    (['60b', 'avenue'], True),
    (['600b', 'avenue'], True),
    (['241', 'r', 'de'], True),
    (['241r', 'rue'], True),
    (['place', 'des', 'terreaux'], False),
    (['rue', 'du', 'bis'], False),
    (['9', 'grand', 'rue'], True),
])
def test_flag_housenumber(inputs, expected):
    tokens = [Token(input_) for input_ in inputs]
    tokens = list(flag_housenumber(tokens))
    assert tokens == inputs
    assert (tokens[0].kind == 'housenumber') == expected


@pytest.mark.parametrize("input,expected", [
    ('60bis', '60b'),
    ('60BIS', '60b'),
    ('60ter', '60t'),
    ('4terre', '4terre'),
    ('60quater', '60q'),
    ('60 bis', '60 bis'),
    ('bis', 'bis'),
])
def test_fold_ordinal(input, expected):
    assert fold_ordinal(Token(input)) == expected


@pytest.mark.parametrize("input,expected", [
    ('03', '3'),
    ('00009', '9'),
    ('02230', '02230'),  # Do not affect postcodes.
    ('0', '0'),
])
def test_remove_leading_zeros(input, expected):
    assert remove_leading_zeros(input) == expected


def test_index_housenumbers_use_processors(config):
    doc = {
        'id': 'xxxx',
        '_id': 'yyyy',
        'type': 'street',
        'name': 'rue des Lilas',
        'city': 'Paris',
        'lat': '49.32545',
        'lon': '4.2565',
        'housenumbers': {
            '1 bis': {
                'lat': '48.325451',
                'lon': '2.25651'
            }
        }
    }
    process_documents(json.dumps(doc))
    stored = get_document('d|yyyy')
    assert stored['housenumbers']['1b']['raw'] == '1 bis'


@pytest.mark.parametrize("input,expected", [
    ('rue du 8 mai troyes', False),
    ('8 rue du 8 mai troyes', '8'),
    ('3 rue du 8 mai troyes', '3'),
    ('3 bis rue du 8 mai troyes', '3 bis'),
    ('3 bis r du 8 mai troyes', '3 bis'),
    ('3bis r du 8 mai troyes', '3 bis'),
])
def test_match_housenumber(input, expected):
    doc = {
        'id': 'xxxx',
        '_id': 'yyyy',
        'type': 'street',
        'name': 'rue du 8 Mai',
        'city': 'Troyes',
        'lat': '49.32545',
        'lon': '4.2565',
        'housenumbers': {
            '3': {
                'lat': '48.325451',
                'lon': '2.25651'
            },
            '3 bis': {
                'lat': '48.325451',
                'lon': '2.25651'
            },
            '8': {
                'lat': '48.325451',
                'lon': '2.25651'
            },
        }
    }
    process_documents(json.dumps(doc))
    result = search(input)[0]
    assert (result.type == 'housenumber') == bool(expected)
    if expected:
        assert result.housenumber == expected


def test_match_housenumber_with_multiple_tokens(config):
    config.SYNONYMS = {'18': 'dix huit'}
    doc = {
        'id': 'xxxx',
        '_id': 'yyyy',
        'type': 'street',
        'name': 'rue du 8 Mai',
        'city': 'Troyes',
        'lat': '49.32545',
        'lon': '4.2565',
        'housenumbers': {
            '8': {
                'lat': '48.8',
                'lon': '2.25651'
            },
            '10': {
                'lat': '48.10',
                'lon': '2.25651'
            },
            '18': {
                'lat': '48.18',
                'lon': '2.25651'
            },
        }
    }
    process_documents(json.dumps(doc))
    result = search('8 rue du 8 mai')[0]
    assert result.housenumber == '8'
    assert result.lat == '48.8'
    result = search('10 rue du 8 mai')[0]
    assert result.housenumber == '10'
    assert result.lat == '48.10'
    result = search('18 rue du 8 mai')[0]
    assert result.housenumber == '18'
    assert result.lat == '48.18'


def test_make_labels(config):
    doc = {
        'id': 'xxxx',
        '_id': 'yyyy',
        'type': 'street',
        'name': 'rue des Lilas',
        'city': 'Paris',
        'postcode': '75010',
        'lat': '49.32545',
        'lon': '4.2565',
        'housenumbers': {
            '1 bis': {
                'lat': '48.325451',
                'lon': '2.25651'
            }
        }
    }
    process_documents(json.dumps(doc))
    result = Result(get_document('d|yyyy'))
    result.housenumber = '1 bis'  # Simulate match_housenumber
    make_labels(None, result)
    assert result.labels == [
        '1 bis rue des Lilas 75010 Paris',
        'rue des Lilas 75010 Paris',
        '1 bis rue des Lilas 75010',
        'rue des Lilas 75010',
        '1 bis rue des Lilas Paris',
        'rue des Lilas Paris',
        '1 bis rue des Lilas',
        'rue des Lilas'
    ]


def test_make_municipality_labels(config):
    doc = {
        'id': 'xxxx',
        '_id': 'yyyy',
        'type': 'municipality',
        'name': 'Lille',
        'city': 'Lille',
        'postcode': '59000',
        'lat': '49.32545',
        'lon': '4.2565',
    }
    process_documents(json.dumps(doc))
    result = Result(get_document('d|yyyy'))
    make_labels(None, result)
    assert result.labels == [
        'Lille',
        '59000 Lille',
        'Lille 59000',
    ]
