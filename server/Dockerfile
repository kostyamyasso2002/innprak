FROM python:latest

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN rm requirements.txt

RUN wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
RUN mkdir server && cd server && mkdir model && cd ..
RUN mv vosk-model-small-ru-0.22.zip /server/model/vosk-model-small-ru-0.22.zip && cd /server/model && unzip vosk-model-small-ru-0.22.zip && cd ../..

ADD simple_server.py /server/
ADD speech_recogniser.py /server/

WORKDIR /server/
