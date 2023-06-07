# TODO: Save the data of the game to the onboard flash whenever it is bein charged
# Optional TODO: Add the clock

import adafruit_pcd8544
import board,busio,digitalio
import math
import analogio
import microcontroller
import time
import supervisor

epoch = time.time()
last_time = epoch # Update this to keep track of how much time has passed

# Define NOKIA 5110 SPI pins
mosi_pin = board.GP11
clk_pin = board.GP10
#backlight_pin = board.GP??

# Define control switches 
switch0 = digitalio.DigitalInOut(board.GP2)
switch1 = digitalio.DigitalInOut(board.GP3)
switch2 = digitalio.DigitalInOut(board.GP5)
switch3 = digitalio.DigitalInOut(board.GP4)

# Initialize control switch directions
switch0.direction = digitalio.Direction.INPUT
switch1.direction = digitalio.Direction.INPUT
switch2.direction = digitalio.Direction.INPUT
switch3.direction = digitalio.Direction.INPUT

# Initialize control switch pulls (didn't need those resistor after all lmao)
switch0.pull = digitalio.Pull.DOWN
switch1.pull = digitalio.Pull.DOWN
switch2.pull = digitalio.Pull.DOWN
switch3.pull = digitalio.Pull.DOWN

# Set the analog in for the battery level
battery_pin = analogio.AnalogIn(board.A0)

# PCD8544 SPI initialization
spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)
dc = digitalio.DigitalInOut(board.GP16) # data/command
cs = digitalio.DigitalInOut(board.GP18) # Chip select
reset = digitalio.DigitalInOut(board.GP17) # reset

# LCD setup
lcd = adafruit_pcd8544.PCD8544(spi, dc, cs, reset, baudrate=500000)
lcd.bias = 4
lcd.contrast = 40
lcd.rotation = 2

# LCD Screen specs
size = 700
width = 84
height = 48

# Battery level specs
maxvolt = 4.0
minvolt = 3.3
bv = (9 * minvolt - maxvolt)/(minvolt-maxvolt)
av = (9-bv)/maxvolt

# Charger plugged in input
#lipo_charger = digitalio.DigitalInOut(board.GP21)
#lipo_charger.direction = digitalio.Direction.INPUT
#lipo_charger.pull = digitalio.Pull.DOWN

# Backlight connection # Works
backlight_pin = digitalio.DigitalInOut(board.GP22)
backlight_pin.direction = digitalio.Direction.OUTPUT

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Test backlight 
backlight_pin.value = True

# Font specs
char_size = [5,8]
chg = char_size[0] # Character gap: give this much gap between characters

# Cursor variables for text input
global x_loc; x_loc = 0
global y_loc; y_loc = 0

# Game scores
global hunger_val; hunger_val = 4
global joy_val; joy_val = 8
global love_val; love_val = 9
# Get this value from the ADC showing the charge level of lipo
global energy_val; energy_val = 9

global energy_str; energy_str = 'R' 
# Energy state, default R: regular
# E: Battery error
# P: Plugged in

global day_val; day_val = 0 # How many days of continuous running

# Image file names
happy_imgs = ['img/hepi_0.bin', 'img/hepi_1.bin'] # When everything ok, default
tired_imgs= ['img/tired_0.bin', 'img/tired_1.bin'] # When battery low
hungry_imgs = ['img/hungy_0.bin', 'img/hungy_1.bin'] # When not fed enough
lonely_imgs = ['img/sad_0.bin', 'img/sad_1.bin'] # When not loved enough
sad_imgs = ['img/sad_0.bin', 'img/sad_1.bin'] # When not joyful enough
sleep_imgs = ['img/sleep_0.bin', 'img/sleep_1.bin'] # Sleep images for charging

# Animation file names
eating_imgs = ['img/nom_0.bin', 'img/nom_1.bin']
kiss_imgs = ['img/chu_0.bin', 'img/chu_1.bin']
hug_imgs = ['img/hug_0.bin', 'img/hug_1.bin'] # Need to prepare a hug image
headpat_imgs = ['img/headpat_0.bin', 'img/headpat_1.bin']

# Image swap counter for not changing the image every iteration
swp = 0

#def backlightSet(cyc = 0):
#    b_light = pwmio.PWMOut(backlight_pin, frequency = 120, duty_cycle = cyc)

def getEnergy():
    # 6.6 inst. of 3.3 because of voltage divider
    # Max voltage 4.2 Min voltage 3.3
    global energy_val
    battery_voltage = (battery_pin.value * 6.6)/65536 
    print("battery voltage: %f"%battery_voltage)
    energy_val = av * battery_voltage + bv
    if energy_val > 9: energy_val = 9; # Plugged in
    elif energy_val < 1: energy_val = 1; # Battery error
    #if lipo_charger == True: energy_str = 'P'; #######################
    #else: energy_str = 'R';

def writeScr():
    global x_loc; x_loc=0;
    global y_loc; y_loc=0;
    global width;
    margin = 4

    getEnergy() # Update energy_val

    scoreVal = ( hunger_val, joy_val, love_val ) # Integer scores
    scoreChar = ['H','J','L','E']
    x_loc = margin
    
    # Create a tuple with all the scores that will be displayed,
    # depending on the energy state string either display the value
    # or the text describing the state

    if energy_str != 'R':
        scoreTup = scoreVal + (energy_str,) 
    else:
        scoreTup = scoreVal + (energy_val,)

    for i in range(0,4):
        valStr = '{}'.format(scoreTup[i])
        lcd.text(scoreChar[i], x_loc, y_loc, 1)
        x_loc += chg-1
        lcd.text(':', x_loc, y_loc, 1)
        x_loc += chg-1
        lcd.text(valStr, x_loc, y_loc, 1)
        x_loc = (i+1)*math.floor((width+1)/4)+margin

    # One score takes 5+ in height
    y_loc = char_size[1];
    lcd.line(0,y_loc,width-1,y_loc,1)

    # Show the time

def drawImg(imgName):
    global width;
    global height;
    global x_loc;
    global y_loc;
    
    with open(imgName, "rb") as bin_file:
        bin_content = bin_file.read()
        bin_array = bytearray(bin_content)
        for binc in range(0,len(bin_array)):
            if not bin_array[binc]:
                lcd.pixel(x_loc, y_loc, 1)
            x_loc = binc % width
            y_loc = math.floor(binc/width)

def drawAnimation(disp_anim):
    # The animation loop, show two images swapping between them to create 
    # the animations
    animation_length = 1 # Seconds
    frame_length = 0.25 # Seconds
    for cnt in range(0, math.floor(animation_length/frame_length)):
        lcd.fill(0) # Clear screen
        drawImg("img/bg.bin")
        print("In animation loop")
        print("{}".format(disp_anim[cnt % 2]))
        drawImg(disp_anim[cnt % 2]) # Swap between the two images
        time.sleep(frame_length) # Wait as long as the frame length
        writeScr() # Write the scores to the top of the screen
        lcd.show() # Write everything to screen

def drawScene():
    global swp # Keep swp in track in the global namespace
    global hunger_val; global joy_val; global love_val; global energy_val;

    lcd.fill(0) # Clear screen
    drawImg("img/bg.bin")

    score_dict = { # Dictionary for sorting and getting the key of the lowest value
            "hungry": hunger_val,
            "sad": joy_val,
            "lonely": love_val,
            "tired": energy_val
            }
    
    if energy_str == 'P': # If plugged in show the sleep images !!! Revert this after developing it
        imglist = sleep_imgs

    else:
        sorted_scores = sorted(score_dict.items(), key=lambda x:x[1]) # Sort scores
        print(sorted_scores)
        smallest_key = next(iter(sorted_scores))[0] # First key in dict

        # If all of them bigger than 6
        if score_dict[str(smallest_key)] > 6:
            imglist = happy_imgs

        # If the smallest is less than 6 display the appropriate image
        else:
            if smallest_key == 'hungry': imglist = hungry_imgs;
            elif smallest_key == 'sad': imglist = sad_imgs;
            elif smallest_key == 'lonely': imglist = lonely_imgs;
            else: imglist = tired_imgs;

    swp = (swp+0.2) % 2 # Slow down the image swap time
    drawImg(str(imglist[math.floor(swp)]))
    writeScr() # Write the scores to the top of the screen
    lcd.show() # Write everything to screen

def bFeed():
    pass

def condInc(valScore, amnt = 1, incOrDec = True):
    # Conditionally increase or decrease
    # If incOrDec is true increase, else decrease by amp amount
    if incOrDec:
        valScore += amnt
        if valScore > 9: valScore = 9;
    else:
        valScore -= amnt
        if valScore < 1: valScore = 1;
    return valScore

while True:

    for switch_loop in range(0,10):
        if switch0.value: # Feed
            # Increases the food score but decreases joy
            if switch3.value:
                if switch1.value and switch2.value:
                    # Reset if all buttons are pressed
                    supervisor.reload()
                else:
                    # Toggle sleep
                    if energy_str == 'R': energy_str = 'P';
                    else: energy_str = 'R';
                    time.sleep(0.5)
            elif switch2.value:
                # Toggle backlight
                if backlight_pin.value == True: backlight_pin.value = False;
                else: backlight_pin.value = True;
                time.sleep(0.5)
            else:
                drawAnimation(eating_imgs)
                hunger_val = condInc(hunger_val, 2, True)
                joy_val = condInc(joy_val, 1, False)

        elif switch1.value: # Kiss
            # Increases love by 1
            drawAnimation(kiss_imgs)
            love_val = condInc(love_val, 1, True)

        elif switch2.value: # Hug
            # Increase joy and love by 1 but decreases food score
            drawAnimation(hug_imgs)
            love_val = condInc(love_val, 1, True)
            joy_val = condInc(joy_val, 1, True)
            hunger_val = condInc(hunger_val, 1, False)

        elif switch3.value: # Headpat
            # Increases the joy by 1 but decreases love
            drawAnimation(headpat_imgs)
            joy_val = condInc(joy_val, 2, True)
            love_val = condInc(love_val, 1, False)

    if energy_str == 'R':
        if ( time.time() - last_time > 3600 ):
            # If an hour has past, decrease the scores
            hunger_val = condInc(hunger_val, 2, False)
            joy_val = condInc(joy_val, 1, False)
            love_val = condInc(love_val, 1, False)
            last_time = time.time() # Update the last decrement time
            time.sleep(1)

    drawScene()
