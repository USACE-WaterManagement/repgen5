# Alternate image: registry1.dso.mil/ironbank/opensource/python:3.11.9-alpine 
ARG BASE_IMAGE=python:3.11-alpine3.19
FROM $BASE_IMAGE as build
# ironbank image requires USER root to build
USER root
RUN apk add --no-cache zip
COPY . /repgen5
WORKDIR /repgen5
RUN ./package.sh

FROM $BASE_IMAGE
USER root
ADD ./requirements.txt /tmp
# Bug in ironport that doesn't clear the apk cache; see https://repo1.dso.mil/dsop/opensource/python/python-alpine/python-alpine-311/-/issues/35
RUN rm -rf /var/cache/apk/* ; pip install -r /tmp/requirements.txt ; rm /tmp/requirements.txt
COPY --from=build /repgen5/build/repgen /
COPY --from=build /repgen5/converter/convert_report.py /repgen5/converter/convert.sh /converter/
ADD ./entrypoint.sh /

# Location of report templates (--in arg)
VOLUME /input
# Location of data files (--file arg)
VOLUME /data
# Location of report output (--out arg)
VOLUME /output
# Temporary file location
VOLUME /tmp

ENV UID=1000
ENV GID=1000
ENV OFFICE_ID=
ENV TZ=UTC
ENV CDA_PRIMARY=cwms-data.usace.army.mil:443/cwms-data
ENV CDA_TIMEOUT=30
ENV COMPATIBILITY_MODE=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER $UID:$GID
LABEL org.opencontainers.image.authors="Daniel.T.Osborne@usace.army.mil"

ENTRYPOINT ["/entrypoint.sh"]
