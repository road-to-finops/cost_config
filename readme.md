# Deploy Config Rules


## EIP
Identify unattached EIP
Auto remindate releaseing them 

* Run this in your terminal
``` aws cloudformation update-stack --stack-name config --template-body file://template.yml --capabilities CAPABILITY_NAMED_IAM ```


awsassume shell --profile sand --duration 60


aws elb add-tags --load-balancer-name my-load-balancer --tags "Key=project,Value=lima" "Key=department,Value=digital-media"

https://aws.amazon.com/blogs/mt/how-to-query-your-aws-resource-configuration-states-using-aws-config-and-amazon-athena/

Last Notes:
* Currently the template deploys successfully creating the lambda to partition
* However cant create the notifcation to trigger the lambda
* S3 relies on current S3 in sandbox as i cant deploy the bucket poly from CF but it can be done manually using the link above
* The delivery channel cant me made without the S3 having the policy

Try usong the Enable config yml in CF folder gotten from AWS in personal account as less restritions
