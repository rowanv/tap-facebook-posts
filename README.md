# tap-facebook-posts
Singer.io tap for getting Facebook posts from the Facebook Graph API.


This tap:
- Pulls posts data for a given node from the [Facebook Graph API][https://developers.facebook.com/docs/graph-api]. If no state is specified, it will pull all available data for the feed.
 

# Quick Start

1. Install 

```
pip3 install tap-facebook-posts
```

2. Create the config file

Create a JSON file called `config.json`. Its contents should look like:

```
  {
  	"access_token": "<YOUR_FACEBOOK_ACCESS_TOKEN>"
  }
```

3. Run the tap
```
tap-facebook-posts -c config.json
```


# Development
## Running un-packaged tap
```
cd tap_facebook_posts
python . -c ../config.json
```
```
python -m tap_facebook_posts -c ../config.json
```

## Running tests
Install the requirements in `requirements-dev.txt`. Then, run the tests with `nosetests`.

# Deploy
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