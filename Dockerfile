FROM python:3.12

WORKDIR /work

RUN pip --no-input --no-cache-dir --disable-pip-version-check install poetry && \
    poetry config virtualenvs.create false
ADD pyproject.toml /work/
RUN poetry install

ADD ./app /work/app

CMD ["python", "-m", "app", "worker"]
