######################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
######################################

# import the configs
from bomb_configs import *
# other imports
from tkinter import *
import tkinter
from threading import Thread
import pygame
from time import sleep
import os
import sys

#########
# classes
#########

# the LCD display GUI
class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        # make the GUI fullscreen
        window.attributes("-fullscreen", True)
        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        self._hint = False
        # setup the initial "boot" GUI
        self.setupBoot()

    # sets up the LCD "boot" GUI
    def setupBoot(self):
        # set column weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        # the scrolling informative "boot" text
        self._lscroll = Label(self, bg="black", fg="white", font=("Courier New", 14), text="", justify=LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=W)
        self.pack(fill=BOTH, expand=True)

    # sets up the LCD GUI
    def setup(self):
        # the timer
        self._ltimer = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=W)
        # the keypad passphrase
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        # the jumper wires status
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        # the pushbutton status
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        # the toggle switches status
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        # the strikes left
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)
        if (SHOW_BUTTONS):
            # the pause button (pauses the timer)
            self._bpause = tkinter.Button(self, bg="green", fg="white", font=("Courier New", 18), text="Pause", anchor=CENTER, command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            # the hint button (defuses a random phase and reduces strikes left by 2)
            self._bhint = tkinter.Button(self, bg="yellow", fg="black", font=("Courier New", 18), text="Hint", anchor=CENTER, command=self.hint)
            self._bhint.grid(row=6, column=1, pady=40)
            # the quit button
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button
       
    # hint button method
    def hint(self):
        self._hint = True

    # pauses the timer
    def pause(self):
        if (RPi):
            self._timer.pause()

    # setup the conclusion GUI (explosion/defusion)
    def conclusion(self, success=False):
        # destroy/clear widgets that are no longer needed
        self._lscroll["text"] = ""
        self._ltimer.destroy()
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()
        if (SHOW_BUTTONS):
            self._bpause.destroy()
            self._bhint.destroy()
            self._bquit.destroy()
       
        # Reconfigure the GUI for retry or quit
        self.add_quit_retry_buttons(success)

    def add_quit_retry_buttons(self, success):
        # add the quit and retry buttons
        self._bretry = tkinter.Button(self, bg="green", fg="white", font=("Courier New", 18), text="Retry", anchor=CENTER, command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)
        self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
        self._bquit.grid(row=1, column=2, pady=40)

        # Display the result image and play sound
        if success:
            image_file = os.path.join(os.getcwd(), "success.gif")
            sound_file = os.path.join(os.getcwd(), "success.mp3")
        else:
            image_file = os.path.join(os.getcwd(), "explosion.gif")
            sound_file = os.path.join(os.getcwd(), "explosion.mp3")
        self.display_animated_image(image_file, sound_file)

    # display an animated image using Tkinter's PhotoImage
    def display_animated_image(self, image_file, sound_file):
        # Load the image file directly with PhotoImage if it's a GIF
        animation_image = PhotoImage(file=image_file)

        # Create a frame to hold the animated image with a black background
        animation_frame = Frame(self, bg="black")
        animation_frame.grid(row=0, column=0, columnspan=3, sticky=EW)

        # Create a label to display the image
        animation_label = Label(animation_frame, image=animation_image, bg="black")
        animation_label.image = animation_image  # Keep a reference!
        animation_label.pack()

        # Initialize and play sound
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    # re-attempts the bomb (after an explosion or a successful defusion)
    def retry(self):
        # re-launch the program (and exit this one)
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)
   
    # quits the GUI, resetting some components
    def quit(self):
        if (RPi):
            # turn off the 7-segment display
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            # turn off the pushbutton's LED
            for pin in self._button._rgb:
                pin.value = True
        # exit the application
        exit(0)
        
    def display_riddle(self, riddle):
        # Method to display riddles on the LCD screen
        self._lscroll["text"] = riddle
        
    def display_keypad_challenge(self, message):
    # Display the current challenge or message on the keypad screen
        self._lscroll.config(text=message)
        
# template (superclass) for various bomb components/phases
class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        # phases have an electronic component (which usually represents the GPIO pins)
        self._component = component
        # phases have a target value (e.g., a specific combination on the keypad, the proper jumper wires to "cut", etc)
        self._target = target
        # phases can be successfully defused
        self._defused = False
        # phases can be failed (which result in a strike)
        self._failed = False
        # phases have a value (e.g., a pushbutton can be True/Pressed or False/Released, several jumper wires can be "cut"/False, etc)
        self._value = None
        # phase threads are either running or not
        self._running = False
       
# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # the default value is the specified initial value
        self._value = initial_value
        # is the timer paused?
        self._paused = False
        # initialize the timer's minutes/seconds representation
        self._min = ""
        self._sec = ""
        # by default, each tick is 1 second
        self._interval = 1
       
    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            if (not self._paused):
                # update the timer and display its value on the 7-segment display
                self._update()
                self._component.print(str(self))
                # wait 1s (default) and continue
                sleep(self._interval)
                # the timer has expired -> phase failed (explode)
                if (self._value == 0):
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)
               
    # updates the timer (only internally called)
    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)
       
    # pauses and unpauses the timer
    def pause(self):
        # toggle the paused state
        self._paused = not self._paused
        # blink the 7-segment display when paused
        self._component.blink_rate = (2 if self._paused else 0)
       
    # returns the timer as a string (mm:ss)
    def __str__(self):
        return f"{self._min}:{self._sec}"

# Keypad phase updated with Sequence Recall
class Keypad(PhaseThread):
    def __init__(self, component, name="Keypad"):
        super().__init__(name, component)
        self._letter_sequence = self.generate_letter_sequence()
        self._expected_input = self.letters_to_numbers(self._letter_sequence)
        self._current_input = ""
        gui.display_keypad_challenge("Enter sequence for: " + self._letter_sequence)

    def generate_letter_sequence(self):
        # Generate a random sequence of letters
        return ''.join(random.choice(ascii_uppercase) for _ in range(5))  # Example: "ABCED"

    def letters_to_numbers(self, letters):
        # Convert letters to the corresponding numbers on a phone keypad
        return ''.join(KEYPAD_LETTER_TO_NUMBER[letter] for letter in letters if letter in KEYPAD_LETTER_TO_NUMBER)

    def run(self):
        self._running = True
        while self._running:
            pressed_keys = self._component.get_pressed_keys()  # Method to read the keypad input
            if pressed_keys:
                for key in pressed_keys:
                    self._current_input += str(key)
                    gui.display_keypad_challenge(self._current_input)  # Update display with current input
                if self._current_input == self._expected_input:
                    self._defused = True
                    self._running = False
                elif len(self._current_input) >= len(self._expected_input):
                    self._failed = True
                    self.reset_phase()
            sleep(0.1)

    def reset_phase(self):
        self._current_input = ""
        self._failed = False
        gui.display_keypad_challenge("Try again: " + self._letter_sequence)


# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, name="Button"):
        super().__init__(name, component_state)
        # RGB component to display colors or binary codes
        self._rgb = component_rgb
        # Store binary codes as class attributes
        self.binary_code_1 = "0000"
        self.binary_code_2 = "0000"

    def run(self):
        # Main loop to manage button interactions
        while self._running:
            self.flash_binary_codes()  # Update and display binary codes periodically or based on some condition
            sleep(1)  # Sleep to simulate time between updates

    def flash_binary_codes(self):
        # Simulate binary code changes
        self.binary_code_1 = format(random.randint(0, 15), '04b')
        self.binary_code_2 = format(random.randint(0, 15), '04b')
        # Method to update the display with the new codes
        self.update_display(self.binary_code_1, self.binary_code_2)

    def update_display(self, code1, code2):
        # Update an LED display or GUI element with the binary codes
        # This part depends on your specific hardware setup
        print(f"Displaying code 1: {code1}, code 2: {code2}")
        # Example: Set RGB LEDs based on binary code
        # This is highly hardware-specific and needs actual implementation details

    def __str__(self):
        # Return current binary codes as string representation
        return f"Binary Code 1: {self.binary_code_1}, Binary Code 2: {self.binary_code_2}"

       
# the toggle phase
class Toggles(PhaseThread):
    def __init__(self, component, name="Toggles"):
        # Initialize the superclass with the thread name and the hardware component
        super().__init__(name, component, None)  # Target is dynamic, so it's set to None
        # Read the initial value of the toggle switches to manage state changes
        self._prev_value = self._get_value()

    def run(self):
        # Keep this thread running until stopped
        self._running = True
        while self._running:
            # Continuously read the current state of the toggles
            current_value = self._get_value()
            # Check current toggle state against dynamically set binary codes
            # These codes should be updated elsewhere in your program, e.g., by the Button class
            if current_value == int(binary_code_1, 2) or current_value == int(binary_code_2, 2):
                # If a match is found, mark the phase as defused and stop this thread
                self._defused = True
                self._running = False
            # Save the current state for comparison in the next loop iteration
            self._prev_value = current_value
            # Sleep to reduce CPU load and allow other processes to run
            sleep(0.1)

    def _get_value(self):
        # Convert the states of the toggle pins into a single binary integer
        value = [str(int(pin.value)) for pin in self._component]
        return int("".join(value), 2)

    def __str__(self):
        # Provide a string representation showing the current binary state of the toggles
        return f"Current Value: {bin(self._get_value())[2:].zfill(4)}"  # Adjust zfill for number of toggles
# Wires phase class modified to handle riddles
class Wires(PhaseThread):
    def __init__(self, component, name="Wires"):
        super().__init__(name, component, None)
        self._riddle, self._sequence = self.select_riddle()

    def select_riddle(self):
        # Select a random riddle and determine the corresponding wire sequence
        riddle = random.choice(list(WIRE_RIDDLES.keys()))
        sequence = WIRE_SEQUENCES[WIRE_RIDDLES[riddle]]
        return riddle, sequence

    def run(self):
        self._running = True
        gui.display_riddle(self._riddle)  # Display the riddle to the user
        user_sequence = []  # This list should be populated based on user interactions
        while self._running:
            if len(user_sequence) == len(self._sequence) and user_sequence == self._sequence:
                self._defused = True
                self._running = False
            sleep(0.1)
