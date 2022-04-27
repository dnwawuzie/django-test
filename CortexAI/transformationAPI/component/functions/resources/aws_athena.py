import boto3
import time
from transformationAPI.component.functions.resources.aws_session import session_creator

AWS_CATALOGUE = 'AwsDataCatalog'
#BUFFER_LOCATION = 's3://a-c-mc-p-dhub-dhub/querydata/'
#BUFFER_BUCKET = 'a-c-mc-p-dhub-dhub'
#BUFFER_FOLDER = 'querydata/'


def display_databases(environment):
    '''
    display an athena database

    examples:
        database1: database
        database2: database

    Args:
        environment: name of the environment
    '''

    #might need next token

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')

    else:
        session = session_creator(environment)

    client = session.client('athena')
    response = client.list_databases(
        CatalogName=AWS_CATALOGUE
    )

    database_list = {}

    for base in response['DatabaseList']:
        database_list[base['Name']] = 'database'
    #env_list = {environment[__TABLE_PRIMARY_KEY]: environment["status"] for environment in environments}

    return database_list


def display_tables(database, environment):
    '''
    display all tables in an athena database

    examples:
        table1: table
        table2: table

    Args:
        database: name of the athena database
        environment: name of the environment
    '''
    #might need next token

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
    else:
        session = session_creator(environment)

    client = session.client('athena')
    response = client.list_table_metadata(
        CatalogName=AWS_CATALOGUE,
        DatabaseName=database
    )

    table_list = {}

    for table in response['TableMetadataList']:
        table_list[table['Name']] = 'table'

    return table_list


def display_row_count(table, database, environment):
    '''
    display the row count of an athena database table

    examples:
        123

    Args:
        table: name of the Athena table
        database: name of the Athena database
        environment: name of the environment
    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
    else:
        session = session_creator(environment)

    client = session.client('athena')

    query = 'SELECT COUNT(*) FROM ' + database + '.' + table
    response_query_execution_id = run_athena_query(client, query, database)

    result = athena_poll(response_query_execution_id, client, 'row_count')
    if "_col0" in result:
        result.pop('_col0')
    return result


def display_columns(table, database, environment):
    '''
    display the column names for an Athena table

    examples:
        Country
        Postal Code
        Name

    Args:
        table: name of the Athena table
        database: name of the Athena database
        environment: name of the environment
    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
    else:
        session = session_creator(environment)

    client = session.client('athena')

    query = 'SHOW COLUMNS FROM ' + database + '.' + table
    response_query_execution_id = run_athena_query(client, query, database)

    result = athena_poll(response_query_execution_id, client, 'column')
    return result


def run_athena_query(client, query, database, bucket, key):
    '''
    run an athena query

    examples:
        create table statements

    Args:
        client: the boto3 client
        query: the query to run in athena
        database: the database to run the query on
        bucket: the location of the bucket to store the query results
        key: the kms key to access the athena table
    '''

    buffer_location = "s3://" + bucket + "/querydata/"
    response_query_execution_id = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database,
            'Catalog': AWS_CATALOGUE
        },
        ResultConfiguration={
            'OutputLocation': buffer_location,
            'EncryptionConfiguration': {
                'EncryptionOption': 'CSE_KMS',
                'KmsKey': key
            }
        },
        WorkGroup='primary'
    )

    return response_query_execution_id


def athena_poll(response_query_execution_id, client, request_type):
    '''
    check if the Athena query completed

    Args:
        response_query_execution_id: the id for the athena query that was previously run
        client: the boto3 client
        request_type: is the request to look at column names or row counts
    '''

    result = ''

    wait = True
    if not wait:
        return response_query_execution_id['QueryExecutionId']
    else:
        response_get_query_details = client.get_query_execution(
            QueryExecutionId=response_query_execution_id['QueryExecutionId']
        )
        status = 'RUNNING'
        iterations = 360  # 30 mins

        while (iterations > 0):
            iterations = iterations - 1
            response_get_query_details = client.get_query_execution(
                QueryExecutionId=response_query_execution_id['QueryExecutionId']
            )
            status = response_get_query_details['QueryExecution']['Status']['State']

            if (status == 'FAILED') or (status == 'CANCELLED'):
                return False, False

            elif status == 'SUCCEEDED':
                location = response_get_query_details['QueryExecution']['ResultConfiguration']['OutputLocation']

                ## Function to get output results
                response_query_result = client.get_query_results(
                    QueryExecutionId=response_query_execution_id['QueryExecutionId']
                )
                result_data = response_query_result['ResultSet']

                result = grab_result(response_query_result, request_type)
                iterations = 0
        else:
            time.sleep(5)
    return result


def grab_result(response_query_result, request_type):
    '''
    check if the Athena query completed

    example:
        Athena query result

    Args:
        response_query_result: the result from the query
        request_type: is the request to look at column names or row counts
    '''

    result = {}
    if len(response_query_result['ResultSet']['Rows']) > 0:
        for row in response_query_result['ResultSet']['Rows']:
            value = [obj['VarCharValue'] for obj in row['Data']]
            text = value[0].replace(" ", "")
            result[text] = request_type
        return result

    else:
        return result


def get_kms_key(environment, bucket):
    '''
    grab the kms key for the bucket (used to make athena queries)

    Args:
        environment: the name of the spoke environment
        bucket: the bucket that is being copied
    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
    else:
        session = session_creator(environment)

    client = session.client('s3')
    response = client.get_bucket_encryption(Bucket=bucket)
    key = response['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID']
    return key

