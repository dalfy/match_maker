FROM python:2.7
MAINTAINER mrsixw

RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
EXPOSE 9913
ENTRYPOINT ["python"]
CMD ["match_maker.py"]
