# Addok plugin for Luxemburg specifics

## Installation

    pip install addok-luxemburg


## Configuration

- Add QUERY_PROCESSORS_PYPATHS

    QUERY_PROCESSORS_PYPATHS = [
        …,
        "addok_luxemburg.extract_address",
        "addok_luxemburg.clean_query",
    ]

- Add PROCESSORS_PYPATHS

    PROCESSORS_PYPATHS = [
        …,
        "addok_luxemburg.glue_ordinal",
        "addok_luxemburg.fold_ordinal",
        "addok_luxemburg.flag_housenumber",
        …,
    ]

- Replace default `make_labels` by luxemburg dedicated one:

    SEARCH_RESULT_PROCESSORS_PYPATHS = [
        'addok_luxemburg.make_labels',
        …,
    ]
