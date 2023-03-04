FROM python:3.7

WORKDIR /var/chrome

# RUN curl -O https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip && \
#   unzip chromedriver_linux64.zip && \
#   rm chromedriver_linux64.zip



# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ENV PATH "$PATH:/var/chrome"

# RUN apt-get update && apt-get install -y chromium=80.0.3987.162-1~deb10u1

COPY src/* /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

# ENTRYPOINT ["python", "scheduler.py"]
