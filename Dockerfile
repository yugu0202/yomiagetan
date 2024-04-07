FROM python:3
ENV VOICEVOX_CORE_VERSION 0.15.3
ENV ONNXRUNTIME_VERSION 1.13.1

RUN apt update
RUN apt -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN apt install -y vim less ffmpeg
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN pip install discord.py[voice]

RUN wget https://github.com/VOICEVOX/voicevox_core/releases/download/${VOICEVOX_CORE_VERSION}/voicevox_core-${VOICEVOX_CORE_VERSION}+cpu-cp38-abi3-linux_x86_64.whl
RUN pip install voicevox_core-${VOICEVOX_CORE_VERSION}+cpu-cp38-abi3-linux_x86_64.whl

RUN wget https://github.com/microsoft/onnxruntime/releases/download/v${ONNXRUNTIME_VERSION}/onnxruntime-linux-x64-${ONNXRUNTIME_VERSION}.tgz
RUN tar -zxvf onnxruntime-linux-x64-${ONNXRUNTIME_VERSION}.tgz

WORKDIR /root

RUN cp /onnxruntime-linux-x64-${ONNXRUNTIME_VERSION}/lib/libonnxruntime.so.${ONNXRUNTIME_VERSION} ./libonnxruntime.so.${ONNXRUNTIME_VERSION}

RUN wget https://jaist.dl.sourceforge.net/project/open-jtalk/Dictionary/open_jtalk_dic-1.11/open_jtalk_dic_utf_8-1.11.tar.gz
RUN tar -zxvf open_jtalk_dic_utf_8-1.11.tar.gz

COPY ./app/* ./

CMD ["python", "main.py"]