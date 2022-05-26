FROM python

WORKDIR /mores

COPY ./requirements.txt /mores/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /mores/requirements.txt

COPY ./app /mores/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
