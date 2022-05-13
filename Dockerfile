# set base image
FROM python:3.9.11-alpine

# WORKDIR /cortexai

# set environments variables
ENV PATH="/home/cortexai/.local/bin:${PATH}"

RUN pip install --upgrade pip

RUN adduser -D django-test
USER django-test

RUN pip install --upgrade cython

USER root

RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev

USER django-test

# copy the dependencies file to the working directory
COPY requirements.txt .

# RUN apk update && apk upgrade \
#     && apk add --no-cache --virtual .build-deps gcc build-base linux-headers \
#     ca-certificates python3-dev libffi-dev libressl-dev git


# install dependencies
RUN pip install -r requirements.txt

# set the working directory in the container
COPY . .
#COPY . /home/cortexai
# COPY main.py ./
# WORKDIR /cortexai

# run-time configuration
EXPOSE 8000

CMD [ "python", "manage.py", "runserver" ]