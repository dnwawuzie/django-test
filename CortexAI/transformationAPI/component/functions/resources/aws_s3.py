import logging
import boto3
from botocore.exceptions import ClientError
import time
from transformationAPI.component.functions.resources.aws_session import session_creator
from transformationAPI.component.functions.resources.aws_athena import run_athena_query, get_kms_key

#TODO due diligence on checking that all atehna tables are a subfolder of a bucket -  Alex asked for this
#TODO add an if statement to ignore views when copying databases

AWS_CATALOGUE = 'AwsDataCatalog'
BUFFER_LOCATION = 's3://a-c-mc-p-dhub-dhub/querydata/'
BUFFER_BUCKET = 'a-c-mc-p-dhub-dhub'
BUFFER_FOLDER = 'querydata'


def build_bucket(bucket_name, environment):
    """
        create an s3 bucket

        Examples:
            a bucket in a specific environment

        Args:
            bucket_name = 's3_bucket'
            environment = 'environment_name'

    """

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.resource('s3')

    else:
        session = session_creator(environment)
        s3 = session.resource('s3')

    s3.create_bucket(Bucket=bucket_name)


def upload_file(file_name, bucket_name, environment):
    """
        upload a file to an environment

        Examples:
            a file in a specified environment

        Args:
            file_name = 'file_name'
            bucket_name = 'bucket_name'
            environment = 'environment_name'

    """

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.client('s3')
    else:
        session = session_creator(environment)
        s3 = session.client('s3')

    object_name = file_name
    response = s3.upload_file(file_name, bucket_name, object_name)

    return response


def download_file(file_path, bucket, file_name, environment):
    '''
        download a file from s3 to local

        Examples:
            a file in a local environment

        Args:
            file_path = 'path_to_file'
            bucket = 'bucket_name'
            file_name = 'name_of_file'
            environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.client('s3')
    else:
        session = session_creator(environment)
        s3 = session.client('s3')

    s3.download_file(bucket, file_path, file_name)


def list_files(list_bucket, environment):
    '''
        list all files in an s3 bucket

        Examples:
            file1
            file2
            file3

        Args:
            list_bucket = 'bucket_name'
            environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.resource('s3')
    else:
        session = session_creator(environment)
        s3 = session.resource('s3')

    bucket = s3.Bucket(list_bucket)

    dict = {}

    dict[list_bucket] = []

    for obj in bucket.objects.all():
        dict[list_bucket].append(obj.key)

    return dict


def list_files_contents(bucket, environment):
    '''
        list contents in a file

        Examples:
            adlfjaldfksdaf
            asdlfjldjfsd

        Args:
            bucket = 'bucket_name'
            environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.client('s3')
    else:
        session = session_creator(environment)
        s3 = session.client('s3')

    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)

    return contents


def copy_file_to_bucket(from_bucket, from_bucket_key, to_bucket, to_bucket_key, from_database, to_database, table,
                        environment, hub_to_spoke):
    '''
    move a single file from a S3 instance to another S3 instance

    Examples:
        a file in a new bucket

    Args:
        from_bucket = 'my_hub_bucekt_name'
        from_bucket_key = 'Hub/Screenshot_1.png'    this does not require from_bucket
        to_bucket = 'my_spoke_bucket_name'
        to_bucket_key = 'Spoke/Screenshot_1.png'    this does not require to_bucket
        from_database = 'sampledb'
        to_database = 'spokedb'
        table = 'test_table'
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
    s32 = session2.client('s3')

    #s3 = session.client('s3')

    #try:
    #s3.meta.client.head_bucket(Bucket=from_bucket)
    #except ClientError:
        #print("The bucket for the file you are trying to copy either doesn't exist or you do not have access.")

    #s32 = session2.client('s3')

    #try:
        #s32.meta.client.head_bucket(Bucket=to_bucket)
    #except ClientError:
        #print("The bucket you are trying to copy to either doesn't exist or you do not have access.")

    client = session.client('athena')

    query = 'SHOW CREATE TABLE ' + from_database + '.' + table

    response_query_execution_id = run_athena_query(client, query, from_database)

    query = build_spoke_athena(client, response_query_execution_id, from_bucket, to_bucket, from_bucket_key,
                               to_bucket_key, from_database, to_database, table)

    client = session2.client('athena')

    response_query_execution_id = run_athena_query(client, query, to_database)

    source_response = s3.get_object(
        Bucket=from_bucket,
        Key=from_bucket_key
    )

    s32.upload_fileobj(
        source_response['Body'],
        to_bucket,
        to_bucket_key
    )

    delete_whole_folder(BUFFER_BUCKET, BUFFER_FOLDER)


def copy_folder_to_bucket(from_database, to_database, table, from_bucket, to_bucket, environment, hub_to_spoke):
    '''
    move a folder from an S3 instance to another S3 instance

    Examples:
        a folder in a new bucket

    Args:
        from_database = 'sampledb'
        to_database = 'spokedb'
        table = 'test_table'
        from_bucket = 'my_hub_bucekt_name'
        to_bucket = 'my_spoke_bucket_name'
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
    s32 = session2.client('s3')

    client = session.client('athena')

    query = 'SHOW CREATE TABLE ' + from_database + '.' + table

    if hub_to_spoke:
        key = get_kms_key('hub', from_bucket)
    else:
        key = get_kms_key(environment, from_bucket)

    response_query_execution_id = run_athena_query(client, query, from_database, from_bucket, key)
    query = build_spoke_athena(client, response_query_execution_id, from_database, to_database, table)
    client = session2.client('athena')

    print(query)

    loc_start = query.rfind('s3://' + from_bucket) + len(from_bucket) + 6
    print(loc_start)
    loc_end = query.rfind("'", loc_start)
    print(loc_end)
    if loc_end == -1:
        from_bucket_key = ""
    else:
        from_bucket_key = query[loc_start:loc_end]

    query = query.replace(from_bucket, to_bucket)
    print(query)

    res = session.resource('s3')
    if hub_to_spoke:
        key = get_kms_key(environment, to_bucket)
    else:
        key = get_kms_key('hub', to_bucket)

    first_line = query.splitlines()[1]
    if "." in first_line:
        buffer_location = "s3://" + to_bucket + "/querydata/"
        loc_start = first_line.rfind("EXISTS") + 7
        loc_end = first_line.rfind(".")
        database_name = first_line[loc_start:loc_end]
        create_database_query = "create database " + database_name
        print(create_database_query)
        response_query_execution_id = client.start_query_execution(
                QueryString=create_database_query,
                ResultConfiguration={
                    'OutputLocation': buffer_location,
                    'EncryptionConfiguration': {
                        'EncryptionOption': 'CSE_KMS',
                        'KmsKey': key
                    }
                },
                WorkGroup='primary'
        )


    response_query_execution_id = run_athena_query(client, query, to_database, to_bucket, key)

    old_bucket = res.Bucket(from_bucket)
    print(from_bucket_key)

    for obj in old_bucket.objects.filter(Prefix=from_bucket_key):

        print(obj)

        source_response = s3.get_object(
            Bucket=from_bucket,
            Key=obj.key
        )

        s32.upload_fileobj(
            source_response['Body'],
            to_bucket,
            obj.key
        )

    if hub_to_spoke:
        delete_whole_folder(from_bucket, BUFFER_FOLDER, 'hub')
        delete_whole_folder(to_bucket, BUFFER_FOLDER, environment)
    else:
        delete_whole_folder(to_bucket, BUFFER_FOLDER, 'hub')
        delete_whole_folder(from_bucket, BUFFER_FOLDER, environment)


def delete_whole_bucket(bucket, environment):
    '''
    delete a bucket

    Examples:
        bucket is deleted

    Args:
        bucket = 'bucket_name'
        environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.resource('s3')
    else:
        session = session_creator(environment)
        s3 = session.resource('s3')

    bucket = s3.Bucket(bucket)
    bucket.delete()

    return 'bucekt {} has been deleted'.format(bucket)


def delete_single_file(bucket, file_name, environment):
    '''
    delete a single file

    Examples:
        file is deleted

    Args:
        bucket = 'bucket_name'
        file_name = 'file_name'
        environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.client('s3')
    else:
        session = session_creator(environment)
        s3 = session.client('s3')

    s3.delete_object(Bucket=bucket, Key=file_name)

def delete_whole_folder(bucket, folder_name, environment):
    '''
    delete whole folder

    Examples:
        whole folder is deleted

    Args:
        bucket = 'bucket_name'
        folder_name = 'folder_name'
        environment = 'environment_name'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
        s3 = session.resource('s3')
    else:
        session = session_creator(environment)
        s3 = session.resource('s3')

    bucket = s3.Bucket(bucket)
    bucket.objects.filter(Prefix=folder_name).delete()



def build_spoke_athena(client, response_query_execution_id, from_database, to_database, table):
    '''
    check if athena query has completed

    Examples:
        athena query done

    Args:
        client: the boto3 client
        response_query_execution_id: id for the create table statment that would have run before this function
        from_database: the name of the source database
        to_database: the name fo the target database
        table: name of the table to copy

    '''

    query = ''
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
                query = athena_spoke_query_builder_assist(response_query_result, from_database, to_database, table)

                iterations = 0
        else:
            time.sleep(5)

    return query


def athena_spoke_query_builder_assist(response_query_result, from_database, to_database, table):
    '''
        helper function to assist in the building of the create query for the target table

        Args:
            response_query_result: the show create table output to be altered for the target table's create statement
            from_database: the name of the source database
            to_database: the name fo the target database
            table: name of the table to copy

        Returns:
            the query string that will be needed to create the athena table in the spoke
    '''

    query = ''
    start = False

    if len(response_query_result['ResultSet']['Rows']) > 1:
        for row in response_query_result['ResultSet']['Rows']:
            value = [obj['VarCharValue'] for obj in row['Data']]
            text = value[0]
            if "CREATE EXTERNAL TABLE" in text:
                text = text[:22] + "IF NOT EXISTS " + text[22:]
            if "ROW FORMAT DELIMITED" in text:
                start = False
            if "WITH SERDEPROPERTIES" in text:
                start = True
            if "STORED AS INPUTFORMAT" in text:
                start = True
            if "OUTPUTFORMAT" in text:
                start = True
            if "LOCATION" in text:
                start = False
            if "TBLPROPERTIES" in text:
                start = True
            if start:
                continue

            query = query + '\n' + text

        query = query.replace("`", "")
        query = query.replace(from_database + '.' + table, to_database + '.' + table)

        return query

    else:
        return query
