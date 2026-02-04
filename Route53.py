import boto3
import click

def create_hosted_zone(domain):
    client = boto3.client('route53')
    try:
        response = client.create_hosted_zone(
            Name=domain,
            CallerReference=domain,
            HostedZoneConfig={
                'Comment': 'Hosted zone for ' + domain,
                'PrivateZone': False
            }
        )
        # Tag the hosted zone separately
        client.change_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=response['HostedZone']['Id'].split('/')[-1],
            AddTags=[
                {'Key': 'Name', 'Value': domain},
                {'Key': 'CreatedBy', 'Value': 'platform-cli'},
                {'Key': 'Owner', 'Value': 'yoavvaknin'}
            ]
        )
        click.secho(f"Hosted zone created: {response['HostedZone']['Id']}", fg='green')
    except Exception as e:
        click.secho(f"Error creating hosted zone: {e}", fg='red')




def manage_hosted_records(domain, ip_address, action):
    client = boto3.client('route53')
    try:
        # 1. Find the Zone ID by name
        zones = client.list_hosted_zones_by_name(DNSName=domain)
        if not zones['HostedZones'] or zones['HostedZones'][0]['Name'] != f"{domain}.":
            click.secho(f"No hosted zone found for: {domain}", fg='red')
            return
            
        zone_id = zones['HostedZones'][0]['Id'].split('/')[-1]

        # 2. Check permissions - does the Zone belong to the CLI?
        tags_resp = client.list_tags_for_resource(ResourceType='hostedzone', ResourceId=zone_id)
        tags = {tag['Key']: tag['Value'] for tag in tags_resp['ResourceTagSet']['Tags']}
        
        if tags.get('CreatedBy') != 'platform-cli':
            click.secho(f"Access Denied: Zone {domain} was not created by this CLI.", fg='red', bold=True)
            return

        action_type = action.upper() 
        if action.upper() in ['CREATE', 'DELETE', 'UPSERT']:
            action_type = action.upper() 
        elif action_type == 'UPDATE':
            action_type = 'UPSERT'    
        else:
            click.secho("Invalid action. Use 'create', 'update', or 'delete'.", fg='red')
            return
        
        client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': action_type,
                    'ResourceRecordSet': {
                        'Name': domain, 
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': ip_address}]
                    }
                }]
            }
        )
        click.secho(f"Record {action_type} successful for {domain} -> {ip_address}", fg='green', bold=True)
    except Exception as e:
        click.secho(f"Error managing records: {e}", fg='red')
        
def list_hosted_zones():
    client = boto3.client('route53')
    try:
        zones = client.list_hosted_zones()
        click.secho("Hosted Zones:", fg='cyan', bold=True)
        for zone in zones['HostedZones']:
            click.secho(f"- {zone['Name']} (ID: {zone['Id']})", fg='yellow')
    except Exception as e:
        click.secho(f"Error listing hosted zones: {e}", fg='red')        