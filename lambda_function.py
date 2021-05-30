import json 
import os
import boto3 
from nacl.signing import VerifyKey 
from nacl.exceptions import BadSignatureError 

TEMPLATE_URL = os.environ['template_url']
ROLE_ARN = os.environ['ROLE_ARN']
STACK_NAME = os.environ['StackName']
PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY']

def ValidationError(exception):
    if exception.response['Error']['Code'] == "ValidationError":
        return {
            'statusCode': 200, 
            'body': json.dumps({'type': '4', 'data': {'content': 'Server is not online'}})
        }

    return {
            'statusCode': 200, 
            'body': json.dumps({'type': '4', 'data': {'content': 'An error occured'}})
        }  

def ReturnStackStatus(response):
    print("Executing?")
    StackStatus = response['Stacks'][0]['StackStatus']
    print(response)
    print(StackStatus)
    
    if StackStatus == "CREATE_IN_PROGRESS":
        return {
        'statusCode': 200, 
        'body': json.dumps({'type': '4', 'data': {'content': 'Server is still starting'}})
    }
    elif StackStatus == "CREATE_COMPLETE":
        return {
        'statusCode': 200, 
        'body': json.dumps({'type': '4', 'data': {'content': 'Server is running'}})
    }
    return {
       'statusCode': 200, 
        'body': json.dumps({'type': '4', 'data': {'content': f'Current Stack Status: {StackStatus}'}})
    }


def lambda_handler(event, context):

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    
    signature = event['headers']["x-signature-ed25519"] 
    timestamp = event['headers']["x-signature-timestamp"] 
    body = event['body']
    json_body = json.loads(event['body'])

    try: 
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        if json_body["type"] == 1:
            return {
             'statusCode': 200, 
             'body': json.dumps({'type': 1})
         }
    except (BadSignatureError) as e:
        return {
             'statusCode': 401, 
             'body': json.dumps("Bad Signature")
         } 

    client = boto3.client('cloudformation')
    def checkCFStatus(StackName):
        print(json_body)
        if json_body['data']['options'][0]['value'] == "start":        
            try:
                print("executing")
                response = client.describe_stacks(StackName = StackName)
                return ReturnStackStatus(response)
            except Exception as e:
                print(e)
                if e.response['Error']['Code'] == "ValidationError":
                    try:
                        response = client.create_stack(StackName=StackName, TemplateURL=TEMPLATE_URL, RoleARN=ROLE_ARN)
                        return {
                        'statusCode': 200, 
                        'body': json.dumps({'type': '4', 'data': {'content': 'Starting Server...'}})
                        }
                    except Exception as e:
                        print(e)
                        print(e.response)
                        return {
                        'statusCode': 200, 
                        'body': json.dumps({'type': '4', 'data': {'content': 'An error occured starting the server'}})
                }    
            
            
            
        elif json_body['data']['options'][0]['value'] == "status":
            try:
                response = client.describe_stacks(StackName=StackName)
            except Exception as e:
                ValidationError(e)

            # StackStatus = response['StackStatus']
            ReturnStackStatus(response)
        elif json_body['data']['options'][0]['value'] == "stop":
            try:
                response = client.delete_stack(StackName=StackName, RoleARN=ROLE_ARN)
            except Exception as e:
                ValidationError(e)

    
    checkCFStatus(STACK_NAME)

    
    