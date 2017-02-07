from addok.helpers import yielder

from . import utils
try:
    import pkg_resources
except ImportError:  # pragma: no cover
    pass
else:
    if __package__:
        VERSION = pkg_resources.get_distribution(__package__).version


clean_query = yielder(utils.clean_query)
extract_address = yielder(utils.extract_address)
preprocess_housenumber = utils.preprocess_housenumber
flag_housenumber = utils.flag_housenumber
make_labels = utils.make_labels
remove_leading_zeros = yielder(utils.remove_leading_zeros)
match_housenumber = utils.match_housenumber
