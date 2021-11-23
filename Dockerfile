# Docker image for Jenkins build

FROM ubuntu:latest

# WORKDIR /space

#Install WGET, bz2, vim 
RUN apt-get -y update && \
	apt-get -y full-upgrade && \
	apt-get -y clean all
