FROM ubuntu:20.04
WORKDIR /bot
RUN chmod -R 777 /bot
RUN apt-get -yqq update
ENV TZ Asia/Kolkata
ENV DEBIAN_FRONTEND noninteractive

RUN apt -yqq install python3 python3-pip mediainfo mkvtoolnix wget

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN chmod 777 run.sh
RUN useradd -ms /bin/bash  myuser
USER myuser
RUN wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1XX0AF-TmNi8R7y4O5U6I_C4f6kKtkcm9' -O /usr/bin/ffmpeg 
RUN chmod 777 /usr/bin/ffmpeg
CMD ./run.sh
