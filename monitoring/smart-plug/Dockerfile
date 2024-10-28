FROM python:3.7

RUN mkdir /code
WORKDIR /code
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
ADD ./main.py /code/main.py
ADD ./entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT /code/entrypoint.sh
