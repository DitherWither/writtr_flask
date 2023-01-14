# Note to self: For dev purposes only, don't use when deploying
# expects a volume at /app

FROM python:latest
RUN mkdir /build
COPY requirements.txt /build/requirements.txt
RUN pip install -r /build/requirements.txt
EXPOSE 5000
WORKDIR /app

CMD ["/bin/sh", "/app/run.sh"]
