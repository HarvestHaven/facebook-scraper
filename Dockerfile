FROM python:3.6

WORKDIR /var/chrome

RUN curl -O https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip && \
  rm chromedriver_linux64.zip

ENV PATH "$PATH:/var/chrome"

RUN apt-get update && apt-get install -y chromium=80.0.3987.162-1~deb10u1

COPY src/* /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "scheduler.py"]
