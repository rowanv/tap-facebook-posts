#!/bin/bash

# Check that source has correct formatting
autopep8 tap_facebook_posts/*/*.py -r --diff

# More comprehensive static analysis, complexity check
flake8 tap_facebook_posts/