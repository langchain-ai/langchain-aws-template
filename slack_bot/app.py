from aws_cdk import (
    App, Duration, Stack, 
    aws_apigateway as apigateway, 
    aws_lambda as lambda_, 
    aws_secretsmanager as secretsmanager,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_lambda_event_sources as event_sources,
    RemovalPolicy
)
import config


class SlackBotApp(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        table = dynamodb.Table(self, "table", table_name=config.config.DYNAMODB_TABLE_NAME, 
            partition_key=dynamodb.Attribute(name="SessionId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        queue = sqs.Queue(
            self, 
            config.config.MESSAGE_QUEUE_NAME, 
            queue_name=config.config.MESSAGE_QUEUE_NAME,
            fifo=True,
            visibility_timeout=Duration.minutes(5)
        )

        layer = lambda_.LayerVersion.from_layer_version_arn(
            self,
            "SecretsExtensionLayer",
            layer_version_arn=config.config.SECRETS_EXTENSION_ARN
        )

        # Reader lambda
        handler = lambda_.Function(self, "SlackBotReader",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("dist_reader/lambda.zip"),
            handler="message_reader.handler",
            layers=[layer],
            timeout=Duration.minutes(1)
        )

        queue.grant_send_messages(handler)
        table.grant_read_write_data(handler)

        secret = secretsmanager.Secret.from_secret_name_v2(self, 'secret', config.config.API_KEYS_SECRET_NAME)
        secret.grant_read(handler)
        

        api = apigateway.RestApi(self, "slack-bot-api",
            rest_api_name="Slack bot service api",
            description="Recieves and processes messages from slack, calling an LLM chain to respond to direct messages."
        )

        post_integration = apigateway.LambdaIntegration(handler)

        api.root.add_method(
            "POST", 
            post_integration
        )

        # Writer lambda
        writer_handler = lambda_.Function(self, "SlackBotWriter",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("dist_writer/lambda.zip"),
            handler="message_writer.handler",
            layers=[layer],
            timeout=Duration.minutes(5)
        )
        secret.grant_read(writer_handler)
        queue.grant_consume_messages(writer_handler)
        table.grant_read_write_data(writer_handler)

        writer_handler.add_event_source(event_sources.SqsEventSource(queue))


app = App()
SlackBotApp(app, "SlackBotApp")
app.synth()