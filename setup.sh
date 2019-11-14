#!/bin/bash

function software_installation {
    sudo apt update -y
    sudo apt upgrade -y
    
    sudo apt install -y \
        curl \
        git \
        vim \
        software-properties-common \
        python3-dev \
        python3-pip \
        network-manager \
        firewalld \
        acl \
        selinux-basics \
        selinux-policy-default
    
    # pysftp dependencies
    sudo apt install -i
        libffi-dev \
        libssl-dev
    sudo pip3 install pysftp
}

function read_not_empty {
    read -p "$1: " value_to_read
    while [ -z "$value_to_read" ]; do
        read -p "$1: " value_to_read
    done
    echo "$value_to_read"
}

function configure_network {
    sudo systemctl enable network-manager
    sudo nmcli device disconnect wlan0 2>/dev/null

    # - Configure firewall
    sudo systemctl mask iptables
    sudo systemctl enable firewalld
    sudo systemctl start firewalld

    sudo firewall-cmd --permanent --add-interface eth0
    sudo firewall-cmd --permanent --add-rich-rule "rule family='ipv4' source address='192.168.0.0/24' service name='ssh' accept"
    sudo firewall-cmd --permanent --add-rich-rule "rule family='ipv4' source address='${backup_host}/32' service name='ssh' accept"
    sudo firewall-cmd --reload
}

echo 'Begining installation'
software_installation
cp config.py.dist config.py
configure_network

