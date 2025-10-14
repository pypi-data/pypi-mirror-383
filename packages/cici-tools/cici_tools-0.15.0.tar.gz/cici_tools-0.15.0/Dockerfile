# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.11-alpine AS python-build

WORKDIR /build/

# hadolint ignore=DL3018
RUN apk add --no-cache git

# hadolint ignore=DL3013,DL3042
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install --upgrade uv

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache \
    uv pip install --system -r requirements.txt

COPY . ./

RUN --mount=type=cache,target=/root/.cache \
    uv pip install --system .

RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip uninstall -y uv \
    && python3 -m pip uninstall -y pip \
    && rm -rf /usr/local/lib/python3.11/site-packages/pip*

ARG CONTAINER_PROXY
FROM ${CONTAINER_PROXY}python:3.11-alpine

COPY --from=python-build /usr/local/ /usr/local/

ENV PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"

RUN addgroup -g 2000 cici \
    && adduser -u 2000 -g 2000 -SD cici

ENV HOME="/tmp"

USER cici

ENTRYPOINT ["cici"]
