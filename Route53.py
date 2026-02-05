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
        zones_response = client.list_hosted_zones()
        found_managed_zone = False
        click.secho("Hosted Zones & Records:", fg='cyan', bold=True)
        
        for zone in zones_response['HostedZones']:
            zone_id_full = zone['Id']
            zone_id = zone_id_full.split('/')[-1]
            
            tags_response = client.list_tags_for_resource(
                ResourceType='hostedzone',
                ResourceId=zone_id
            )
            tags = {tag['Key']: tag['Value'] for tag in tags_response['ResourceTagSet']['Tags']}
            
            if tags.get('CreatedBy') == 'platform-cli':
                found_managed_zone = True
                owner = tags.get('Owner', 'unknown')
                
                click.secho(f"\n Domain: {zone['Name']}", fg='yellow', bold=True)
                click.echo(f"   ID: {zone_id} | Owner: {owner}")

                records_response = client.list_resource_record_sets(HostedZoneId=zone_id_full)
                
                click.echo("   Records:")
                for record in records_response['ResourceRecordSets']:
                    values = [r.get('Value', r.get('DNSName', '')) for r in record.get('ResourceRecords', [])]
                    val_str = ", ".join(values) if values else "Alias/Special"

                    click.echo(f"     - {record['Name']} [{record['Type']}] -> {val_str} (TTL: {record.get('TTL', 'N/A')})")
        
        if not found_managed_zone:
            click.echo("No hosted zones created by this CLI were found.")
            
    except Exception as e:
        click.secho(f"Error listing hosted zones and records: {e}", fg='red')