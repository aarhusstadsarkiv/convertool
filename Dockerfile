FROM git.openaws.dk/aarhusstadsarkiv/convertool-base:latest AS base
WORKDIR /root/convertool
COPY . .

FROM base AS prod
RUN pipx install .

FROM base AS test
# Install veraPDF
WORKDIR /root
COPY config/verapdf-autoinstall.xml .
RUN apt-get update && apt-get install -y default-jre
RUN curl -L https://software.verapdf.org/releases/verapdf-installer.zip -o /root/verapdf-installer.zip
RUN unzip /root/verapdf-installer.zip
RUN chmod a+x /root/verapdf-*/verapdf-install
RUN /root/verapdf-*/verapdf-install /root/verapdf-autoinstall.xml
ENV PATH="/root/.local/verapdf:$PATH"
RUN rm -rf /root/verapdf-*

# Install poetry
WORKDIR /root/convertool
RUN pip3 install poetry
RUN poetry install