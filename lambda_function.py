import json 
import os
import boto3 
from nacl.signing import VerifyKey 
from nacl.exceptions import BadSignatureError 

def lambda_handler(event, context):

    PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY']
    
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    
    signature = event['headers']["x-signature-ed25519"] 
    timestamp = event['headers']["x-signature-timestamp"] 
    body = event['body']

    try: 
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        body = json.loads(event['body'])
        if body["type"] == 1:
            return {
             'statusCode': 200, 
             'body': json.dumps({'type': 1})
         }
        else:
            client = boto3.client('cloudformation')
            def checkCFStatus(StackName):
                try:
                    response = client.describe_stacks(StackName = StackName)
                    if response['StackStatus'] == "CREATE_IN_PROGRESS":
                        return {
                        'statusCode': 200, 
                        'body': json.dumps({'type': '4', 'data': {'content': 'Server is still starting'}})
                    }
                    elif response['StackStatus'] == "CREATE_COMPLETE":
                        return {
                        'statusCode': 200, 
                        'body': json.dumps({'type': '4', 'data': {'content': 'Server has started'}})
                    }
                    else:
                        StackStatus = response['StackStatus']
                        return {
                        'statusCode': 200, 
                        'body': json.dumps({'type': '4', 'data': {'content': f'Stack Status {StackStatus}'}})
                        }
                except Exception as e:
                    print(e)
                    if e.response['Error']['Code'] == "ValidationError":
                        template_url = "https://cf-templates-17vfm34f5w9b5-us-east-1.s3.amazonaws.com/2021147IUX-mcServerDeploy.yml"
                        Role_ARN = "arn:aws:iam::832167807522:role/CloudFormationServiceRole"
                        try:
                            response = client.create_stack(StackName=StackName, TemplateURL=template_url, RoleARN=Role_ARN)
                            return {
                            'statusCode': 200, 
                            'body': json.dumps({'type': '4', 'data': {'content': 'Starting Server...'}})
                            }
                        except Exception as e:
                            print(e)
                            print(e.response)
                            return {
                            'statusCode': 200, 
                            'body': json.dumps({'type': '4', 'data': {'content': 'An exception occured'}})
                    }

            return checkCFStatus(os.environ['StackName'])

    except (BadSignatureError) as e:
        return {
             'statusCode': 401, 
             'body': json.dumps("Bad Signature")
         } 
    