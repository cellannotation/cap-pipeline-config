docker-compose down
docker-compose run -d --service-ports vfb-kb
sleep 300
docker-compose run vfb-kb2kb
docker-compose run vfb-validatekb
docker-compose run vfb-collectdata 
docker run --volume /tmp/pipeline:/out --network="host" -e KBpassword=neo4j/neo -e KBserver=http://127.0.0.1:7474 matentzn/vfb-pipeline-collectdata
