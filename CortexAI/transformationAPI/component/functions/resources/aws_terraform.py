from python_terraform import *

#  cli equivalnce
# terraform apply -var='a=b' -var='c=d' -refresh=false -no-color -target='aws_resource.xxxx'

def create_aws_resources(S3_bucket_name):
    

    #create an terraform instance
    tf=Terraform()

    #pointing terraform working directory 
    #assigning variable to terraform
    tf = Terraform(working_dir=r'reference_data\resources_templates', variables={'S3_bucket_name':S3_bucket_name})

    #returns terraform.apply back
    return_code, stdout, stderr = tf.apply(capture_output=False)

    #actually apply terraform change
    tf.apply(no_color=IsFlagged, refresh=False )
    
   
def delete_aws_resources(S3_bucket_name):

    #create an terraform instance
    tf=Terraform()

    #pointing terraform working directory 
    #assigning variable to terraform
    tf = Terraform(working_dir=r'reference_data\resources_templates', variables={'S3_bucket_name':S3_bucket_name})

    #returns terraform.apply back
    return_code, stdout, stderr = tf.destroy(capture_output=False)

    #actually apply terraform change
    tf.destroy(no_color=IsFlagged, refresh=False )




