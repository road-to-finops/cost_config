import boto3
import os
import json
from botocore.exceptions import ClientError
from time import strftime 
from datetime import datetime

def lambda_handler(event, context):
    
    s3 = boto3.client('s3')
    client = boto3.client('sts')
    
    #define variables for formatted date, and an output file for header row
    now = datetime.now()
    current_time = now.strftime("%m-%d-%Y-%H:%M")
    TransitionOutput = "Bucket Name, Transition In Days, Storage Class, Transition Status"
    
    #add user identity in bucket creation
    user_id = client.get_caller_identity()
    user_role = (user_id['Arn'].split(':')[5]).split('/')[1]

    #create S3 lifecycle policy
    def createPolicy(Name):
        policy = {
                        "Rules": [
                            {
                                "ID": "MPU Role",
                                "Status": "Enabled",
                                "Filter": {
                                    "Prefix": ""
                                },
                                "AbortIncompleteMultipartUpload": {
                                    "DaysAfterInitiation": 7
                                }
                            }
                        ]
                    }
        return policy
    
    #get buckets in the account
    BucketNames = s3.list_buckets()
    for bucket in BucketNames['Buckets']:
        Name = bucket['Name'] 
        try:
            #Case 1 - Check the existing lifecycle policies, if there are any then skip the bucket but record it in the excel for reference
            result = s3.get_bucket_lifecycle_configuration(Bucket=Name) 
            Rules= result['Rules']
            print(Name)
            if any("AbortIncompleteMultipartUpload" in keys for keys in Rules):
                for Rule in Rules:
                    for key, value in Rule.items():
                        if key == 'AbortIncompleteMultipartUpload':
                            Days = Rule[key]['DaysAfterInitiation']
                            TransitionStatus = Name + ',' + str(Days) + ',' + ', No changes made to S3 Lifecycle configuration' 
                            TransitionOutput = TransitionOutput + '\n' + TransitionStatus
            #Additional customization - if you want to modify existing policy, that logic will go here in else block
        except ClientError as err: 
            #Case 2 - if no lifecycle policy exists, then create and attach it to the bucket
            if err.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                policy = createPolicy(Name)
                for p in policy['Rules']:
                    for key, value in p.items():
                        if key =='AbortIncompleteMultipartUpload':
                            Days = p['AbortIncompleteMultipartUpload']['DaysAfterInitiation']
                            TransitionStatus = Name + ',' + str(Days) + ',' + ', Added a new S3 Lifecycle Transition Rule to S3 INT' 
                            TransitionOutput = TransitionOutput + '\n' + TransitionStatus
                s3.put_bucket_lifecycle_configuration(Bucket=Name, LifecycleConfiguration = policy)
            else:
                print ("err.response['Error']['Code']")
                
    try:
        s3.put_object(Body=TransitionOutput,Key='s3automationresultbucket.csv',Bucket=os.environ['outputbucketname'])
        body = ('your lambda function has been executed successfully. Please check the output file saved in S3 bucket - ' + os.environ['outputbucketname'] + ' and File name - s3automationresultbucket.csv')
    except ClientError as err:
        body = err.response['Error']
        
    return {
        'body': body
    }
lambda_handler(None, None)
