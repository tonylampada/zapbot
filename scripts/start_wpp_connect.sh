docker run -d --rm \
    -p 21465:21465 \
    --name wppconnect-server \
    -v $(pwd)/docker/wppconfig.js:/usr/src/wpp-server/dist/config.js \
    -v $(pwd)/wppconnect_tokens:/usr/src/wpp-server/tokens \
    -v $(pwd)/wppconnect_userDataDir:/usr/src/wpp-server/userDataDir \
    wppconnect-server
