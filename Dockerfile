# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER bvcelari@gmail.com

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y git curl wget net-tools vim

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

# Install GIP system requirements
RUN apt-get install -y libmysqlclient-dev

RUN apt-get install -y libpq-dev python-dev

# Clone app
RUN git clone https://github.com/bvcelari/GIP

# Get pip to download and install requirements:
RUN pip install -r /GIP/requirements.txt


# Expose ports, check if many aare fine
EXPOSE 8000 5432

# Set the default directory where CMD will execute
WORKDIR /GIP

# There should be a script to create the DB and import carga_db 
