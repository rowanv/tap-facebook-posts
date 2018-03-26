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
    required_config_vars = ['access_token', 'node_id', ]
    for r in required_config_vars:
        if r not in config:
            logger.fatal("Missing required configuration keys: {}".format(r))
            exit(1)

    after_state_marker = None
    if args.state:
        with open(args.state) as state_file:
            state = json.load(state_file)
            after_state_marker = state['after']

    try:
        fetch_posts(config['node_id'], access_token=config['access_token'],
                    after_state_marker=after_state_marker)
    except Exception as exception:
        logger.critical(exception)
        raise exception


if __name__ == "__main__":
    main()
