# a gente precisa primeiro ter uma imagem docker com o wpp connect rodando
git clone https://github.com/wppconnect-team/wppconnect-server.git
cd wppconnect-server
docker build -t wppconnect-server .
