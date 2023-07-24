image_name=synology-chat-gpt:debug
container_name=synology-chat-gpt-debug
docker build . -t image_name --no-cache
docker stop $container_name || echo ignore
docker rm $container_name || echo ignore
docker run --rm \
    -p 60000:8000 \
    --name $container_name \
    -v $(pwd)/data:/app/data \
    -e OPENAI_API_BASE=https://openai-service.mbmzone.com/v1 \
    image_name