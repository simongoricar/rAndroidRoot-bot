# Use python 3.8 image
FROM python:3.8-alpine
RUN apk update && apk add --virtual build-dependencies build-base gcc wget git

# Copy and install requirements
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN apk del build-dependencies

# Create the bot user
RUN adduser --disabled-password bot
WORKDIR /home/bot
USER bot

# Copy files
COPY . .

CMD ["python", "./bot.py"]