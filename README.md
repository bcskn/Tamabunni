# Tamabunni
DIY Tamagotchi inspired handheld using Raspberry Pi Pico and Nokia 5110 LCD
Video: https://www.youtube.com/watch?v=bPAoemKU1jg

![image](https://github.com/bcskn/Tamabunni/assets/12624047/94cbbe6d-ea69-42c0-a663-095925e9cac2)

## Materials
1. Raspberry Pi Pico (Wireless version is not supported)
2. Nokia 5110 LCD (Their characteristics can change between different manufacturers so be careful)
3. Lipo charge circuit (
4. Lipo
5. 2-pin tact buttons  x4
6. 

## Case
I 3D printed the case but you can easily design a new one yourself as finding the exact components to fit the case might be harder than just making up a new one.
But I still recommend checking the 3D model to see how the parts go!

## Wiring
1. Directly soldering onto the LCD is not recommended they are easy to fry. Either get a header version or be careful while soldering and wait a bit for it too cool down between solders.
2. LCD backlight pin can be anode or cathode, for my version it was the anode but that is not always the case so keep that in mind.
3. Buttons are easy as you can pull them down in software instead of adding pull down resistors.

Check the schematic for details.

## Installing the game
1. Flash the Pico with Circuit Python
2. Copy the contents of src/ inside the Pico
3. Reset and you are done.

## Troubleshooting
1. Screen problems
  1.
  2.
