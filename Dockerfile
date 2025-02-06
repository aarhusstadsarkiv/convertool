FROM python:3.13.1-bookworm AS base
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
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install GDAL
RUN apt-get update && apt-get install -y libproj-dev gdal-bin

# Install Imagemagick
RUN apt-get update && apt-get install -y imagemagick
COPY config/imagemagick_policy.xml /etc/ImageMagick-6/policy.xml

# Install LibreOffice
RUN apt-get update && apt-get install -y libreoffice

# Install GhostScript
RUN apt-get update && apt-get install -y ghostscript

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Install chrome
WORKDIR /root
RUN curl -L https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /root/google-chrome-stable_current_amd64.deb
RUN apt-get update && apt-get install -y /root/google-chrome-stable_current_amd64.deb
RUN ln -s $(which google-chrome-stable) /usr/bin/chrome
RUN rm google-chrome-stable_current_amd64.deb


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