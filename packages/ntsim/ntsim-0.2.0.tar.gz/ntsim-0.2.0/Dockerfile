FROM git.jinr.ru:5005/zavyalov_github/docker2ntsim:latest

LABEL maintainer="zav.postline@yandex.ru"

WORKDIR /workdir

COPY . /software/ntsim

COPY /docker/requirements.txt /workdir
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV LHAPDF_ROOT_DIR=/software/LHAPDF-6.5.3-install
RUN pip install nudisxs==1.1.2
RUN pip install nupropagator
RUN pip install --upgrade tbb

RUN rm -rf /workdir

COPY docker/run_tests.sh /workdir/
COPY docker/tests/ /workdir/tests/

WORKDIR /software

COPY /docker/generators.sh /software/
ENTRYPOINT ["/software/generators.sh"]
CMD ["/bin/bash"]

RUN mkdir work/ && cd work/ \
    && ln -s ../ntsim/ntsim/tutorials/configs/ .