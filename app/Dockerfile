FROM python:3.5.2
MAINTAINER Kavish Jain "kavishme@gmail.com"
COPY . ./
WORKDIR ./
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["./app.py"]
