import boto3
from botocore.exceptions import ClientError

import json
APPLICABLE_RESOURCES = ["AWS::ElasticLoadBalancing::LoadBalancer"]
SECURITY_GROUPS_ALLOWED_PUBLIC_ACCESS = [""]
COMPLIANT = "COMPLIANT"
NON_COMPLIANT = "NON_COMPLIANT"
NOT_APPLICABLE = "NOT_APPLICABLE"


def evaluate_compliance(classic_elb, client):
    try:
        elb_name = classic_elb["LoadBalancerName"]
        instance_health = client.describe_instance_health(LoadBalancerName=elb_name)
        
        if instance_health["InstanceStates"] == []:
            return {
            "compliance_type": NON_COMPLIANT,
            "annotation": "No instances attached",
            "load balancer name": elb_name
            }

        elif instance_health['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                "compliance_type": "NOT_APPLICABLE",
                "annotation": "The configurationItem was deleted and therefore cannot be validated.",
                "load balancer name": elb_name
            }

        elif elb_name in APPLICABLE_RESOURCES:
            return {
                "compliance_type": "NOT_APPLICABLE",
                "annotation": "The rule doesn't apply to resources of type " +
                            elb_name + "."
            }
        else:
            compliance_type = COMPLIANT
            annotation_message = "ELB attached"

            return {
                "compliance_type": compliance_type,
                "annotation": annotation_message,
                "load balancer name": elb_name
            }
        
            
    except ClientError as e:
        return {
            "compliance_type": NON_COMPLIANT,
            "annotation": "describe_elb failure on review " + e
        }



def lambda_handler(event, context):
    print(event)
    client = boto3.client("elb")
    lbs = client.describe_load_balancers()

    for classic_elb in lbs["LoadBalancerDescriptions"]:
        elb_name = classic_elb["LoadBalancerName"]
        evaluation = evaluate_compliance(classic_elb, client)

        config = boto3.client('config')
        print(evaluation)
        # the call to put_evalations is required to inform aws config about the changes
        response = config.put_evaluations(
            Evaluations=[
                {
                    'ComplianceResourceType': "AWS::ElasticLoadBalancing::LoadBalancer",
                    'ComplianceResourceId': elb_name,
                    'ComplianceType': evaluation["compliance_type"],
                    "Annotation": evaluation["annotation"],
                    'OrderingTimestamp': 'Mon, 02 Nov 2020 10:00:06 GMT'
                },
            ],
            ResultToken=event['resultToken'])
