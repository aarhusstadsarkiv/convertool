FROM ubuntu:24.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt-get update && apt-get install -y \
    vim \
    curl \
    wget \
    git \
    cmake \
    apt-transport-https \
    software-properties-common \
    ca-certificates \
    libc6-i386 \
    libc6-x32 \
    libxtst6
RUN rm -rf /var/lib/apt/lists/*

# Install uv
ENV UV_NO_MODIFY_PATH=1
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install GDAL
RUN apt-get update && apt-get install -y libproj-dev gdal-bin

# Install Imagemagick
RUN apt-get update && apt-get install -y imagemagick
COPY config/imagemagick_policy.xml /etc/ImageMagick-6/policy.xml

# Install vipps
RUN apt-get update && apt-get install -y libvips-tools

# Install LibreOffice
RUN apt-get update && apt-get install -y libreoffice

# Install GhostScript
RUN apt-get update && apt-get install -y ghostscript

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install xmlstarlet
RUN apt-get update && apt-get install -y xmlstarlet

# Install chrome
WORKDIR /root
RUN apt-get update && apt-get install -y chromium


FROM base AS prod
# Install convertool
WORKDIR /root/convertool
COPY . .
RUN uv sync
RUN uv tool install .

WORKDIR /root
CMD ["bash"]


FROM prod AS test
# Install go and Siegfried
WORKDIR /root
RUN curl -L https://go.dev/dl/go1.23.1.linux-amd64.tar.gz -o go.tar.gz
RUN tar -C /usr/local -xzf go.tar.gz
ENV GOPATH="/usr/local/go"
ENV PATH="$GOPATH/bin:$PATH"
RUN go install github.com/richardlehane/siegfried/cmd/sf@latest
ENV SIEGFRIED_PATH="$GOPATH/bin/sf"
ENV SIEGFRIED_HOME="/root/.sf"
RUN sf -home "$SIEGFRIED_HOME" -update

# Install extra and dev dependencies
WORKDIR /root/convertool
RUN uv sync --all-extras --dev
CMD ["bash"]