.PHONY: clean dist bundle deploy diff run

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

run:
	cd streamlit_app && streamlit run app.py