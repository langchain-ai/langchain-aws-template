# langchain-aws-template
This package contains a service api template that deploys a langchain based generative model API backed by a lambda and api gateway.
Package also contains a streamlit demo web app that can connect with the deployed api to test it in a web app.

## Prerequisites
- nodejs 18+
- Python 3.9+
- aws-cdk toolkit (`npm install -g aws-cdk`)
- AWS account configured with credentials (https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_prerequisites)
- openai api key saved in Secrets Manager in your AWS Account
    - Expected secret name is `api-keys`
    - openai key is expected to be stored with `openai-api-key` key

## Deploy to AWS
Clone the repository
```bash
git clone https://github.com/3coins/langchain-aws-template.git
```

Install the dependencies, this creates a conda env named `langchain-aws-service` and activates it
```bash
make setup-service
```

Deploy the stack to your AWS console. 
```bash
make deploy
```

## Executing the API
Note the api-id and resource-id from the deployment step 

```bash
aws apigateway test-invoke-method --rest-api-id <api-id> \
    --http-method POST \
    --body '{"prompt": "explain code: print(\"Hello world\")", "session_id": ""}' \
    --resource-id <resource-id> \
    --output json
```

You can also run the streamlit app to test the api in a web app

## Running the streamlit app
Install dependencies, this creates a conda env named `langchain-aws-streamlit` and activates it
```bash
make setup-streamlit
```

Make sure to update the `<your-api-endpoint>` in `streamlit_app/api.py` to your api gateway endpoint.

Run the streamlit app, this will open the web app in the browser.
```bash
make run
```
