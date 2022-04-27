import boto3
from transformationAPI.component.functions.resources.aws_dynamodb import get_all_environment_properties

def session_finder(location):
    '''
        find the arn for the environment

        Examples:
            an arn

        Args:
            location = 'environment_name'

    '''

    item = get_all_environment_properties(location)

    return item['arn']

def session_builder(role_arn):
    '''
        get the credentials for an environment based on an arn

        Examples:
            username and password for an environment

        Args:
            role_arn = 'environment_arn'

    '''

    sts = boto3.client('sts', region_name="ca-central-1")
    token = sts.assume_role(RoleArn=role_arn, RoleSessionName="Session1")
    credentials = token['Credentials']

    return credentials

def session_creator(location):
    '''
        create a session

        Examples:
            session for use in boto3

        Args:
            location = 'environment_name'

    '''

    role_arn = session_finder(location)
    credentials = session_builder(role_arn)
    session = boto3.session.Session(region_name='ca-central-1', aws_access_key_id=credentials['AccessKeyId'],
                                    aws_session_token=credentials['SessionToken'],
                                    aws_secret_access_key=credentials['SecretAccessKey'])

    return session