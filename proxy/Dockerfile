FROM python:2.7.2
MAINTAINER Kavish Jain "kavishme@gmail.com"
COPY . ./
WORKDIR ./
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["proxy.py"]
