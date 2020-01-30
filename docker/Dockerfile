# master
FROM ubuntu:18.04

RUN apt update && \
    apt install -y apt-rdepends build-essential devscripts equivs gnupg2 liblz4-tool python3-distutils vim wget && \
    apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654 && \
    wget packages.bit-bots.de/key.asc -O- | apt-key add - && \
    mkdir build

WORKDIR /build

# Generate large package list
RUN echo "deb http://packages.ros.org/ros/ubuntu bionic main" > /etc/apt/sources.list.d/ros-latest.list && \
    echo "deb-src http://packages.ros.org/ros/ubuntu bionic main" >> /etc/apt/sources.list.d/ros-latest.list && \
    apt update

COPY build_package /build/
COPY resolve_dependencies /build/

