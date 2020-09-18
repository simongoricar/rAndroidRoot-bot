# Use python 3.8 image
FROM python:3.8-alpine

# Copy and install requirements
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create the bot user
RUN useradd --create-home bot
WORKDIR /home/bot
USER bot

# Copy files
COPY . .

CMD ["python", "./bot.py"]