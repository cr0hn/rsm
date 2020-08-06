FROM python:3.8-slim as builder

COPY . /rsm
RUN pip wheel --no-cache-dir --wheel-dir=/root/wheels -r /rsm/requirements.txt \
    &&  pip wheel --no-cache-dir --wheel-dir=/root/wheels /rsm

FROM python:3.8-slim-buster
COPY --from=builder /root/wheels /root/wheels

RUN python -m pip install --no-cache-dir --no-cache /root/wheels/* \
    && rm -rf /root/wheels

ENTRYPOINT ["rsm"]
