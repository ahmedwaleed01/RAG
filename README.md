## Install Requirments

```bash
pip install -r requirements.txt
```

## Run FastApi Server

```bash
uvicorn main:app --reload
```

## Build Docker

```bash
docker compose -f docker-compose.yml up -d --build
```

### Stop Docker

```bash
sudo docker stop $(sudo docker ps -qa)
```

### Remove Docker

```bash
sudo docker rm $(sudo docker ps -qa)
```

### Remove image

```bash
sudo docker rmi $(sudo docker images -qa)
```

## Remove volumes

```bash
sudo docker volume rm $(sudo docker volume ls -q)
```

### Remove all

```bash
 sudo docker system prune --all
```
