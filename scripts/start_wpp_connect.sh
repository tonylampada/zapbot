docker run -d --rm \
    -p 21465:21465 \
    --name wppconnect-server \
    -v $(pwd)/docker/wppconfig.js:/usr/src/wpp-server/dist/config.js \
    -v $(pwd)/wppconnect_tokens:/usr/src/wpp-server/tokens \
    wppconnect-server