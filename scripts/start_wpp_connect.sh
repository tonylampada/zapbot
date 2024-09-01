docker run -it --rm \
    -p 21465:21465 \
    --name wppconnect-server \
    -v $(pwd)/docker/wppconfig.js:/usr/src/wpp-server/dist/config.js \
    wppconnect-server