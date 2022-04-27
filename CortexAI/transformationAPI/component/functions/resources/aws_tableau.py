import boto3
import tableauserverclient as TSC
from transformationAPI.component.functions.resources.aws_session import session_creator

#session = boto3.Session(region_name='ca-central-1')

#credentials = session_builder('arn:aws:iam::749300965134:role/dhub-hub-dhubspoke-assumed-role')
#session2 = boto3.session.Session(region_name='ca-central-1', aws_access_key_id=credentials['AccessKeyId'],
#                                 aws_session_token=credentials['SessionToken'],
#                                 aws_secret_access_key=credentials['SecretAccessKey'])

def list_objects(username, password, server, object):

    '''
    Untested but should list all objects in a tableau server

    '''

    tableau_auth = TSC.TableauAuth(username, password)
    server = TSC.Server(server)

    with server.auth.sign_in(tableau_auth):
        endpoint = {
            'workbook': server.workbooks,
            'datasource': server.datasources,
            'view': server.views,
            'job': server.jobs,
            'project': server.projects,
            'webhooks': server.webhooks,
        }.get(object)

        for resource in TSC.Pager(endpoint.get):
            print(resource.id, resource.name)

def copy_bucket_to_bucket(from_bucket, from_bucket_key, to_bucket, to_bucket_key, environment, hub_to_spoke):
    '''
    move a single tableau file from a S3 instance to another S3 instance

    Examples:
        a tableau file in a new bucket

    Args:
        from_bucket = 'my_hub_bucekt_name'
        from_bucket_key = 'Hub/Screenshot_1.png'    this does not require from_bucket
        to_bucket = 'my_spoke_bucket_name'
        to_bucket_key = 'Spoke/Screenshot_1.png'    this does not require to_bucket
        environment = 'environment_name'
        hub_to_spoke = True or False

    '''

    if hub_to_spoke:
        session = boto3.session.Session(region_name='ca-central-1')
        session2 = session_creator(environment)
    else:
        session = session_creator(environment)
        session2 = boto3.session.Session(region_name='ca-central-1')

    s3 = session.client('s3')

    #try:
    #    s3.meta.client.head_bucket(Bucket=from_bucket)
    #except ClientError:
    #    return ("The bucket for the file you are trying to copy either doesn't exist or you do not have access.")

    s32 = session2.client('s3')

    #try:
    #    s32.meta.client.head_bucket(Bucket=to_bucket)
    #except ClientError:
    #    return ("The bucket you are trying to copy to either doesn't exist or you do not have access.")

    source_response = s3.get_object(
        Bucket=from_bucket,
        Key=from_bucket_key
    )

    s32.upload_fileobj(
        source_response['Body'],
        to_bucket,
        to_bucket_key
    )


def tableau_workbook_migration(server, username, password, filepath, site):
    '''
    upload a tableau workbook to a server

    Examples:
        tableau dashboard available in tableau

    Args:
        server = server address
        username = username to sign into server
        password = password to sign into server
        filepath = computer filepath of the workbook to publish
        site = id (contentUrl) of site to sign into

    '''

    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(username, password, site_id=site)
    server = TSC.Server(server)

    overwrite_true = TSC.Server.PublishMode.Overwrite

    print(filepath)

    with server.auth.sign_in(tableau_auth):

        # Step 2: Get all the projects on server, then look for the default one.
        all_projects, pagination_item = server.projects.get()
        default_project = next((project for project in all_projects if project.is_default()), None)

        # Step 3: If default project is found, form a new workbook item and publish.
        if default_project is not None:
            new_workbook = TSC.WorkbookItem(default_project.id)
            new_job = server.workbooks.publish(new_workbook, filepath, overwrite_true)
            print("Workbook published. JOB ID: {0}".format(new_job.id))
        else:
            error = "The default project could not be found."
            raise LookupError(error)

def build_bucket(bucket_name, environment):
    '''
        creates a bucket in an environment

        Examples:
            a bucket in an environment

        Args:
            bucket_name = 'bucket_name'
            environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.resource('s3')
        s3.create_bucket(Bucket=bucket_name)
    else:
        session = session_creator(environment)
        s3 = session.resource('s3')
        s3.create_bucket(Bucket=bucket_name)