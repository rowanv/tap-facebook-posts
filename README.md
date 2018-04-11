# tap-facebook-posts
Singer.io tap for getting Facebook posts from the Facebook Graph API.


[![PyPI version](https://badge.fury.io/py/tap-facebook-posts.svg)](https://badge.fury.io/py/tap-facebook-posts)



This tap:
- Pulls posts data for a given node from the [Facebook Graph API][https://developers.facebook.com/docs/graph-api]. If no state is specified, it will pull all 
available data for the feed, up to a limit of 50 API calls.
- Outputs the schema for the posts resource
- Prints the 'after' cursor (the next post that one should request from the API) to STATE
- Can fetch all posts after an 'after' cursor if provided with a `-s` flag 

## Connecting tap-facebook-posts

### Quick Start

1. Install 

We recommend using a virtualenv
```
virtualenv -p python3 my_venv
source my_venv/bin/activate
pip install tap-facebook-posts
```

2. Create the config file

Create a JSON file called `config.json`. Its contents should look like:

```
  {
  	"node_id": "<NODE_ID>",
  	"access_token": "<YOUR_FACEBOOK_GRAPH_API_ACCESS_TOKEN>"
  }
```
You can quickly get a Graph API Explorer access token via the [Graph API Explorer][https://developers.facebook.com/tools/explorer?method=GET&path=me%3Ffields%3Did%2Cname&version=v2.12]

3. Run the tap
```
tap-facebook-posts -c config.json
```


4. (Optional) If you'd like to run the tap with a STATE, you should make a JSON file called `state.json`. Its contents should look like:
```
{
	"after": "<YOUR_FACEBOOK_AFTER_STATE_MARKER>"
}
```
You can then run the tap with
```
tap-facebook-posts -c config.json -s state.json
```
If you omit state settings, it will fetch all available posts for the given `node_id`.

## Development
### Running un-packaged tap
```
cd tap_facebook_posts
python . -c ../config.json
```
```
python -m tap_facebook_posts -c ../config.json
```

### Running tests
Install the requirements in `requirements-dev.txt`. Then, run the tests with `nosetests`.
You can check the tap with singer-tools using `singer-check-tap --tap tap-facebook-posts -c config.json`

### Linting
```
bash dev_tools/linter.sh
```

## Deploy
TestPyPI
```
python setup.py sdist
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip install --index-url https://test.pypi.org/simple/ tap-facebook-posts==0.0.2a1
```

ProdPyPI
```
twine upload dist/*
```