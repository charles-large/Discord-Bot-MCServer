# Discord-Bot-MCServer

This project integrates Discord's slash commands or outgoing webhook, to execute a lambda function that will either start, stop or get the status of a cloudformation stack. 
It was originally meant to host a minecraft or valheim server which could be turned on and off on demand through discord, although it could be used to interact with anything that can be hosted in AWS. 

Architecture:

![](https://user-images.githubusercontent.com/70664028/120233952-efa34d00-c224-11eb-805a-8f78a4d2c7ec.png)

First a user will interact with the webhook by using slash commands in discord. The bot is given an address to query for a response, this address would be my api gateway url. API Gateway is then told to forward the request to a specific lambda function. The lambda function then reads the response and responds accordingly based on the value of the input. For instance, if the value in the slash command is "start", the server will check whether the server is started and if not start it. It will do this by sending a boto3 request to launch a specified template in an S3 bucket. Once it executes, it will return a response to the user. 
