# couch_bot
The newest iteration (Fall 2022)

Setup Instructions:
1. Create a RPi 32 bit image within an micro SD card
	* set the username and password using the RPi Imager application
2. Paste the file `ssh` and `wpa_supplicant.conf` into the boot folder
	* edit `wpa_supplicant.conf`
3. Add `enable_uart=1` to `config.txt`
4. ssh into the RPi
5. Run commands:
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install python3-pip
``` 
6. Clone the github respository into the RPi
7. Install dependencies:
```
$ pip3 install -r ~/couch_bot/requirements.txt
```
8. Change the requirements for the Logitech Controller port:
```
$ sudo chmod 666 /dev/ttyS0
```
9. Run the script:
```
$ python3 ~/couch_bot/couch_bot.py
```

Todo:
1. Documentation
1. Have couch_bot.py start on boot
1. Fix the frame
1. Make the joystick functions in classes/couch_bot.py generic instead of using the Logitech controller values to compute math
1. Avoid running into walls
1. Add code for neopixels

