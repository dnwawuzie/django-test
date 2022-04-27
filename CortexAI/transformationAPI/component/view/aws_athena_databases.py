import json
from django.http import JsonResponse
from transformationAPI.component.functions.resources.aws_athena import display_databases
from transformationAPI.component.model.serializers import DatabaseTableSerializer
from transformationAPI.component.model.models import DatabaseTable
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
import coreapi
import coreschema
from rest_framework import schemas


class Databases(GenericAPIView):
    serializer_class = DatabaseTableSerializer

    def get(self, request):
        """
       list all existing databases in an environment

       Parameter Name:
       - **environment**,
       The name of the environment to get the list from
       ---
       tags:
       - GET method
       parameters:
       - in: body
       name:
       required: true
       description: data for loading in JSON format
       type: string
       responses:
       201:
       description: data properly loaded to DB
       schema:
           id:
           properties:
           message:
               type:
               default:
       204:
       description: Data not supported
       schema:
           id: Error
           properties:
           error message:
               type: string
               default: Error
       400:
       description: Invalid load JSON
       schema:
           id: Error
           properties:
           error message:
               type: string
               default: Error
       500:
       description: Internal server error
       schema:
           id: Error
           properties:
           error message:
               type: string
               default: Error
        """

        return Response({"message": "Hello, world!"})
