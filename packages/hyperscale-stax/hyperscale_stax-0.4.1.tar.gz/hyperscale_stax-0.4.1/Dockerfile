FROM python:3.13-alpine@sha256:527c28b29498575b851ad88e7522ac7201bbd9e920d2c11b00ff2b39b315f5f8 AS builder

ARG VERSION

WORKDIR /app

COPY ./requirements.txt .
COPY ./dist/hyperscale_stax-$VERSION-py3-none-any.whl .

RUN pip install --require-hashes --no-cache-dir --prefix /app/packages -r requirements.txt
RUN pip install --no-deps --no-cache-dir --prefix /app/packages hyperscale_stax-$VERSION-py3-none-any.whl

FROM python:3.13-alpine@sha256:527c28b29498575b851ad88e7522ac7201bbd9e920d2c11b00ff2b39b315f5f8

WORKDIR /app

COPY --from=builder /app/packages /app/packages
ENV PYTHONPATH=/app/packages/lib/python3.13/site-packages
ENV PATH="/app/packages/bin:${PATH}"

RUN addgroup -g 1001 -S appgroup && \
  adduser -S appuser -u 1001 -G appgroup && \
  chown -R appuser:appgroup /app

USER appuser

ENTRYPOINT ["/app/packages/bin/stax"]
