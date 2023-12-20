FROM python:3.11

ENV APP /Module_4

WORKDIR $APP

COPY . .

EXPOSE 5000 3000

ENTRYPOINT ["python", "main.py"]