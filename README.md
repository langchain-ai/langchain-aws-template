# langchain-aws-template
This package contains a service api template that deploys a langchain based generative model API backed by a lambda and api gateway.

## Prerequisites
- nodejs 18+
- Python 3.9+
- aws-cdk
- AWS account configured with credentials (https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- openai api key saved in Secrets Manager in your AWS Account

## Deploy to AWS
Clone the repository
```bash
git clone https://github.com/3coins/langchain-aws-template.git
```

Install the aws-cdk tool
```bash
npm install -g aws-cdk
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
