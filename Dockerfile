FROM python:3.11-slim 

ADD requirements.txt requirements.txt
RUN apt-get update -y --fix-missing && apt-get install -y python3-pip python3-dev \
    && python3 -m pip install --upgrade pip \
    && pip3 install -r requirements.txt

WORKDIR /home

COPY ./app /home/app/

ENTRYPOINT ["python3", "/home/app/vk_test.py"]
