#!/bin/bash

### Example

#### scp_images.sh TYJL 2023_06_22 moths daltonm

marms=$1
date=$2
exp=$3
cnet=$4

if [ $exp == 'sleep' ]; then
    data_folder=/media/marmosets/fast1/$exp/$marms/$date
else
    data_folder=/media/marmosets/fast2/$exp/$marms/$date
fi

scp $data_folder.tar $cnet@midway3.rcc.uchicago.edu:/scratch/midway3/$cnet/kinematics_jpgs/$exp/$marms/
