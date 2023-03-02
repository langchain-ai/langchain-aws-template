rm -rf dist
mkdir dist
pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist
pip install -I openai -t dist
rm -r dist/*.dist-info
cp config.py memory.py chain.py main.py dist/
cd dist && zip -r lambda.zip *