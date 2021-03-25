import boto3
def script_handler(events, context):
    client = boto3.client('elb')
    LoadBalancerName = "empty-lb"
    response = client.add_tags(
        LoadBalancerNames=[
            LoadBalancerName,
        ],
        Tags=[
            {
                'Key': 'ConfigUncompliant',
                'Value': 'True'
            },
        ]
    )
    print(response)