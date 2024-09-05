WORKDIR /root/convertool
COPY . .

FROM convertool-base:latest AS test
RUN cp config/imagemagick_policy.xml /etc/ImageMagick-6/policy.xml
RUN pip3 install poetry
RUN poetry install
CMD ["bash"]

FROM git.openaws.dk/aarhusstadsarkiv/convertool-base:latest AS prod
RUN cp config/imagemagick_policy.xml /etc/ImageMagick-6/policy.xml
RUN pipx install .
CMD ["bash"]