FROM git.openaws.dk/aarhusstadsarkiv/convertool-base:latest AS base
WORKDIR /root/convertool
COPY . .

FROM base AS prod
RUN pipx install .

FROM base AS test

# Install vim
RUN apt-get update && apt-get install -y vim

# Install poetry
WORKDIR /root/convertool
RUN pip3 install poetry
RUN poetry install