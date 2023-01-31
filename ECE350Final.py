#Author: Anthony Tang
#Due Date: May 3, 2021
#Description: ECE 350 Final

import RPi.GPIO as GPIO #setting mode to BCM, for GPIO pin naming conventions
import time #imports time library
from time import sleep #this one imports specifically sleep, which apparently I needed to so for some reason

LEDR = 20	# pin38/GPIO20 --- LED Red
LEDB = 16	# pin36/GPIO16 --- LED Blue
LEDY = 12	# pin32/GPIO12 --- LED Yellow
LEDG = 26	# pin37/GPIO26 --- LED Green
BTN = 21    # pin40/GPIO21 --- button

#given Adafruit code, which controls the lcd display
class Adafruit_CharLCD:

    # commands
    LCD_CLEARDISPLAY 		= 0x01
    LCD_RETURNHOME 			= 0x02
    LCD_ENTRYMODESET 		= 0x04
    LCD_DISPLAYCONTROL 		= 0x08
    LCD_CURSORSHIFT 		= 0x10
    LCD_FUNCTIONSET 		= 0x20
    LCD_SETCGRAMADDR 		= 0x40
    LCD_SETDDRAMADDR 		= 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT 				= 0x00
    LCD_ENTRYLEFT 				= 0x02
    LCD_ENTRYSHIFTINCREMENT 	= 0x01
    LCD_ENTRYSHIFTDECREMENT 	= 0x00

    # flags for display on/off control
    LCD_DISPLAYON 		= 0x04
    LCD_DISPLAYOFF 		= 0x00
    LCD_CURSORON 		= 0x02
    LCD_CURSOROFF 		= 0x00
    LCD_BLINKON 		= 0x01
    LCD_BLINKOFF 		= 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE 	= 0x08
    LCD_CURSORMOVE 		= 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE 	= 0x08
    LCD_CURSORMOVE 		= 0x00
    LCD_MOVERIGHT 		= 0x04
    LCD_MOVELEFT 		= 0x00

    # flags for function set
    LCD_8BITMODE 		= 0x10
    LCD_4BITMODE 		= 0x00
    LCD_2LINE 			= 0x08
    LCD_1LINE 			= 0x00
    LCD_5x10DOTS 		= 0x04
    LCD_5x8DOTS 		= 0x00



    def __init__(self, pin_rs=24, pin_e=23, pins_db=[17, 18, 27, 22], GPIO = None):
	# Emulate the old behavior of using RPi.GPIO if we haven't been given
	# an explicit GPIO interface to use
	if not GPIO:
	    import RPi.GPIO as GPIO
   	self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        self.GPIO.setwarnings(False)
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)

        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)

	self.write4bits(0x33) # initialization
	self.write4bits(0x32) # initialization
	self.write4bits(0x28) # 2 line 5x7 matrix
	self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
	self.write4bits(0x06) # shift cursor right

	self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

	self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
	self.displayfunction |= self.LCD_2LINE

	""" Initialize to default text direction (for romance languages) """
	self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
	self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode

        self.clear()


    def begin(self, cols, lines):

	if (lines > 1):
		self.numlines = lines
    		self.displayfunction |= self.LCD_2LINE
		self.currline = 0


    def home(self): #returns cursor back to first row, first column

	self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
	self.delayMicroseconds(3000) # this command takes a long time!
	

    def clear(self): #clears the lcd, this one is used in my code lcd.clear

	self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
	self.delayMicroseconds(3000)	# 3000 microsecond sleep, clearing the display takes a long time


    def setCursor(self, col, row): #move cursor to a specific row, column

	self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

	if ( row > self.numlines ): 
		row = self.numlines - 1 # we count rows starting w/0

	self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))


    def noDisplay(self):  #turn off lcd display
	""" Turn the display off (quickly) """

	self.displaycontrol &= ~self.LCD_DISPLAYON
	self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def display(self): #turn lcd display on
	""" Turn the display on (quickly) """

	self.displaycontrol |= self.LCD_DISPLAYON
	self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noCursor(self):
	""" Turns the underline cursor on/off """

	self.displaycontrol &= ~self.LCD_CURSORON
	self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self): #displays cursor
	""" Cursor On """

	self.displaycontrol |= self.LCD_CURSORON
	self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self): #sets blinking cursor on/off
	""" Turn on and off the blinking cursor """

	self.displaycontrol &= ~self.LCD_BLINKON
	self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self): #sets blinking cursor on/off
	""" Turn on and off the blinking cursor """

	self.displaycontrol &= ~self.LCD_BLINKON
	self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def DisplayLeft(self): #allows for scrolling the lcd display 
	""" These commands scroll the display without changing the RAM """

	self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)


    def scrollDisplayRight(self): #allows for scrolling the lcd display 
	""" These commands scroll the display without changing the RAM """

	self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);


    def leftToRight(self): #allows text ot appear from left to right
	""" This is for text that flows Left to Right """

	self.displaymode |= self.LCD_ENTRYLEFT
	self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);


    def rightToLeft(self): #allows text ot appear from right to left
	""" This is for text that flows Right to Left """
	self.displaymode &= ~self.LCD_ENTRYLEFT
	self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def autoscroll(self):
	""" This will 'right justify' text from the cursor """

	self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
	self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def noAutoscroll(self): 
	""" This will 'left justify' text from the cursor """

	self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
	self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def write4bits(self, bits, char_mode=False): #takes commands and sends to lcd to display
        """ Send command to LCD """

	self.delayMicroseconds(1000) # 1000 microsecond sleep

        bits=bin(bits)[2:].zfill(8)

        self.GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)

	self.pulseEnable()

        for pin in self.pins_db:
            self.GPIO.output(pin, False)

        for i in range(4,8):
            if bits[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i-4], True)

	self.pulseEnable()


    def delayMicroseconds(self, microseconds): #function to delay my microseconds
	seconds = microseconds / float(1000000)	# divide microseconds by 1 million for seconds
	sleep(seconds)


    def pulseEnable(self): #write the 4 lower bits.
	self.GPIO.output(self.pin_e, False)
	self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
	self.GPIO.output(self.pin_e, True)
	self.delayMicroseconds(1)		# 1 microsecond pause - enable pulse must be > 450ns 
	self.GPIO.output(self.pin_e, False)
	self.delayMicroseconds(1)		# commands need > 37us to settle


    def message(self, text): #takes tring and displays to lcd
        """ Send string to LCD. Newline wraps to second line"""

        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line
            else:
                self.write4bits(ord(char),True)

#global variables
lcd = Adafruit_CharLCD() #variable lcd refers to the class Adafruit_CharLCD above, for LCD display 
status = 1 #status variable


def setup(): #setup function
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by BCM values
	GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BTN's mode is input, and pull up to high level
	
	GPIO.setup(25,GPIO.OUT,initial=GPIO.LOW) #pin setup for ultrasonic sensor
	GPIO.setup(8,GPIO.IN)
	
	GPIO.setup(LEDR, GPIO.OUT) #setting up GPIO pins for LEDs
	GPIO.setup(LEDB, GPIO.OUT)
	GPIO.setup(LEDY, GPIO.OUT)
	GPIO.setup(LEDG, GPIO.OUT)


def swLCD(ev=None): #function call on button press to switch output of LCD
	global status
	status = not status #with the button press, switch status
	#switching value of status switches between the if else stament below
	if status == 1:
		lcd.clear() #when button off, clear screen
		print("lcd off") #testing purose
	else:
		while True:
			lcd.clear()
			#when button pressed on, display message
			#lcd.message("  Anthony Tang \nECE 350 Final")
			D = round(checkdist(),2) #use checkdist formula to detemine distance from sensor
			lcd.message("Distance:" + str(D) + " m") #print distance on LCD bar for user to see
			print("lcd on") #testing purposes
			#if object within 0.5 meters, turn on LEDs to warn user
			if (D < 0.5):
				GPIO.output(LEDR, False)
				GPIO.output(LEDB, False)
				GPIO.output(LEDY, False)
				GPIO.output(LEDG, False)
			else:
				GPIO.output(LEDR, True)
				GPIO.output(LEDB, True)
				GPIO.output(LEDY, True)
				GPIO.output(LEDG, True)
			sleep(0.2) #sleep to help lcd.message
		
		
def checkdist(): #formula to determine distance from Ultrasonic distance sensor
	GPIO.output(25, GPIO.HIGH) #prep output pins
	time.sleep(0.000015)
	GPIO.output(25, GPIO.LOW)
	while not GPIO.input(8):
		pass
	#t1 and t2 refer to the time a signal is sent out and sign takes to come back
	#with this the sensor uses the formula in the return command to get the distance from the sensor
	t1 = time.time()
	while GPIO.input(8):
		pass
	t2 = time.time()
	return (t2-t1)*340/2

def loop():
	GPIO.add_event_detect(BTN, GPIO.FALLING, callback=swLCD) # waits for button to be pressed, calls swLCD when pressed
	while True:
		pass   # Don't do anything

def destroy(): #used in except path of try/except loop when calling loop()
	GPIO.cleanup()   # Release resource
	
if __name__ == '__main__':     # Program start from here
	setup()
	lcd.clear()
	#turn off all LEDs at start
	GPIO.output(LEDR, True)
	GPIO.output(LEDB, True)
	GPIO.output(LEDY, True)
	GPIO.output(LEDG, True)
	#D = round(checkdist(),2)
	try:
		#print("lcd off") testing purposes
		loop() #call loop for check for button press
	except KeyboardInterrupt:  # except needed for try
		destroy()

