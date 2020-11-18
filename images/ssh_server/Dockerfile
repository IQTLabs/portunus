FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    openssh-server \
    ubuntu-server \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/run/sshd
RUN mkdir -p /root/.ssh
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
