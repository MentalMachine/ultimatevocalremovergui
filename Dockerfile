FROM nvcr.io/nvidia/cuda:12.3.1-runtime-ubuntu22.04
CMD nvidia-smi
# TODO - Use lighter one... if can
#FROM python:3.9.16

# If using other image, need to: install pyenv
# install specific python

RUN apt-get update
# Needed to then be able to add repos
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
# Disable interactive prompts when installing python
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y ffmpeg \
  libsndfile1 \
  python3.9 \
  python3-pip \
  python3-tk

WORKDIR /opt/ultimateVocalRemoverCli
COPY . .

ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/opt/ultimateVocalRemoverCli/cli.py"]