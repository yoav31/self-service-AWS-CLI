import boto3
import click

def create_instance(name, type, AMI_name, count):
    if AMI_name.lower() == 'amazon-linux' :
        ami_id = 'ami-0532be01f26a3de55'  
    elif AMI_name.lower() == 'ubuntu' :
        ami_id = 'ami-0b6c6ebed2801a5cb'     
    else:
        click.secho("Unsupported AMI specified. Use amazon-linux or ubuntu." , fg='red')
        return
    
    if type not in ['t2.small', 't3.micro']:
        click.secho(f"Error: {type} is not allowed. Use only t2.small or t3.micro ", fg='red')
        return
    if count >2 or count <1:
        click.secho(f"Error: You can create only 1 or 2 instances at a time. You requested {count} instances.", fg='red')
        return
    
    ec2_resource = boto3.resource('ec2', region_name='us-east-1')
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    
    existing_instances = ec2_client.describe_instances(
    Filters=[
        {'Name': 'tag:CreatedBy', 'Values': ['platform-cli']},
        {'Name': 'instance-state-name', 'Values': ['running', 'pending']},
    ]
    )
    
    count_existing = sum(len(r['Instances']) for r in existing_instances['Reservations'])
    if count_existing >= 2:
        click.secho(f"limmit reached! You have {count_existing} running instances, no more than 2 running instances created by this CLI", fg='red', bold=True)
        return

    """Create EC2 instances with specified parameters"""
    try:
        click.echo(f"Launching {AMI_name} instance...")
        instances = ec2_resource.create_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=count,
            InstanceType=type,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': name},
                    {'Key': 'CreatedBy', 'Value': 'platform-cli'},
                    {'Key': 'Owner', 'Value': 'yoavvaknin'} 
                ]
            }]
        )
        for instance in instances:
            click.secho(f" Created EC2 instance: {instance.id}", fg='green', bold=True)
            
    except Exception as e:
        click.secho(f" AWS Error: {e}", fg='red')

def manage_instance(name, action):
    """Start or stop an EC2 instance by name"""
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [name]},
                {'Name': 'tag:CreatedBy', 'Values': ['platform-cli']}
            ]
        )
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance['InstanceId'])
        
        if not instances:
            click.secho(f"No EC2 instance found with name: {name}", fg='red')
            return
        
        if action.lower() == 'start':
            ec2_client.start_instances(InstanceIds=instances)
            click.secho(f"Started instance(s) with name: {name}", fg='green')
        elif action.lower() == 'stop':
            ec2_client.stop_instances(InstanceIds=instances)
            click.secho(f"Stopped instance(s) with name: {name}", fg='green')
        else:
            click.secho("Invalid action. Use 'start' or 'stop'.", fg='red')
    
    except Exception as e:
        click.secho(f" AWS Error: {e}", fg='red')

        
def list_instances():
    """List all EC2 instances"""    
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:CreatedBy', 'Values': ['platform-cli']}
            ]
        )
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
                instances.append(instance_info)
        
        if not instances:
            click.secho("No EC2 instances found created by this CLI.", fg='yellow')
            return
        
        for inst in instances:
            click.secho(f"Instance ID: {inst['InstanceId']}, Type: {inst['InstanceType']}, State: {inst['State']}, Tags: {inst['Tags']}", fg='cyan')
    
    except Exception as e:
        click.secho(f" AWS Error: {e}", fg='red')
    