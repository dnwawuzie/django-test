#!/usr/bin/env python
import boto3
import json

__ENVIRONMENT_TABLES = "environments"
__TABLE_PRIMARY_KEY = "environment"
__TABLE_REGION = "ca-central-1"
__S3_RESOURCE = "dynamodb"

session = boto3.Session(region_name='ca-central-1')


def create_connection():
    '''
        create a connecting to the dynamo database
    '''
    dynamodb = session.resource(__S3_RESOURCE, region_name=__TABLE_REGION)
    table = dynamodb.Table(__ENVIRONMENT_TABLES)
    return dynamodb, table


def create_new_environment(items):
    '''
        create an environment

        Examples:
            environment with a list of parameters

        Args:
            items = 'list_of_variables'

    '''

    dynamodb, table = create_connection()
    params = json.loads(items[0])

    if __TABLE_PRIMARY_KEY not in params:
        raise Exception("Primary key not available in the list of items to be inserted")
    response = table.put_item(Item=params)
    return response


def get_all_environment_properties(environment_name):
    '''
        list all environment variables

        Examples:
            list of variables for the environment

        Args:
            environment_name = 'list_of_variables'

    '''

    #used to build sessions

    dynamodb, table = create_connection()
    response = table.get_item(
        Key={
            __TABLE_PRIMARY_KEY: environment_name
        }
    )
    item = response['Item']
    return item

def list_all_environment_properties(environment_name):
    '''
        create an environment

        Examples:
            environment with a list of parameters

        Args:
            items = 'list_of_variables'

    '''

    #used for the get envrionment API call

    #change_environment_parameter(environment_name, 'sagemaker_notebook', get_sagemaker_link(environment_name))
    dynamodb, table = create_connection()
    response = table.get_item(
        Key={
            __TABLE_PRIMARY_KEY: environment_name
        }
    )
    item = response['Item']
    return item


def show_table_status():
    '''
        show environment status

        Examples:
            environments status

    '''

    dynamodb, table = create_connection()
    return table.table_status


def create_environment_table():
    '''
        create an environment table

        Examples:
            environment table

    '''

    dynamodb = session.resource(__S3_RESOURCE, region_name=__TABLE_REGION)
    dynamodb.create_table(
        TableName=__ENVIRONMENT_TABLES,
        KeySchema=[
            {
                'AttributeName': __TABLE_PRIMARY_KEY,
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': __TABLE_PRIMARY_KEY,
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST',
    )


def change_environment_parameter(environment_name, parameter, value):
    '''
        change a parameter for an environment

        Examples:
            arn = new_arn

        Args:
            environment_name - 'environment_name'
            parameter = 'parameter_to_update'
            value = 'value_for_parameter'

    '''

    dynamodb, table = create_connection()
    u_expression = "set " + parameter + "= :g"
    u_expression_values = {":g": value}
    table.update_item(
        Key={
            __TABLE_PRIMARY_KEY: environment_name,
        },
        UpdateExpression=u_expression,
        ExpressionAttributeValues=u_expression_values,
        ReturnValues="UPDATED_NEW"
    )
    return True


def delete_environment_table():
    '''
        delete an environment table

        Examples:
            deletes an environment table

    '''

    dynamodb, table = create_connection()
    response = table.delete()
    return response


def delete_environment(environment_name):
    '''
        create an environment

        Examples:
            environment has been deleted

        Args:
            environment_name = 'environment_name'

    '''

    dynamodb, table = create_connection()
    response = table.delete_item(
        Key={
            __TABLE_PRIMARY_KEY: environment_name
        }
    )
    return response


def change_environment_state(environment_name, env_state):
    '''
        change the state of an environment to running or stopped

        Examples:
            environment stopped or environment running

        Args:
            environment_name = 'environment_name'
            env_state = 'stopped'

    '''

    dynamodb, table = create_connection()
    u_expression = "set my_status = :g"
    u_expression_values = {":g": env_state}
    table.update_item(
        Key={
            __TABLE_PRIMARY_KEY: environment_name,
        },
        UpdateExpression=u_expression,
        ExpressionAttributeValues=u_expression_values,
        ReturnValues="UPDATED_NEW"
    )
    return env_state


def list_all_environment():
    '''
        list the environments

        Examples:
            listing of all environments

    '''

    dynamodb, table = create_connection()
    response = table.scan()
    environments = response['Items']
    env_list = {environment[__TABLE_PRIMARY_KEY]: environment["my_status"] for environment in environments}
    return env_list


def get_sagemaker_link(environment):
    '''
        create a sagemaker link to list with environment parameters

        Examples:
            a sagemaker link with a built in username and password

        Args:
            environment = 'environment_name'

    '''

    env_session = session_creator(environment)
    client = env_session.client('sagemaker')
    notebook = 'dhub-' + environment + '-notebook-instance'
    url = client.create_presigned_notebook_instance_url(NotebookInstanceName=notebook,
                                                        SessionExpirationDurationInSeconds=1800)

    return url['AuthorizedUrl']


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


def main():


    Item = {
        'environment': "aia-bns2",
        'owner': "kovi",
        'owner_email': "kovi@deloitte.ca",
        'status': "Stopped",
        'partner': "nihar",
        'sagemaker_link': "http://abc234/234",
        's3_bucket': "s3a://kovi_bucket"
    }
    # print(list_all_environment())
    # delete_environment ("aia-bn7")
    # print(list_all_environment())
    # change_environment_parameter("aia-scotia",'sagemaker_link2','http://def/def')
    # print(create_new_environment(Item))
    print(list_all_environment())
    # print(get_all_environment_properties("aia-scotia"))
    # print( change_environment_state("aia-scotia", "started"))
    # print(get_all_environment_properties("aia-scotia"))
    # print(show_table_status())


if __name__ == "__main__":
    main()
