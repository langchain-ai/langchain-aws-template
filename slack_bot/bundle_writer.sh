#!/usr/bin/env bash

pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist_writer
#openai doesn't have a binary distribution, so need a separate install
pip install -I openai -t dist_writer 

#remove extraneous bits from installed packages
rm -r dist_reader/*.dist-info
cp config.py memory.py models.py chain.py message_writer.py dist_writer/
cd dist_writer && zip -r lambda.zip *
