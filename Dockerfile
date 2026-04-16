FROM python:3.13-trixie AS base
ARG DEBIAN_FRONTEND=noninteractive

ENV PATH="/root/.local/bin:$PATH"

# Install uv
ENV UV_NO_MODIFY_PATH=1
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Run installer script
WORKDIR /root
COPY installers.sh installers.sh
RUN sh installers.sh
RUN rm installers.sh


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