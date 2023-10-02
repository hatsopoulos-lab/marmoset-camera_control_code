#!/bin/bash

### Example

#### tar_images.sh TYJL 2023_06_22 moths

marms=$1
date=$2
exp=$3

if [ $exp == 'sleep' ]; then
    data_folder=/media/marmosets/fast1/$exp/$marms
else
    data_folder=/media/marmosets/fast2/$exp/$marms
    other_data_folder=/media/marmosets/fast1/$exp/$marms
    echo $other_data_folder/$date
    echo $data_folder/ 
    cp -r $other_data_folder/$date/ $data_folder/  
fi

cd $data_folder
tar -cf /media/marmosets/Elements/JL_cricket_backup/cricket/$date.tar $date
