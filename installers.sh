apt update

# Base dependencies
apt install -y \
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

# Setup .local/bin
mkdir -p ~/.local/bin

# Install GDAL
apt install -y libproj-dev gdal-bin

# Install Imagemagick
apt install -y imagemagick

# Install nconvert
curl -L -o nconvert.tgz 'https://download.xnview.com/NConvert-linux64.tgz'
tar zxvf nconvert.tgz
mv NConvert/* ~/.local/bin
rm -rf nconvert.tgz NConvert/

# Install pdftoppm
apt install poppler-utils

# Install tiffcp
apt install libtiff-tools

# Install vipps
apt install -y libvips-tools

# Install LibreOffice
curl -o libreoffice.tar.gz 'https://downloadarchive.documentfoundation.org/libreoffice/old/24.8.7.2/deb/x86_64/LibreOffice_24.8.7.2_Linux_x86-64_deb.tar.gz'
tar zxvf libreoffice.tar.gz
dpkg -i LibreOffice_24.8.7.2_Linux_x86-64_deb/DEBS/*.deb
ln -s /opt/libreoffice24.8/program/soffice /usr/bin/libreoffice
rm -rf libreoffice LibreOffice_24.8.7.2_Linux_x86-64_deb/

# Install GhostScript
apt install -y ghostscript

# Install ffmpeg
apt install -y ffmpeg

# Install xmlstarlet
apt install -y xmlstarlet

# Install chrome
apt install -y chromium
