import os
import PySpin
import time
import threading
import argparse

class params: 
    frameRate = 30
    exposure = 6000.0 # in microseconds. Increasing exposure will allow more light in but also increase motion blur
    gain = 14 # increase for brighter images, decrease for darker
    crop_by_cam = [(0, 0), (0, 0)]
    eventSeparator = 1/frameRate * 5

    nCams = 1
    cam1 = '23139007'
    
#This sets up a small number of buffers for each camera. It doesn't mean anything, but if you don't do this the first camera will take up all of the space allotted for buffers and the second camera will fail to initialize. 
NUM_BUFFERS = 10
NS_PER_S = 1000000000  # The number of nanoseconds in a second

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
        
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result

def configure_single_cam_trigger_and_output(cam): #+++

    result = True
    print('*** Configuring trigger and exposure signal output for primary camera ***\n')
    try:
        # Set primary cam to acquire a single frame when the counter starts each cycle (the counter resets after it reaches the Period, as determined by the fps)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Counter0Start)
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

# def configure_trigger_and_output_primary(cam): #+++

#     result = True
#     print('*** Configuring trigger and exposure signal output for primary camera ***\n')
#     try:
#         # Set primary cam to acquire a single frame when the counter starts each cycle (the counter resets after it reaches the Period, as determined by the fps)
#         cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
#         cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
#         cam.TriggerSource.SetValue(PySpin.TriggerSource_Counter0Start)
#         cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)
#         cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        
#         # set primary camera to output exposure active signal on line 1, with line2 used along with pull-up resistor to boost output to 5V. The  
#         cam.LineSelector.SetValue(PySpin.LineSelector_Line1)
#         cam.LineMode.SetValue(PySpin.LineMode_Output)
#         cam.LineSource.SetValue(PySpin.LineSource_ExposureActive)
#         cam.LineSelector.SetValue(PySpin.LineSelector_Line2)
#         cam.V3_3Enable.SetValue(True)

#     except PySpin.SpinnakerException as ex:
#         print('Error: %s' % ex)
#         return False

#     return result


# def configure_trigger_and_output_secondary(cam): #+++

#     result = True

#     print('*** Configuring trigger and exposure signal output for secondary camera ***\n')

#     try:
#         # Set secondary cam to acquire a single frame when it receives a LevelHigh input on line3
#         cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
#         cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
#         cam.TriggerSource.SetValue(PySpin.TriggerSource_Line3)
#         cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)
#         cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

#         # Set secondary camera to output exposure active signal on line 2 --> recorded in cerebus nsx file
#         cam.LineSelector.SetValue(PySpin.LineSelector_Line2)
#         cam.LineMode.SetValue(PySpin.LineMode_Output)
#         cam.LineSource.SetValue(PySpin.LineSource_ExposureActive)

#     except PySpin.SpinnakerException as ex:
#         print('Error: %s' % ex)
#         return False

#     return result

def configureLogicBlock(cam): #+++
    
    # This function and the configureCounter function allow the same pulse to begin recordings and end recordings. 

    cam.UserOutputSelector.SetValue(PySpin.UserOutputSelector_UserOutput0) #
    cam.UserOutputValue.SetValue(False)

    cam.LogicBlockSelector.SetValue(PySpin.LogicBlockSelector_LogicBlock0) #
    cam.LogicBlockLUTSelector.SetValue(PySpin.LogicBlockLUTSelector_Enable) #
    cam.LogicBlockLUTOutputValueAll.SetValue(0xAF)

    cam.LogicBlockLUTInputSelector.SetValue(PySpin.LogicBlockLUTInputSelector_Input0) # 
    cam.LogicBlockLUTInputSource.SetValue(PySpin.LogicBlockLUTInputSource_Line3) #
    cam.LogicBlockLUTInputActivation.SetValue(PySpin.LogicBlockLUTInputActivation_RisingEdge) #

    cam.LogicBlockLUTInputSelector.SetValue(PySpin.LogicBlockLUTInputSelector_Input1) # 
    cam.LogicBlockLUTInputSource.SetValue(PySpin.LogicBlockLUTInputSource_LogicBlock0) #
    cam.LogicBlockLUTInputActivation.SetValue(PySpin.LogicBlockLUTInputActivation_LevelHigh) #

    cam.LogicBlockLUTInputSelector.SetValue(PySpin.LogicBlockLUTInputSelector_Input2) #
    cam.LogicBlockLUTInputSource.SetValue(PySpin.LogicBlockLUTInputSource_UserOutput0) #
    cam.LogicBlockLUTInputActivation.SetValue(PySpin.LogicBlockLUTInputActivation_LevelHigh) #

    cam.LogicBlockLUTSelector.SetValue(PySpin.LogicBlockLUTSelector_Value) #
    cam.LogicBlockLUTOutputValueAll.SetValue(0x20)
    
def configureCounter(cam): #+++

    period = round(1/params.frameRate * 1e6)

    # set counter0 to run for the period (the inverse of the frame rate specified in params, adjusted to the MHz tick)
    # the counter will start from zero again once it reaches the period. Each time it reaches the period it will trigger the primary camera
    cam.CounterSelector.SetIntValue(PySpin.CounterSelector_Counter0)
    cam.CounterDuration.SetValue(period)

    # update the counter with each MHz tick
    cam.CounterEventSource.SetValue(PySpin.CounterEventSource_MHzTick)

    # set counter to start when LogicBlock0 outputs a LevelHigh pulse
    cam.CounterTriggerSource.SetValue(PySpin.CounterTriggerSource_LogicBlock0)
    cam.CounterTriggerActivation.SetIntValue(PySpin.CounterTriggerActivation_LevelHigh)
    
def configure_image_settings(cam, crop):
    try:
        result = True   

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

def acquire_images(cams): #+++
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
            
            # this has something to do with the logic block, but idk what exactly
            cam.UserOutputSelector.SetIntValue(PySpin.UserOutputSelector_UserOutput0)
            cam.UserOutputValue.SetValue(True)

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
            # cam.CounterSelector.SetIntValue(PySpin.CounterSelector_Counter1)
            # count = cam.CounterValue() - 1
            
            timestamp_nanoSec = image_result.GetTimeStamp() 
            timestamps.append(timestamp_nanoSec * 1e-9)
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

            print('\n Cam %d     Event = %d     frame = %d, latency = %d' % (cam_num, eventNum, frameNum, round(latency*1e3)))

            # Create a unique filename
            image_folder = filename.image_folder
  
            image_filename = '%s/jpg_cam%d/%s_%s_%s_session_%d_cam%d_event_%s_frame_%s_currentTime_%d_%s.jpg' % (image_folder, 
                                                                                                                 cam_num, 
                                                                                                                 filename.marms, 
                                                                                                                 filename.date, 
                                                                                                                 filename.expName, 
                                                                                                                 filename.session, 
                                                                                                                 cam_num, 
                                                                                                                 "{:03}".format(int(eventNum)), 
                                                                                                                 "{:07d}".format(int(frameNum)),
                                                                                                                 round(timestamp_nanoSec), 
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
        # secondaryCams = cams[1:]
        
        # Initialize camera
        for cam in cams:
            cam.Init()
            exposure(cam)
           
        for cam, crop in zip(cams, params.crop_by_cam):
            configure_image_settings(cam, crop)
        
        configureCounter(primaryCam) 
        configureLogicBlock(primaryCam)
        configure_single_cam_trigger_and_output(primaryCam)

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

    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    for cam_num in range(0, params.nCams): 
        image_folder = filename.image_folder

        file_path = '%s/jpg_cam%d' %(image_folder, cam_num+1)
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

    cams = [cam1]
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
     	help="session number")

    args = vars(ap.parse_args())
    
    class filename: 
        expName = args['exp_name']
        marms = args['marms'] 
        session = args['session']
        date = time.strftime('%Y_%m_%d')
        if type(session) == str: 
            image_folder = '/media/marmosets/fast1/%s/%s/%s/%s'  %(expName, marms, date, session)
        else:
            image_folder = '/media/marmosets/fast1/%s/%s/%s/session%d' %(expName, marms, date, session)
    
    main()
