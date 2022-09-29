# dockepcap
a project used to dump all traffic through the container net namespace

Build docker image
```bash
docker build -t dockerpcap .
```

Container run
```bash
docker run -d --privileged=true -v /var/run/:/var/run/ --net=host dockerpcap
```