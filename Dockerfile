# set base image
FROM python:3.9.11-alpine

# set environments variables
ENV PATH="/home/cortexai-test/.local/bin:${PATH}"


# copy the dependencies file to the working directory
COPY requirements.txt .
RUN apk update && apk upgrade \
    && apk add --no-cache --virtual .build-deps gcc build-base linux-headers \
    ca-certificates python3-dev libffi-dev libressl-dev git
# install dependencies
RUN pip install -r requirements.txt

# set the working directory in the container
RUN mkdir /cortexai
COPY ./cortexai /cortexai
WORKDIR /cortexai

RUN adduser -D cortexai-test
USER cortexai-test

# run-time configuration
EXPOSE 8000

ENTRYPOINT ["/bin/bash"]