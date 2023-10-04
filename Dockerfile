FROM python:3.11-bullseye

RUN    mkdir -p /opt/app-root/src \
    && chown -R 1001:0 /opt/app-root/src \
    && chmod -R g+rwx /opt/app-root/src

WORKDIR /opt/app-root/src

COPY app.py .
COPY maxi.py .
COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER 1001
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
