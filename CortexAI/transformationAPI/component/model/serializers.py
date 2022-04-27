from rest_framework.serializers import (
    CharField,
    IntegerField,
    ListField,
    HyperlinkedModelSerializer,
    ModelSerializer,
    SerializerMethodField,
    Serializer,
    DateTimeField
)

from transformationAPI.component.model.models import DatabaseTable, CodePointToPoint, DatabasePointToPoint, AWSFile, \
    S3PointToPoint, TableauPointToPoint, Environment


class DatabaseTableSerializer(ModelSerializer):
    # table_name = CharField(required=False)
    # database_name = CharField(required=False)
    # environment = CharField(required=False)

    class Meta:
        model = DatabaseTable
        fields = ('table_name', 'database_name', 'environment')


class CodePointToPointSerializer(ModelSerializer):
    class Meta:
        model = CodePointToPoint
        fields = '__all__'


class DBHubToSpokeSerializer(ModelSerializer):
    class Meta:
        model = DatabasePointToPoint
        fields = '__all__'


class DatabasePointToPointSerializer(ModelSerializer):
    class Meta:
        model = DatabasePointToPoint
        fields = '__all__'


class AWSFileSerializer(ModelSerializer):
    class Meta:
        model = AWSFile
        fields = '__all__'


class S3PointToPointSerializer(ModelSerializer):
    class Meta:
        model = S3PointToPoint
        fields = '__all__'


class TableauPointToPointSerializer(ModelSerializer):
    class Meta:
        model = TableauPointToPoint
        fields = "__all__"


class EnvironmentSerializer(ModelSerializer):
    class Meta:
        model = Environment
        fields = "__all__"
