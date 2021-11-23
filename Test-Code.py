import boto3
import time
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    regionsEC2 = []
    failedEC2 = []

    ec2Client = boto3.client('ec2', region_name='eu-west-1')

    regions = ec2Client.describe_regions()

    for region in regions['Regions']:
        regionsEC2.append(region['RegionName'])

    for r in regionsEC2:
        allEC2 = []
        windowsEC2 = []

        ec2 = boto3.resource('ec2', region_name=r)
        ssm = boto3.client('ssm', region_name=r)

        print("Checking region: " + r)

        # Find all instances.
        instances = ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': [
                        'running',
                    ]
                },
            ]
        )

        for instance in instances:
            allEC2.append(instance.id)

        # Find Windows instances.
        instances = ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': [
                        'running',
                    ]
                },
                {
                    'Name': 'platform',
                    'Values': [
                        'windows',
                    ]
                },
            ]
        )

        for instance in instances:
            windowsEC2.append(instance.id)

        # Remove windows instances from list of instances.
        if len(windowsEC2) > 0:
            for w in windowsEC2:
                allEC2.remove(w)

        for i in allEC2:
            print("Attempting to send command to instance: " + i + " in region " + r)

            try:
                response = ssm.send_command(
                    InstanceIds=[i],
                    DocumentName='AWS-RunRemoteScript',
                    Parameters={
                        'sourceType': ['GitHub'],
                        "sourceInfo":["{\n\"owner\" : \"VIOOH\",\n\"repository\" : \"ssm-linux-users\",\n\"path\" : \"script.sh\",\n\"getOptions\" : \"branch:main\"}"],
                        'commandLine': ["./script.sh"]
                    }
                )
                command_id = response['Command']['CommandId']
                print("Command ID: " + command_id)
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidInstanceId' or e.response['Error']['Code'] == 'TargetNotConnected':
                    print("Instance ID not recognised. Check instance meets SSM pre-requisites.")
                    failedEC2.append(i)
                    print("")
                else:
                    print("Unknown exception occurred. Check logs.")
                    raise e
            else:
                time.sleep(2)
                output = ssm.get_command_invocation(CommandId=command_id, InstanceId=i)

                if output['Status'] == "Success":
                    print("Script reported as successfully run.")
                    print("")
                else:
                    print("Something went wrong.")
                    print("")
    print("The following instances could not be reached.")
    print(failedEC2)
