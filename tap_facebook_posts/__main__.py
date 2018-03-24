#!/usr/bin/env python3
import argparse
import json

import singer

from .fetch_facebook_posts_data import fetch_posts


logger = singer.get_logger()


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config', help='Config file', required=True)
    parser.add_argument(
        '-s', '--state', help='State file')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    with open(args.config) as config_file:
        config = json.load(config_file)

    if 'access_token' not in config:
        logger.fatal("Missing required configuration keys: {}".format('access_token'))
        exit(1)

    try:
        fetch_posts(access_token=config['access_token'])
    except Exception as exception:
        logger.critical(exception)
        raise exception



if __name__ == '__main__':
    main()
