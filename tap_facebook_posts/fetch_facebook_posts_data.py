import os
import json
import requests

import singer


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schema(entity):
    return singer.utils.load_json(get_abs_path("schemas/{}.json".format(entity)))


def read_configs():
	with open('../config.json') as config_file:
		data = json.load(config_file)
	return data['access_token']


def fetch_node_feed(node_id, access_token=read_configs()):
	"""Fetch the feed with all Post nodes for a given node.

	For more info, see https://developers.facebook.com/docs/graph-api/using-graph-api/

	node_id: int, unique identifier for a given node.
	"""
	BASE_FACEBOOK_GRAPH_API_URL = 'https://graph.facebook.com/v2.11/'

	url = BASE_FACEBOOK_GRAPH_API_URL + str(node_id) + '/feed?access_token=' + access_token
	response = requests.get(url)
	# Raise if not 200 OK
	response.raise_for_status()
	return(json.loads(response.content))


def fetch_posts(access_token=read_configs()):
	schema = load_schema("facebook_posts")
	singer.write_schema("facebook_posts", schema, key_properties=["id"])

	node_feed = fetch_node_feed('officialstackoverflow', access_token)
	
	for record in node_feed['data']:
		singer.write_record('facebook_posts', record)
