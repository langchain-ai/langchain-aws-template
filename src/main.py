import json

def handler(event, context): 
    body = json.loads(event["body"])
    
    if "prompt" not in body:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "status": "error",
                "message": "prompt missing in payload"
            })
            
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "response": f"Here is the input prompt: \n {body['prompt']}"
        })
    }