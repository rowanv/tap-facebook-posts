import singer

from .fetch_facebook_posts_data import read_configs


LOGGER = singer.get_logger()