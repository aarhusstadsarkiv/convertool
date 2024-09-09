FROM git.openaws.dk/aarhusstadsarkiv/convertool-base:latest AS base
WORKDIR /root/convertool
COPY . .

FROM base AS prod
RUN pipx install .

FROM base AS test
# Install go and Siegfried
ENV GOPATH="/root/.go"
RUN apt-get update && apt-get install -y go
RUN go install github.com/richardlehane/siegfried/cmd/sf@latest
ENV PATH="$GOPATH/bin:$PATH"
ENV SIEGFRIED_PATH="$GOPATH/bin/sf"
ENV SIEGFRIED_HOME="/root/.sf"
RUN sf -home "$SIEGFRIED_HOME" -update

# Install vim
RUN apt-get update && apt-get install -y vim

# Install poetry
WORKDIR /root/convertool
RUN pip3 install poetry
RUN poetry install