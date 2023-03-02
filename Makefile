.PHONY: clean dist bundle deploy

clean:
	@echo "Cleaning dist..."
	rm -rf dist

dist: clean
	@echo "Creating dist dir..."
	mkdir dist

bundle: dist
	@echo "Bundling the lambda assets..."
	./bundle.sh

deploy: bundle
	@echo "Deploying..."
	cdk deploy
