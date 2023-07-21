#!/usr/bin/env bash

rm -rf dist_writer
pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist_writer
#openai doesn't have a binary distribution, so need a separate install
pip install -I openai -t dist_writer 

#remove extraneous bits from installed packages
rm -r dist_writer/*.dist-info
cp config.py models.py utils.py chain.py message_writer.py dist_writer/
cd dist_writer && zip -r lambda.zip *
