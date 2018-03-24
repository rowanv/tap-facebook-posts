#!/usr/bin/env python3
import singer

from .fetch_facebook_posts_data import read_configs


LOGGER = singer.get_logger()



def main_implementation():
	ars = util.parse_args(["access_token"])
	config = args.config
	ACCESS_TOKEN = config.pop('access_token')


def main():
	try:
		main_implementation()
	except Exception as exception:
		logger.critical(exception)
		raise exception



if __name__ == '__main__':
	main()
