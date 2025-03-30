#!/bin/sh

black ./**/*.py
isort --profile=black ./**/*.py
prettier -w **/*.{html,js,css}
