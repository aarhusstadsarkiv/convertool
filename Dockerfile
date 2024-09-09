FROM git.openaws.dk/aarhusstadsarkiv/convertool-base:latest AS base
WORKDIR /root/convertool
COPY . .

FROM base AS prod
RUN pipx install .

FROM base AS test
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

# Install vim
RUN apt-get update && apt-get install -y vim

# Install poetry
WORKDIR /root/convertool
RUN pip3 install poetry
RUN poetry install