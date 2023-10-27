FROM python:3.10

WORKDIR /application

COPY requirements.txt /application/

RUN pip install --no-cache-dir -r requirements.txt

COPY /src/apigateway /application/apigateway
COPY /app/server.py /application/server.py
COPY /.env /application/.env

EXPOSE 8443


CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8443"]