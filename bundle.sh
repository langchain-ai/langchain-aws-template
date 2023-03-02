#!/usr/bin/env bash

pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist
#openai doesn't have a binary distribution, so need a separate install
pip install -I openai -t dist 

#remove extraneous bits from installed packages
rm -r dist/*.dist-info
cp config.py memory.py chain.py main.py dist/
cd dist && zip -r lambda.zip *