FROM python:3.9

WORKDIR /bot

COPY . .

COPY requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
