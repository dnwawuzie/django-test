import boto3
import os
from transformationAPI.component.functions.resources.aws_session import session_creator, session_finder


def create_repo(name, path, environment):

    '''

    create a codecommit repository with a given name as long as
    that name is not already used

    examples:
        codecommit repository

    Args:
        name = 'my_desired_codecommit_name'
        path = 'path_to_the_repo_im_cloning'
        environment = 'name_of_environment'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
    else:
        session = session_creator(environment)

    client = session.client('codecommit')

    try:
        response = client.create_repository(
            repositoryName=name,
            repositoryDescription='Copy of: ' + path
        )

        return (response, True)
    except:
        return ('The repository name you provided either already exists or you do not have permissions to create one.', False)



def clone_repo(path, hub_to_spoke):

    '''
    clone an existing codecommit repository

    examples:
        a cloned repository stored locally

    Args:
        path = 'https://git-codecommit.ca-central-1.amazonaws.com/v1/repos/dhub-coderepo/'
        hub_to_spoke = True or False - Is this repo going from hub to spoke or spoke to hub

    '''

    if hub_to_spoke:
        code_location = path.rsplit('/', 1)[-1]
        command = 'git clone ' + path + ' ' + code_location
        os.system(command)

    else:
        os.system("git config --global credential.helper '!aws --profile spoke codecommit credential-helper $@'")
        code_location = path.rsplit('/', 1)[-1]
        command = 'git clone ' + path + ' ' + code_location
        os.system(command)


def push_clone(response, path, hub_to_spoke):

    '''
    push cloned codecommit repository to the newly created spoke repository

    examples:
        pushed repository in codecommit

    Args:
        response = an internal json that is passed from the create phase
        path = 'https://git-codecommit.ca-central-1.amazonaws.com/v1/repos/dhub-coderepo/'
        hub_to_spoke = True or False - Is this repo going from hub to spoke or spoke to hub

    '''

    code_location = path.rsplit('/', 1)[-1]
    location = response['repositoryMetadata']['cloneUrlHttp']
    print('Sending here: ' + location)
    cur = os.getcwd()
    os.chdir(code_location)

    if hub_to_spoke:

        os.system("git config --global credential.helper '!aws --profile spoke codecommit credential-helper $@'")

        os.system('git remote rename origin backup')
        os.system('git remote add origin ' + location)
        os.system('git remote -v')
        os.system('git push origin')
        os.chdir(cur)

        os.system("git config --global credential.helper '!aws codecommit credential-helper $@'")

    else:

        os.system("git config --global credential.helper '!aws codecommit credential-helper $@'")
        os.system('git remote rename origin backup')
        os.system('git remote add origin ' + location)
        os.system('git remote -v')
        os.system('git push origin')
        os.chdir(cur)

    os.system("mv -f ~/.aws/backup-credentials ~/.aws/credentials")
    os.system("rm -rf " + code_location)


def delete_repo(name, environment):

    '''
    delete a codecommit repository

    Args:
        name = 'my__codecommit_repository_name'
        environment = 'name_of_environment'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')

    else:
        session = session_creator(environment)

    client = session.client('codecommit')
    response = client.delete_repository(
        repositoryName=name
    )

    return(response)

def link_sagemaker(name, response, environment):

    '''
    link the newly created codecommit repository to a sagemaker notebook instance

    Args:
        name = 'my_codecommit_repository_name'
        path = an internal json that is passed from the create phase
        environment = 'name_of_environment'

    '''

    if environment == "hub":
        session = boto3.session.Session(region_name='ca-central-1')
    else:
        session = session_creator(environment)

    client = session.client('sagemaker')

    try:
        client.stop_notebook_instance(NotebookInstanceName=name)
    except:
        print("Notebook already stopped")

    location = response['repositoryMetadata']['cloneUrlHttp']
    repo_name = response['repositoryMetadata']['repositoryName']

    res = client.create_code_repository(CodeRepositoryName=repo_name, GitConfig={'RepositoryUrl':location})
    repo = res['CodeRepositoryArn']

    if "/" in repo:
        default_repo = repo.rsplit('/', 1)[-1]
    else:
        default_repo = repo

    response = client.update_notebook_instance(
        NotebookInstanceName=name,
        DefaultCodeRepository=default_repo
    )

    return response


def build_credentials(environment):
    '''
        add the spoke profile to the AWS credentials

        Args:
            environment = 'name_of_environment'

    '''

    role_arn = session_finder(environment)
    os.system("cp ~/.aws/credentials ~/.aws/backup-credentials")
    os.system('echo "" >> ~/.aws/credentials')
    os.system('echo "[spoke]" >> ~/.aws/credentials')
    os.system('echo "role_arn = ' + role_arn + '" >> ~/.aws/credentials')
    os.system('echo "credential_source = Ec2InstanceMetadata" >> ~/.aws/credentials')
