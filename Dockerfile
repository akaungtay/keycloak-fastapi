# Base Image
FROM python:3.10-alpine
# creating working folder
WORKDIR /app
# setting environmental variable
ENV PORT=8501
ENV KC_SERVER="localhost"
ENV HM_SERVER="localhost"
# install software dependencies
# RUN apk add --no-cache gcc musl-dev linux-headers
# install App requirement
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# exposing port of container
EXPOSE 8501
# copy code
COPY . .
#  run
CMD ["python", "keycloak_login.py"]