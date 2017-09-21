# Addok plugin for Luxembourg specifics

## Installation

    pip install addok-luxembourg


## Configuration

- Add QUERY_PROCESSORS_PYPATHS

    QUERY_PROCESSORS_PYPATHS = [
        …,
        "addok_luxembourg.extract_address",
        "addok_luxembourg.clean_query",
    ]

- Add PROCESSORS_PYPATHS

    PROCESSORS_PYPATHS = [
        …,
        "addok_luxembourg.glue_ordinal",
        "addok_luxembourg.fold_ordinal",
        "addok_luxembourg.flag_housenumber",
        …,
    ]

- Replace default `make_labels` by luxembourg dedicated one:

    SEARCH_RESULT_PROCESSORS_PYPATHS = [
        'addok_luxembourg.make_labels',
        …,
    ]
