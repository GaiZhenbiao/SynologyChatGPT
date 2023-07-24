FROM python:3.8.10-slim-buster
# config when launch container
ENV APP_DATA_DIR=/app/data
ENV APP_ALLOWED_HOSTS=*
ENV OPENAI_API_BASE=https://api.openai.com/v1
VOLUME [ "/app/data" ]
# build
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
# run
RUN chmod +x entrypoint.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]
EXPOSE 8000