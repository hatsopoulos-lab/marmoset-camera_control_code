# marmoset-camera_control_code
camera control code for apparatus and enclosure camera sets

## Recording Session Checklist
1.	Check positions, plug in, or turn on:
	-	Exilis antennas and lightboxes, Surge protector and raspberryPi
    -	Enclosure, apparatus and sleep cameras - Ensure lens adjustment is “Open”
	-	Cerebus, Digital Hub, and Exilis Receiver

2.	Use `spinview` in terminal to check camera positions as needed
3.	Check that fast1/fast2/fast/storage drives on camera comps have plenty of available space

4.	Prepare Central recording
	-	Open Central
    -	Load configuration file from either the default location or a recent recording folder
	-	In Hardware Configuration, check that analog inputs 1-4 are enabled
    -	In File Storage, browse to the Data drive located at `E:\` and make a new folder 
    and filename of the form `MARMCODEYYYYMMDD_TIME_experiment1AndExperiment2`:
		-	Example 1: `TY20220731_1600_freeAndForaging\TY20220731_1600_freeAndForaging`
        -	Example 2: `TY20220823_2000_inHammock_night\ TY20220823_2000_inHammock_night`

	-	Set up spike panel and raster plot for easy viewing

5.	Prepare apparatus recording
	-	Open three terminals. In commands, replace `TYJL`, `2022_08_24`, `test`, `1` 
    with appropriate inputs.
	-	In terminal 1:
		-	`connect_to_rpi` OR `connect_to_rpi_backup`
        -	`sudo beamBreaker_gapFixed.py`  (`M+Enter` or `S+Enter` to toggle mode)
	-	In terminal 2:
		-	`conda activate cams`
		-	`record --marms TYJL --exp_name test --session 1`
		-	Check that cameras all begin acquiring data (should be cams 1-5)
	-	In terminal 3:
		-	`raw2jpg_recording   TYJL   2022_08_24   test   1` 

6.	Prepare enclosure recording
	-	In terminal 1:
		-	`conda activate cams`
		-	`record --marms TYJL --exp_name free --session 1`
		-	Check that cameras all begin acquiring data (should be cams 1-4)
	-	In terminal 2:
		-	`raw2jpg_recording   TYJL   2022_08_24   test   1` 
7.	Begin neural recording 
8.	Open blast gate and begin session
9.	At end of session, Ctrl+C twice to end recording on each computer’s camera terminal
10.	**AFTER** stopping cameras, end neural recording

## Camera Calibration

#### Apparatus

1.	Disconnect and reconnect cameras to reset settings

2.	In terminal 1, switch to manual trigger mode: `Enter + M` 

3.	In terminal 2: `calibrate --marms TYJL --exp_name test --session calib`

4.	Check that cameras all begin acquiring data (should be cams 1-5)

5.	In terminal 3, temporarily cancel raw2jpg conversion if running with `CTRL + C`

6.	Move enclosure out of the way of the calibration space. Hit `Enter` in terminal 1 to 
begin calibration. Move small board slowly through workspace, taking care to ensure 
board is fully seen by at least 2, preferably more cameras at all positions. 
After ~1 minute, you can hit Enter again to end calibration.

#### Enclosure

Repeat steps above:

-	Replace “test” with name of free behavior experiment
-	Move apparatus to acrylic platform. Secure with velcro. DO NOT UNPLUG cables.
Move enclosure out of visual range, then begin calibration. Use the large board 
mounted on cardboard. 

##Possible camera failures:

**Errors seen at top of terminal prior to trigger configuration outputs**

-	This means the cameras were not unplugged to reset. Do that now.

**Trigger does nothing to begin image acquisition**

-	The trigger cables might be loose or disconnected at the circuit board or 
    apparatus panel.

**Fewer then expected cameras are collecting data (e.g. apparatus cams 1-3 instead 
of 1-5).**

-	There is something wrong with the circuit board or the GPIO cable connections 
    at the circuit board or at the cameras.
    
**Event and/or frame numbers don’t match for the cameras**

-	If the offset/error seems stable, you can keep going. If the offset is constantly 
changing, end session. Check if fast drives are getting full. Give the computers a 
break for ~5 minutes, then start a new session.
-	If the problem persists, you may have to factory reset the SSD data drives, or in the worst case replace them.

**Cameras are intermittently unresponsive to Start/stop trigger**

-	All cameras must be plugged in to avoid voltage/current leak at circuit board.

## What to do after camera or session failures
1.	End camera recordings 

2.	End neural recording

3.	Unpug and replug camera USB cables at computer backs. 

4.	Change session number in the “record” and “raw2jpg_recording” commands
OR delete the session folder with faulty data if it is all bad. Make sure to remove data from 
all data drives on each computer (fast1/fast2 on app computer, fast/storage on enc computer)  

5.	Check that the session number of the neural recording has updated.
6.	Restart session

## End of Session

1.	Follow steps 9 and 10 of “Recording Session Checklist”

2.	Calibrate cameras if necessary, then unplug cameras

3.	Cancel `raw2jpg_recording` and restart as `raw2jpg_end` with the same arguments on 
both computers.

4.	On apparatus computer, in the raspberry pi terminal, run `sudo shutdown -h now`

5.	Wrap up anything left in Central, then run the Hardware Shutdown and Close option

6.	Turn off Cerebus, Digital Hub, and Exilis Receiver. Turn off lightboxes. Return antennas to proper storage positions.

7.	Once Pi turns off, click off the power toggle button to the Pi. Turn off Surge protector.

8.	When all images have been converted run the following with corrected input arguments 
on both camera computers (the arguments are `MarmsCode`, `Date`, `Experiment`, `CNET`). 
You will need to have an existing directory at on Midway3 at `/scratch/midway3/CNETID/kinematics_jpgs/EXPERIMENT/MARMSCODE`.

		tar_images HMMG 2023_06_22 sleep
		upload_images HMMG 2023_06_22 sleep daltonm
 
9.	After all data has transferred from camera computers, delete the local version of 
folders that were just transferred, then run the following in terminal (which variation to run depends on the computer - these are alias functions so they should autocomplete with the Tab button):

		clear_fast1_trash 
        clear_fast2_trash
        clear_fast_trash 
        clear_storage_trash 

	-	To view the alias functions: `vi ~/.bash_aliases`

## For a sleep recording

1.	Complete steps 1-4 of recording guide.
	-	All cameras should be plugged in. The sleep camera should be plugged into 
    the apparatus computer.
    
2.	Prepare sleep recording
	
	Open two terminals. In commands, replace `TYJL`, `2022_08_24`, `test`, `1` 
    with appropriate inputs.

	-	In terminal 1:
		-	`connect_to_rpi` OR `connect_to_rpi_backup`
		-	`sudo beamBreaker_gapFixed.py`  (`M+Enter` or `S+Enter` to toggle mode)
	-	In terminal 2:
		-	`conda activate cams`
		-	`sleep_record --marms TYJL --exp_name sleep --session 1`
		-	Check that camera 1 has begun acquiring data 
        
3.	Begin neural recording, then use manual toggle to begin camera recording.  
