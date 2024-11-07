## Disable HTTPS KeyCloak

```
sudo docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin -d quay.io/keycloak/keycloak:23.0.6 start-dev
```

Go inside container and modify config file

```
sudo docker exec -it 28db226ab2d8 /bin/bash

cd /opt/keycloak/bin/

./kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin

./kcadm.sh update realms/master -s sslRequired=NONE --server http://localhost:8080

```

Run keycloak-login
```
sudo docker run -it -p 8501:8501 -e KC_SERVER="172.17.0.1" kc-login:v1.0

```