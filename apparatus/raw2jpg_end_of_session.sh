#!/bin/bash

### Example

###  sudo Documents/camera_control_code/raw2jpg_bci.sh 'BCI02' '2021_01_08' 'test' '1'

# inputs are 'subjectID' 'Date' 'experiment_label' 'session'

marms=$1
date=$2
exp=$3
sessionNum=$4

num2convert=10000

reldir="$( dirname -- "$0"; )";
cd "$reldir";
directory="$( pwd; )";
echo "Directory is ${directory}";

processingPath=$directory/converter_files_maximum_threads
#processingPath=/home/marms/Documents/camera_control_code/converter_files_maximum_threads
session_folder1=/media/marmosets/fast1/$exp/$marms/$date/session$sessionNum
session_folder2=/media/marmosets/fast2/$exp/$marms/$date/session$sessionNum

tmpPath_cam1=$session_folder1/cam1
tmpPath_cam2=$session_folder1/cam2
tmpPath_cam3=$session_folder2/cam3
tmpPath_cam4=$session_folder2/cam4
tmpPath_cam5_fast1=$session_folder1/cam5
tmpPath_cam5_fast2=$session_folder2/cam5

rawPath_cam1=$session_folder1/raw_cam1
rawPath_cam2=$session_folder1/raw_cam2
rawPath_cam3=$session_folder2/raw_cam3
rawPath_cam4=$session_folder2/raw_cam4
rawPath_cam5_fast1=$session_folder1/raw_cam5
rawPath_cam5_fast2=$session_folder2/raw_cam5

jpgPath_cam1=$session_folder1/jpg_cam1
jpgPath_cam2=$session_folder1/jpg_cam2
jpgPath_cam3=$session_folder2/jpg_cam3
jpgPath_cam4=$session_folder2/jpg_cam4
jpgPath_cam5_fast1=$session_folder1/jpg_cam5
jpgPath_cam5_fast2=$session_folder2/jpg_cam5

mkdir -p $jpgPath_cam1
mkdir -p $jpgPath_cam2
mkdir -p $jpgPath_cam3
mkdir -p $jpgPath_cam4
mkdir -p $jpgPath_cam5_fast1
mkdir -p $jpgPath_cam5_fast2

mkdir -p $tmpPath_cam1
mkdir -p $tmpPath_cam2
mkdir -p $tmpPath_cam3
mkdir -p $tmpPath_cam4
mkdir -p $tmpPath_cam5_fast1
mkdir -p $tmpPath_cam5_fast2

cp $processingPath/converter_raw2jpg_cam1 $session_folder1/
cp $processingPath/converter_raw2jpg_cam2 $session_folder1/
cp $processingPath/converter_raw2jpg_cam3 $session_folder2/
cp $processingPath/converter_raw2jpg_cam4 $session_folder2/
cp $processingPath/converter_raw2jpg_cam5 $session_folder1/
cp $processingPath/converter_raw2jpg_cam5 $session_folder2/

grabFiles=1
while [ $grabFiles == 1 ]; do

    #### Experiment 1 image compression 
    cd $session_folder1
    ls $rawPath_cam1/ | head -$num2convert | xargs -i mv $rawPath_cam1/{} $tmpPath_cam1/
    ./converter_raw2jpg_cam1
    ls $tmpPath_cam1/ | head -$num2convert | xargs -i rm $tmpPath_cam1/{}

    cd $session_folder2
    ls $rawPath_cam3/ | head -$num2convert | xargs -i mv $rawPath_cam3/{} $tmpPath_cam3/
    ./converter_raw2jpg_cam3
    ls $tmpPath_cam3/ | head -$num2convert | xargs -i rm $tmpPath_cam3/{}

    cd $session_folder1
    ls $rawPath_cam2/ | head -$num2convert | xargs -i mv $rawPath_cam2/{} $tmpPath_cam2/
    ./converter_raw2jpg_cam2
    ls $tmpPath_cam2/ | head -$num2convert | xargs -i rm $tmpPath_cam2/{}
    
    cd $session_folder2
    ls $rawPath_cam4/ | head -$num2convert | xargs -i mv $rawPath_cam4/{} $tmpPath_cam4/
    ./converter_raw2jpg_cam4
    ls $tmpPath_cam4/ | head -$num2convert | xargs -i rm $tmpPath_cam4/{}
    
    ls $rawPath_cam5_fast2/ | head -$num2convert | xargs -i mv $rawPath_cam5_fast2/{} $tmpPath_cam5_fast2/
    ./converter_raw2jpg_cam5
    ls $tmpPath_cam5_fast2/ | head -$num2convert | xargs -i rm $tmpPath_cam5_fast2/{}
    
    cd $session_folder1
    ls $rawPath_cam5_fast1/ | head -$num2convert | xargs -i mv $rawPath_cam5_fast1/{} $tmpPath_cam5_fast1/
    ./converter_raw2jpg_cam5
    ls $tmpPath_cam5_fast1/ | head -$num2convert | xargs -i rm $tmpPath_cam5_fast1/{} 
    
done
