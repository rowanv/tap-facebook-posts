import json


def read_configs():
	with open('config.json') as config_file:
		data = json.load(config_file)
	return data['access_token']
	