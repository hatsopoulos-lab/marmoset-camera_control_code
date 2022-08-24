# coding=utf-8

import os
import PySpin
import time
import threading
import argparse

class params:
    frameRate = 60
    exposure = 4000.0
    gain = 14
    nCams = 4 
    eventSeparator = 1/frameRate * 5
    crop_by_cam = [(0, 0), (0, 0), (0, 0), (0, 0)]
    redRatio = 1.2
    blueRatio = 3.5
    cam1 = '21503284'
    cam2 = '21503286'
    cam3 = '21503281'
    cam4 = '19129176'

NUM_BUFFERS = 10

def exposure(cam):
    try:
        result = True
        # Disable automatic exposure, ensure desired exposure time does not exceed the maximum and set exposure
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

        exposure_time_to_set = params.exposure
        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)

        # disable automatic gain, ensure desired gain does not exceed maximum and set gain 
        cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        gain_to_set = params.gain
        gain_to_set = min(cam.Gain.GetMax(), gain_to_set)
        cam.Gain.SetValue(gain_to_set)
 
        # Disable automatic white balance and set specific red and blue ratios. If lighting changes, use spinview to determine new values for this.
        cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Off)
        cam.BalanceRatioSelector.SetValue(PySpin.BalanceRatioSelector_Red)
        cam.BalanceRatio.SetValue(params.redRatio)
        cam.BalanceRatioSelector.SetValue(PySpin.BalanceRatioSelector_Blue)
        cam.BalanceRatio.SetValue(params.blueRatio)    
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def configure_trigger_and_output_primary(cam): 

    result = True
    print('*** Configuring trigger and exposure signal output for primary camera ***\n')
    try: 
        # Set primary cam to start acquisition when it receives an input signal on line 3)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        cam.AcquisitionFrameRateEnable.SetValue(True)
        cam.AcquisitionFrameRate.SetValue(params.frameRate)
        cam.TriggerSelector.SetValue(PySpin.TriggerSelector_AcquisitionStart)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Line3)
        cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        
        # set primary camera to output exposure active signal on line 1, with line2 used along with pull-up resistor to boost output to 5V. The  
        cam.LineSelector.SetValue(PySpin.LineSelector_Line1)
        cam.LineMode.SetValue(PySpin.LineMode_Output)
        cam.LineSource.SetValue(PySpin.LineSource_ExposureActive)
        cam.LineSelector.SetValue(PySpin.LineSelector_Line2)
        cam.V3_3Enable.SetValue(True)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def configure_trigger_and_output_secondary(cam): #+++

    result = True

    print('*** Configuring trigger and exposure signal output for secondary camera ***\n')

    try:
        # Set secondary cam to acquire a single frame when it receives a LevelHigh input on line3
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Line3)
        cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

        # Set secondary camera to output exposure active signal on line 2 --> recorded in cerebus nsx file
        cam.LineSelector.SetValue(PySpin.LineSelector_Line2)
        cam.LineMode.SetValue(PySpin.LineMode_Output)
        cam.LineSource.SetValue(PySpin.LineSource_ExposureActive)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def configure_image_settings(cam, crop):

    try:
        result = True   

        cam.PixelFormat.SetValue(PySpin.PixelFormat_BayerRG8)

        if crop[0] == 0:
            width_to_set = cam.WidthMax()
        else:
            width_to_set = crop[0]            
        cam.Width.SetValue(width_to_set)

        if crop[1] == 0:
            height_to_set = cam.HeightMax()
        else:
            height_to_set = crop[1]            
        cam.Height.SetValue(height_to_set)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def acquire_images(cams):
    try:
        result = True
        
        i = 1
        for cam in cams:
            cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous) 

            s_node_map = cam.GetTLStreamNodeMap()

            # Set stream buffer Count Mode to manual
            stream_buffer_count_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferCountMode'))
            stream_buffer_count_mode_manual = PySpin.CEnumEntryPtr(stream_buffer_count_mode.GetEntryByName('Manual'))
            stream_buffer_count_mode.SetIntValue(stream_buffer_count_mode_manual.GetValue())

            # Retrieve and modify Stream Buffer Count
            buffer_count = PySpin.CIntegerPtr(s_node_map.GetNode('StreamBufferCountManual'))
            buffer_count.SetValue(NUM_BUFFERS)
            
            # retrieve and modify stream buffer mode
            handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))            
            handling_mode_entry = handling_mode.GetEntryByName('OldestFirst')
            handling_mode.SetIntValue(handling_mode_entry.GetValue())

            #  Begin acquiring images
            cam.BeginAcquisition()
            print('\n\n Acquisition has begun from camera %d ... \n \n' %i)
            i += 1      

        threads = []
        timestamps = []
        for camNum, cam in enumerate(cams): 
            timestamps.append([0, 1])
            # this is the main code that ensures cameras are synced frame by frame. It sends arguments to function 'image_thread' below. The process can be stopped at any time with Ctrl+C (sometimes you have to push it multiple times). 
            threads.append(threading.Thread(target = image_thread, args = (cam, camNum+1, timestamps[-1], filename))) 

        for t in threads:
            t.start()
                
        for t in threads:
            t.join()
        
        for cam in cams:
           cam.UserOutputSelector.SetIntValue(PySpin.UserOutputSelector_UserOutput0)
           cam.UserOutputValue.SetValue(False)
           cam.EndAcquisition()

        for cam in cams:
           cam.UserOutputSelector.SetIntValue(PySpin.UserOutputSelector_UserOutput0)
           cam.UserOutputValue.SetValue(False)
           cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

def image_thread(cam, cam_num, timestamps, filename): #+++
    event = 1

    record = True
    while record:
        try:
     
            image_result = cam.GetNextImage()
            
            timestamp_microSec = image_result.GetTimeStamp() 
            timestamps.append(timestamp_microSec * 1e-9)
            latency = (timestamps[-1] - timestamps[-2])
            
            if event == 1:
                eventNum = event
                frameNum = 1
                event += 1
                firstFrameTime = time.strftime('%H%M-%S')
            elif latency > params.eventSeparator:
                eventNum = event
                event += 1    
                frameNum = 1
                firstFrameTime = time.strftime('%H%M-%S')
            else: 
                eventNum = event - 1
                frameNum += 1
    
    
            print('\n Cam %d    Event = %d     frame = %d' % (cam_num, eventNum, frameNum))
                
            # Create a unique filename
            image_filename = '%s/raw_cam%d/%s_%s_%s_session_%d_cam%d_event_%s_frame_%s_currentTime_%d_%s.raw' % (filename.image_folder, 
                                                                                                             cam_num, 
                                                                                                             filename.marms, 
                                                                                                             filename.date, 
                                                                                                             filename.expName, 
                                                                                                             filename.session, 
                                                                                                             cam_num, 
                                                                                                             "{:03}".format(int(eventNum)), 
                                                                                                             "{:07d}".format(int(frameNum)),
                                                                                                             round(timestamp_microSec), 
                                                                                                             firstFrameTime) 
            image_result.Save(image_filename)  
           
            image_result.Release()
            
            timestamps.pop(0)
    
        except KeyboardInterrupt:
            record = False
            return False
    
        # except PySpin.SpinnakerException as ex:
        #     print('Error: %s' % ex)
        #     record = False
        #     return False
      
def reset_trigger(cam):
    result = True
    cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    return result

def reset_exposure(cam):
    result = True
    cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
    return result

def run_multiple_cameras(cams):
    try:
        result = True
        err = False
        
        primaryCam = cams[0]
        secondaryCams = cams[1:]
        
        # Initialize camera
        for cam in cams:
            cam.Init()
            exposure(cam)
           
        for cam, crop in zip(cams, params.crop_by_cam):
            configure_image_settings(cam, crop)

        configure_trigger_and_output_primary(primaryCam)
        for cam in secondaryCams:
            configure_trigger_and_output_secondary(cam)

        # Acquire images
        acquire_images(cams)
        
        for cam in cams:
            result &= reset_exposure(cam)
            result &= reset_trigger(cam)

            # Deinitialize camera
            cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():

    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    for cam_num in range(params.nCams):
        file_path = '%s/raw_cam%d' %(filename.image_folder, cam_num+1)
        if not os.path.isdir(file_path): 
            os.makedirs(file_path)

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:
        cam_list.Clear()
        system.ReleaseInstance()
        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    for cam in range(0, num_cameras): 
        if cam_list.GetByIndex(cam).TLDevice.DeviceSerialNumber() == params.cam1:
            cam1 = cam_list.GetByIndex(cam)
        elif cam_list.GetByIndex(cam).TLDevice.DeviceSerialNumber() == params.cam2:
            cam2 = cam_list.GetByIndex(cam)
        elif cam_list.GetByIndex(cam).TLDevice.DeviceSerialNumber() == params.cam3:
            cam3 = cam_list.GetByIndex(cam)
        elif cam_list.GetByIndex(cam).TLDevice.DeviceSerialNumber() == params.cam4:
            cam4 = cam_list.GetByIndex(cam)
    cams = [cam1, cam2, cam3, cam4]
    result &= run_multiple_cameras(cams)
    
    # Cleanup
    for cam in cams:
        del cam

    cam_list.Clear()
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--marms", required=True, type=str,
        help="marmoset 4-digit code, e.g. 'JLTY'")
    ap.add_argument("-e", "--exp_name", required=True, type=str,
     	help="experiment name, e.g. free, foraging, BeTL, crickets, moths, etc")
    ap.add_argument("-s", "--session", required=True, type=int,
     	help="name of calibration session")

    args = vars(ap.parse_args())
    
    class filename: 
        expName = args['exp_name'] #'test' #'foraging'
        marms = args['marms'] 
        session = args['session']
        date = time.strftime('%Y_%m_%d')
        if type(session) == str:
            image_folder = '/media/marms/fast/%s/%s/%s/%s'        % (expName, marms, date, session)
        else:
            image_folder = '/media/marms/fast/%s/%s/%s/session%d' % (expName, marms, date, session)
    main()
