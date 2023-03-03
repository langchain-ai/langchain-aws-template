.PHONY: prepare clean dist bundle deploy diff setup_env run

prepare:
	npm install -g aws-cdk

clean:
	@echo "Cleaning dist..."
	cd service && rm -rf dist

dist: clean
	@echo "Creating dist dir..."
	cd service && mkdir dist

bundle: dist
	@echo "Bundling the lambda assets..."
	cd service && ./bundle.sh

deploy: bundle
	@echo "Deploying..."
	cd service && cdk deploy

diff: 
	cd service && cdk diff

setup_env:
	conda env create -f streamlit_app/environment.yml
	conda activate langchain-aws-template

run:
	cd streamlit_app && streamlit run app.py