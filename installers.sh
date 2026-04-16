sudo apt update

# Base dependencies
sudo apt install -y \
    vim \
    curl \
    wget \
    git \
    cmake \
    sudo apt-transport-https \
    ca-certificates \
    libc6-i386 \
    libc6-x32 \
    libxtst6

# Setup .local/bin
mkdir -p ~/.local/bin

# Install GDAL
sudo apt install -y libproj-dev gdal-bin

# Install Imagemagick
sudo apt install -y imagemagick

# Install nconvert
curl -L -o nconvert.tgz 'https://download.xnview.com/NConvert-linux64.tgz'
tar zxvf nconvert.tgz
mv NConvert/* ~/.local/bin
rm -rf nconvert.tgz NConvert/

# Install vipps
sudo apt install -y libvips-tools

# Install LibreOffice
curl -o libreoffice.tar.gz 'https://downloadarchive.documentfoundation.org/libreoffice/old/24.8.7.2/deb/x86_64/LibreOffice_24.8.7.2_Linux_x86-64_deb.tar.gz'
tar zxvf libreoffice.tar.gz
dpkg -i LibreOffice_24.8.7.2_Linux_x86-64_deb/DEBS/*.deb
sudo ln -s /opt/libreoffice24.8/program/soffice /usr/bin/libreoffice
rm -rf libreoffice LibreOffice_24.8.7.2_Linux_x86-64_deb/

# Install GhostScript
sudo apt install -y ghostscript

# Install ffmpeg
sudo apt install -y ffmpeg

# Install xmlstarlet
sudo apt install -y xmlstarlet

# Install chrome
sudo apt install -y chromium
