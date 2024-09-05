FROM git.openaws.dk/aarhusstadsarkiv/convertool-base:latest AS base
WORKDIR /root/convertool
COPY . .
RUN cp config/imagemagick_policy.xml /etc/ImageMagick-6/policy.xml

FROM base AS test
RUN pip3 install poetry
RUN poetry install
CMD ["bash"]

FROM base AS prod
RUN pipx install .
CMD ["bash"]