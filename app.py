from aws_cdk import (App, Stack, aws_apigateway as apigateway, aws_lambda as lambda_)

class LangChainApp(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        handler = lambda_.Function(self, "LangChainHandler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("src"),
            handler="main.handler"
        )

        api = apigateway.RestApi(self, "langchain-api",
            rest_api_name="LangChain Service Api",
            description="Showcases langchain use of llm models"
        )

        api.add_model("RequestModel", content_type="application/json", 
            model_name="RequestModel",
            schema={
                "title": "requestParameters",
                "type": apigateway.JsonSchemaType.STRING,
                "properties": {
                    "prompt": {
                        "type": apigateway.JsonSchemaType.STRING
                    }
                }
            }
        )

        post_integration = apigateway.LambdaIntegration(handler)

        api.root.add_method("POST", post_integration)

app = App()
LangChainApp(app, "LangChainApp")
app.synth()