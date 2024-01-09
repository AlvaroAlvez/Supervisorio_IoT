#!/bin/bash

#discover the current gateway for actual eth0

gateway_eth0=$(ip route show | grep default | grep -i "eth0" | awk '{print $3}')

#check if eth0 gateway exists

if [ -n "$gateway_eth0" ]; then
     sudo ip route del default via "$gateway_eth0" dev eth0


     sudo ip route add default dev eth0 onlink metric 700
fi
