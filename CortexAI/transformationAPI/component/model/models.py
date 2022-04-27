from django.db import models

# Create your models here.


class DatabaseTable(models.Model):
    table_name = models.CharField(max_length=999)
    database_name = models.CharField(max_length=999)
    environment = models.CharField(max_length=999)

    class Meta:
        ordering = ('table_name',)

    def __str__(self):
        return self.environment

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        table_name = self.table_name
        database_name = self.database_name
        environment = self.environment
        super(DatabaseTable, self).save(*args, **kwargs)


class CodePointToPoint(models.Model):
    target_repo_name = models.CharField(max_length=999)
    source_repo_path = models.CharField(max_length=999)
    sagemaker_name = models.CharField(max_length=999)
    environment = models.CharField(max_length=999)


class DatabasePointToPoint(models.Model):
    from_bucket_name = models.CharField(max_length=999)
    to_bucket_name = models.CharField(max_length=999)
    from_database = models.CharField(max_length=999)
    to_database = models.CharField(max_length=999)
    environment = models.CharField(max_length=999)


class AWSFile(models.Model):
    S3_bucket_name = models.CharField(max_length=999)
    environment = models.CharField(max_length=999)
    file_path = models.CharField(max_length=999)
    file_name = models.CharField(max_length=999)


class S3PointToPoint(models.Model):
    from_bucket_name = models.CharField(max_length=999)
    to_bucket_name = models.CharField(max_length=999)
    from_database = models.CharField(max_length=999)
    to_database = models.CharField(max_length=999)
    table = models.CharField(max_length=999)
    file_path = models.CharField(max_length=999)
    environment = models.CharField(max_length=999)


class TableauPointToPoint(models.Model):
    from_bucket_name = models.CharField(max_length=999)
    from_bucket_name_filepath = models.CharField(max_length=999)
    to_bucket_name = models.CharField(max_length=999)
    to_bucket_name_filepath = models.CharField(max_length=999)
    tableau_server = models.CharField(max_length=999)
    tableau_username = models.CharField(max_length=999)
    tableau_password = models.CharField(max_length=999)
    tableau_site = models.CharField(max_length=999)
    environment = models.CharField(max_length=999)


class Environment(models.Model):
    environment = models.CharField(max_length=999)
    state = models.CharField(max_length=999)
    parameter_name = models.CharField(max_length=999)
    parameter_value = models.CharField(max_length=999)
    environment_parameter = models.QuerySet
