docker run -d \
    -p 21465:21465 \
    --restart unless-stopped \
    --name wppconnect-server \
    -v $(pwd)/docker/wppconfig.js:/usr/src/wpp-server/dist/config.js \
    wppconnect-server

#    -v $(pwd)/wppconnect_tokens:/usr/src/wpp-server/tokens \
#    -v $(pwd)/wppconnect_userDataDir:/usr/src/wpp-server/userDataDir \
