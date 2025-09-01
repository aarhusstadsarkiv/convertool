FROM python:3.13-trixie AS base
ARG DEBIAN_FRONTEND=noninteractive

# Install base dependencies
RUN apt update && apt install -y \
    vim \
    curl \
    wget \
    git \
    cmake \
    apt-transport-https \
    ca-certificates \
    libc6-i386 \
    libc6-x32 \
    libxtst6

# Install uv
ENV UV_NO_MODIFY_PATH=1
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install GDAL
RUN apt update && apt install -y libproj-dev gdal-bin

# Install Imagemagick
RUN apt update && apt install -y imagemagick
COPY config/imagemagick_policy.xml /etc/ImageMagick-6/policy.xml

# Install vipps
RUN apt update && apt install -y libvips-tools

# Install LibreOffice
RUN curl -o libreoffice.tar.gz 'https://downloadarchive.documentfoundation.org/libreoffice/old/24.8.7.2/deb/x86_64/LibreOffice_24.8.7.2_Linux_x86-64_deb.tar.gz'
RUN tar zxvf libreoffice.tar.gz
RUN dpkg -i LibreOffice_24.8.7.2_Linux_x86-64_deb/DEBS/*.deb
RUN ln -s /opt/libreoffice24.8/program/soffice /usr/bin/libreoffice

# Install GhostScript
RUN apt update && apt install -y ghostscript

# Install ffmpeg
RUN apt update && apt install -y ffmpeg

# Install xmlstarlet
RUN apt update && apt install -y xmlstarlet

# Install chrome
WORKDIR /root
RUN apt update && apt install -y chromium


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