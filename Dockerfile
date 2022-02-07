FROM debian:bullseye-slim

ENV DIE_DIR /app/service

WORKDIR $DIE_DIR

RUN apt update -y --quiet
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt -y --quiet install tzdata
RUN apt install -y --quiet libmagic-dev libboost-all-dev git wget tar libglib2.0-0 build-essential \
    qtbase5-dev qtscript5-dev qttools5-dev-tools && \
    wget https://github.com/horsicq/DIE-engine/releases/download/3.04/die_3.04_portable_Ubuntu_20.04_amd64.tar.gz && \
    tar -xzf die_3.04_portable_Ubuntu_20.04_amd64.tar.gz 

RUN wget http://security.ubuntu.com/ubuntu/pool/main/i/icu/libicu66_66.1-2ubuntu2.1_amd64.deb
RUN apt install ./libicu66_66.1-2ubuntu2.1_amd64.deb

RUN apt install -y python3-dev python3-pip git

# db update
RUN rm -rf ./die_linux_portable/base/db
RUN git clone --single-branch -- https://github.com/horsicq/Detect-It-Easy.git ./Detect-It-Easy
RUN cp -r ./Detect-It-Easy/db ./die_linux_portable/base/db

ENV DIEC_DIR $DIE_DIR/die_linux_portable/base/
ENV LD_LIBRARY_PATH="$DIEC_DIR"
RUN echo 'export PATH=$PATH:$DIEC_DIR' >> ~/.bashrc
RUN exec bash 

RUN git clone --single-branch -- https://github.com/raw-data/karton-die-classifier.git ./karton-die-classifier
RUN pip install ./karton-die-classifier/.
CMD exec env PATH=$PATH:$DIEC_DIR karton-die-classifier
