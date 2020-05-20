FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl openssh-server ubuntu-server
RUN mkdir -p /var/run/sshd
RUN mkdir -p /root/.ssh
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
