Lambda code that invokes a bash script to create the required users for our SSM infrastructure.

Script invoked by this lambda: https://github.com/VIOOH/ssm-linux-user

The above script is invoked by this lambda using the AWS-RunRemoteScript SSM document: https://docs.aws.amazon.com/systems-manager/latest/userguide/integration-remote-scripts.html



