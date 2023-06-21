FROM python:alpine3.17
COPY . /app
WORKDIR /app
RUN ["pip", "install", "-r", "requirements.txt"]
WORKDIR /app/src
# RUN python manage.py migrate
EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD python manage.py migrate; python manage.py runserver 0.0.0.0:8000