def pytest_configure():
    from addok.config import config
    config.QUERY_PROCESSORS_PYPATHS = [
        "addok_luxembourg.extract_address",
        "addok_luxembourg.clean_query",
        "addok_luxembourg.remove_leading_zeros",
    ]
    config.SEARCH_RESULT_PROCESSORS_PYPATHS = [
        'addok.helpers.results.match_housenumber',
        'addok_luxembourg.make_labels',
        'addok.helpers.results.score_by_importance',
        'addok.helpers.results.score_by_autocomplete_distance',
        'addok.helpers.results.score_by_ngram_distance',
        'addok.helpers.results.score_by_geo_distance',
    ]
    config.PROCESSORS_PYPATHS = [
        "addok.helpers.text.tokenize",
        "addok.helpers.text.normalize",
        "addok_luxembourg.glue_ordinal",
        "addok_luxembourg.fold_ordinal",
        "addok_luxembourg.flag_housenumber",
        "addok.helpers.text.synonymize",
    ]
