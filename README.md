# DjangoTemplate
this code base is a Django based project template. 

general info

this is a REST service based web application. features listed below have been integrated i nthis code base.

        1. Add API version control
        2. Add example component with suggested code structure
        3. Add python decouple feature with .env file
        4. Add log feature with file rotation configuration and component specific handler
        5. Add example test cases for example call
        6. Add rest_framework lib for REST API development
        7. integrated DB operation example with sqlite3 DB

instructions to run this project
1. clone or copy code base in a folder
2. in root folder (where you can see manage.py) execure command below to make sure code base is in a good condition

        > python3 manage.py check
        output: System check identified no issues (0 silenced).
3. if everything is ok then execute commands below to initiate DB. after this step you should have DB models created in your DB

        > python manage.py makemigrations webapp (this one can be ignored since we already made migration file)
        > python3 manage.py migrate webapp
4. run unit test. there are two examples for different way to run unit test

        > python3 manage.py test (this is the standard way to run unit test as normal)
        > python3 manage.py test --testrunner=webapp.component.test.no_db_test_runner.NoDbTestRunner (this is an example to run unit test without recreate DB)
        typical output
        Creating test database for alias 'default'...
        System check identified no issues (0 silenced).
        INFO {'message': '"Hello world with GET!"'}
        .INFO {'message': '"Hello world with POST!"'}
        .
        ----------------------------------------------------------------------
        Ran 2 tests in 0.017s
        OK
        Destroying test database for alias 'default'...
5. setup log folder. 

        log folder is specified in webapp/settings.py (example: 'filename': '../log/template.log')
        create log folder 'log' as sibling to templateProject folder if you didn't change exist folder path
6. start up application. 

        run command below to start up application. you can specify different ports based on your ENV needs
        > python3 manage.py runserver 8080 (keep in mind that this is only for your local testing basically, not for server side use)
7. how to access APIs from this application

        first install postman as API client to access endpoints listed below
        http://127.0.0.1:8080/api/v1/component/ (this API is for demo how to create an API with annotation and without define a class)
            method: GET/POST
            content type: application/json
        http://127.0.0.1:8080/api/v1/component/class-view (this API is for demo how rto create an API with class)
            method: GET/POST
            content type: application/json
        http://127.0.0.1:8080/api/v1/component/data-load-view (this API is for demo how to make a DB operation as a batch load to DB)
            method: POST
            content type: application/json
            body: [{"resource": "test resource", "description": "test description", "cve_id": "testID12"},{"resource": "test resource", "description": "test description", "cve_id": "testID13"}]
        http://127.0.0.1:8080/api/v1/component/test-model-list-view?cve_id=testID4 (this API is for demo how to retrieve data from DB)
            method: GET
            content type: application/json
            query parameter: cve_id (example value: testID4)
            
Folder structure

        templateProject                 -- this is the root folder of this code base
            db.sqlite3                  -- example DB file
            manage.py                   -- project local management entrance, refernce info above about what command can be run through it. there are more commands than listed
            .env                        -- this is the file defined by python decouple lib which support to decouple env based parameters from source code (settings.py)
            webapp
                __init__.py
                asgi.py                 -- server side service entrance for ASGI
                settings.py             -- this is the over all setting file for Django project. it's integrated with python decouple which involves .env file  
                urls.py                 -- this is the root URLs configuration for whole application. each component will have it's own url.py for specific API url configuration
                wsgi.py                 -- this is file to support WSGI module with Apache to run on server side
                migrations              -- this is the folder which contain application level migration code whatever is needed. 
                    __init__.py
                    0001_initial.py     -- this is auto generated DB initial migration code. please refernece the makemigration command above.
                component               -- this is the component for a group of APIs endpoint and service behind it.
                    __init__.py
                    admin.py            -- this is for Django admin site which we don't use
                    apps.py             -- this is for component configuration. please reference document to see what you can do here: https://docs.djangoproject.com/en/3.2/ref/applications/#application-configuration
                    migrations
                    model               -- this folder is for all models for data persistance. you can create sub packages if you have more models in structure
                        __init__.py
                        models.py       -- this file is for models definition
                        serializers.py  -- this file is serializer for each model
                    repository          -- this folder is for code to operate on models.
                        __init__.py
                        test_model_repo.py -- this file is for operation to each model like create/update/batch load
                    test -- this file is for unit test
                        __init__.py
                        no_db_test_runner.py -- this file is for running test cased with out create/cleanup DB. please reference command above
                        test_views.py   -- this file is for test cases.
                    url                 -- this folder is for component level APIs' URL configuration
                        __init__.py
                        urls.py         -- this is the file to configure all APIs' URL for it's component
                    view                -- this folder is for API endpoints for this component
                        __init__.py
                        views.py        -- this is the file contains all APIs' endpoints code.
