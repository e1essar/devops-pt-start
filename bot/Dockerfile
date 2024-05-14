FROM python:3.9
WORKDIR /bot
COPY . .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5001
CMD ["python", "bot.py"]