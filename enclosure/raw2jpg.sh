#!/bin/bash

### Example

###  sudo Documents/camera_control_code/raw2jpg_bci.sh 'BCI02' '2021_01_08' 'test' '1'

# inputs are 'subjectID' 'Date' 'experiment_label' 'session'

marms=$1
date=$2
exp=$3
sessionNum=$4

num2convert=10000

processingPath='/home/marms/Documents/camera_control_code/converter_files_8_threads'
session_folder=/media/marms/fast/$exp/$marms/$date/session$sessionNum

tmpPath_cam1=$session_folder/cam1
tmpPath_cam2=$session_folder/cam2
tmpPath_cam3=$session_folder/cam3
tmpPath_cam4=$session_folder/cam4

rawPath_cam1=$session_folder/raw_cam1
rawPath_cam2=$session_folder/raw_cam2
rawPath_cam3=$session_folder/raw_cam3
rawPath_cam4=$session_folder/raw_cam4

jpgPath_cam1=$session_folder/jpg_cam1
jpgPath_cam2=$session_folder/jpg_cam2
jpgPath_cam3=$session_folder/jpg_cam3
jpgPath_cam4=$session_folder/jpg_cam4

mkdir -p $jpgPath_cam1
mkdir -p $jpgPath_cam2
mkdir -p $jpgPath_cam3
mkdir -p $jpgPath_cam4

mkdir -p $tmpPath_cam1
mkdir -p $tmpPath_cam2
mkdir -p $tmpPath_cam3
mkdir -p $tmpPath_cam4

cp $processingPath/converter_raw2jpg_cam1 $session_folder/
cp $processingPath/converter_raw2jpg_cam2 $session_folder/
cp $processingPath/converter_raw2jpg_cam3 $session_folder/
cp $processingPath/converter_raw2jpg_cam4 $session_folder/

storagePath=/media/marms/storage/$exp/$marms/$date/session$sessionNum

mkdir -p $storagePath/jpg_cam1
mkdir -p $storagePath/jpg_cam2
mkdir -p $storagePath/jpg_cam3
mkdir -p $storagePath/jpg_cam4

grabFiles=1
while [ $grabFiles == 1 ]; do

    #### Experiment 1 image compression and move to DATA
    cd $session_folder
    ls $rawPath_cam1/ | head -$num2convert | xargs -i mv $rawPath_cam1/{} $tmpPath_cam1/
    ./converter_raw2jpg_cam1
    ls $tmpPath_cam1/ | head -$num2convert | xargs -i rm $tmpPath_cam1/{}
    find $jpgPath_cam1/ -name "*.jpg" | xargs -i mv {} $storagePath/jpg_cam1

    ls $rawPath_cam2/ | head -$num2convert | xargs -i mv $rawPath_cam2/{} $tmpPath_cam2/
    ./converter_raw2jpg_cam2
    ls $tmpPath_cam2/ | head -$num2convert | xargs -i rm $tmpPath_cam2/{}
    find $jpgPath_cam2/ -name "*.jpg" | xargs -i mv {} $storagePath/jpg_cam2

    ls $rawPath_cam3/ | head -$num2convert | xargs -i mv $rawPath_cam3/{} $tmpPath_cam3/
    ./converter_raw2jpg_cam3
    ls $tmpPath_cam3/ | head -$num2convert | xargs -i rm $tmpPath_cam3/{}
    find $jpgPath_cam3/ -name "*.jpg" | xargs -i mv {} $storagePath/jpg_cam3

    ls $rawPath_cam4/ | head -$num2convert | xargs -i mv $rawPath_cam4/{} $tmpPath_cam4/
    ./converter_raw2jpg_cam4
    ls $tmpPath_cam4/ | head -$num2convert | xargs -i rm $tmpPath_cam4/{}
    find $jpgPath_cam4/ -name "*.jpg" | xargs -i mv {} $storagePath/jpg_cam4
done