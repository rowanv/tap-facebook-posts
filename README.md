# tap-facebook-posts
Singer.io tap for getting Facebook posts from the Facebook Graph API.
 

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
## Running tests
Install the requirements in `requirements-dev.txt`. Then, run the tests with `nosetests`.