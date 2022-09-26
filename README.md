# dockepcap
a project used to dump all traffic through the container net namespace

Build docker image
```bash
docker build -t dokcerpcap:latest .
```

Container run
```bash
docker run -d --privileged=true -v /var/run/:/var/run/ --net=host -p 80:80
```