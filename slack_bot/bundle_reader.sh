#!/usr/bin/env bash

pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist_reader

#remove extraneous bits from installed packages
rm -r dist_reader/*.dist-info
cp config.py memory.py models.py message_reader.py dist_reader/
cd dist_reader && zip -r lambda.zip *