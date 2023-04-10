# Lambda Service
This package contains the infrastructure and the code to deploy and run a backend service that calls an LLM chain (`chain.py`). You can use the included `webapp` to connect to the deployment API Gateway endpoint, that lets you interact with the service from a web application.

## Design
![Lambda Service Design](./images/service_design.svg)

## Code organization
### app.py
Contains the infrastructure code written in CDK that will be deployed to AWS

### config.py
Contains the configuration used by the infrastructure and the application code. The current setup expects the API keys to be stored in Secrets Manager under the name `api-keys`. For example, the secrets in the AWS console will look like this:
```json
{
    "openai-api-key": "<api-key-value>"
}
```

### main.py
Lambda handler that processes the incoming request and calls the LLM chain to generate a reply. 

### chain.py
The LLM chain code that calls the LLM with the input from the user.

## Deploying to AWS

Clone the repository
```bash
git clone https://github.com/3coins/langchain-aws-template.git
```

Move to the package directory
```bash
cd service
```

Install the dependencies; this creates a Conda env named `langchain-aws-service` and activates it.
```bash
conda deactivate
conda env create -f environment.yml # only needed once
conda activate langchain-aws-service
```

Bundle the code for Lambda deployment.
```bash
./bundle.sh
```

Deploy to your AWS account. These steps require that you must have configured the AWS credentials on your machine using the AWS CLI and using an account that has permissions to deploy and create infrastructure. See the [AWS CLI setup page](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html) and the [CDK guide](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) to learn more.
```bash
cdk bootstrap # Only needed once, if you have not used CDK before in your account
cdk deploy
```
After you run the above commands, you will see a list of assets that this code will generate and you will be asked whether you want to proceed. Enter `y` to go ahead with the deployment. Copy and save the API URL generated from the deployment; this will be used when you create the Slack app.

## Executing the API
Note the api-id from the deployment step. This is the first part in the endpoint URL generated from the deployment. For example, api-id is `qkwe1arp` in the endpoint URL `https://qkwe1arp.execute-api.us-east-1.amazonaws.com/prod`.

Get the resource id.
```bash
aws apigateway get-resources --rest-api-id <api-id> --output=text
# you will see an output like this, copy the resource id value, which is 789ai1gbjn in this sample
# ITEMS   789ai1gbjn      /
```

Invoke the rest api.
```bash
aws apigateway test-invoke-method --rest-api-id <api-id> \
    --http-method POST \
    --body '{"prompt": "explain code: print(\"Hello world\")", "session_id": ""}' \
    --resource-id <resource-id> \
    --output json
```

## Demo web application
The `webapp` folder contains a demo web app that uses [streamlit](https://streamlit.io/) to run a web application locally, that you can use to connect with the deployed lambda service. 

Move to the webapp directory
```bash
cd webapp
```

Update the `<your-api-endpoint>` in `api.py` to the API URL generated from the service deployment.

Start the web application
```bash
streamlit run app.py
```

Running the above command will open the application in your default browser.

