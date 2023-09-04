#!/usr/bin/env bash

rm -rf dist_reader
pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist_reader

#remove extraneous bits from installed packages
rm -r dist_reader/*.dist-info
cp config.py models.py utils.py message_reader.py dist_reader/
cd dist_reader && zip -r lambda.zip *