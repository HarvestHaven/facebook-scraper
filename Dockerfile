FROM python:3.7

WORKDIR /var/chrome

RUN curl -O https://chromedriver.storage.googleapis.com/111.0.5563.64/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip && \
  rm chromedriver_linux64.zip

ENV PATH "$PATH:/var/chrome"

RUN apt-get update && apt-get install -y chromium=111.0.5563.110-1~deb11u1

COPY src/* /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "scheduler.py"]
