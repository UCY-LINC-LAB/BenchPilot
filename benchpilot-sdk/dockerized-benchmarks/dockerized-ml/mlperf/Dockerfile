FROM python:3.6-bullseye

ENV CMAKE_ARGS="-DONNX_USE_PROTOBUF_SHARED_LIBS=ON" DATA_DIR=/mlperf/data MODEL_DIR=/mlperf/model 

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      build-essential \
      software-properties-common \
      ca-certificates \
      wget \
      curl \
      libopenblas-dev \
      libblas-dev \
      m4 \
      cmake \
      python3-pip \
      python3-yaml \
      python3-setuptools \
      libavutil-dev \
      libavcodec-dev \
      libavformat-dev \
      libswscale-dev \
      libhdf5-dev \
      protobuf-compiler \
      ffmpeg libsm6 libxext6 \
      tini; \
      python3 -m pip install --upgrade pip;
COPY . /benchmark
WORKDIR /benchmark
ARG TARGETARCH
RUN pip3 install -r ./requirements.txt && \
    if [ "$TARGETARCH" = "amd64" ]; then \
	pip3 install tensorflow; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
	pip3 install tensorflow-aarch64; \
    else \
        echo "Unsupported Architecture"; \
        exit 1; \
    fi; \
    cd /benchmark/inference/loadgen && \
    pip3 install pybind11 && \
    CFLAGS="-std=c++14" python3 setup.py install

ENTRYPOINT ["/usr/bin/tini", "--", "/benchmark/entrypoint.sh"]
