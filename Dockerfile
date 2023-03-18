FROM pypy:3.9-slim-buster
ENV PYTHONUNBUFFERED 1

WORKDIR /app/
COPY . .

RUN pip install --user -r requirements.txt

CMD ["pypy3", "main.py"]