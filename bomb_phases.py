#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: 
#################################

import random
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
        self._lkeypad = Label(self, bg="black", fg="#ff0000", font=("Courier New", 18), text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        # the jumper wires status, updated to reflect riddles
        self._lwires = Label(self, bg="black", fg="#ff0000", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        # the pushbutton status
        self._lbutton = Label(self, bg="black", fg="#ff0000", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        # the toggle switches status
        self._ltoggles = Label(self, bg="black", fg="#ff0000", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        # the strikes left
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)
        if (SHOW_BUTTONS):
            # the pause button (pauses the timer)
            self._bpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Pause", anchor=CENTER, command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            # the quit button
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button

    # pauses the timer
    def pause(self):
        if (RPi):
            self._timer.pause()

    # setup the conclusion GUI (explosion/defusion)
    def conclusion(self, exploding=False, success=False):
        while (not exploding and pygame.mixer.music.get_busy()):
            sleep(0.1)
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
            self._bquit.destroy()

# reconfigure the GUI for end results
def conclusion(self, success=False):
    # Play the appropriate sound and display the appropriate image based on success or failure
    image_path = SUCCESS[0] if success else EXPLODE[0]
    audio_path = SUCCESS[1] if success else EXPLODE[1]
    image = PhotoImage(file=image_path)
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    # Update the GUI to show the result image
    self._lscroll.configure(image=image)
    self._lscroll.image = image  # Keep a reference to prevent garbage collection
    self._lscroll.grid(row=0, column=0, columnspan=3, sticky=EW)

    # Show retry and quit buttons
    self._bretry = tkinter.Button(self, bg="green", fg="white", font=("Courier New", 18), text="Retry", command=self.retry)
    self._bretry.grid(row=1, column=0, pady=40)
    self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", command=self.quit)
    self._bquit.grid(row=1, column=2, pady=40)

def retry(self):
    # Restart the program
    os.execv(sys.executable, ['python'] + sys.argv)

def quit(self):
    if (RPi):
        # Reset hardware components
        self._timer._running = False
        self._timer._component.blink_rate = 0
        self._timer._component.fill(0)
        for pin in self._button._rgb:
            pin.value = True
    exit(0)

class PhaseThread(Thread):
    def __init__(self, gui, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        self.gui = gui
        self._component = component
        self._target = target
        self._defused = False
        self._failed = False
        self._value = None
        self._running = False

class NumericPhase(PhaseThread):
    def __init__(self, name, component, target, display_length=0):
        super().__init__(name, component, target)
        self._display_length = display_length
        self._prev_value = self._get_int_state()

    def run(self):
        self._running = True
        while self._running:
            current_value = self._get_int_state()
            if current_value == self._target:
                self._defused = True
                self._running = False
            elif current_value != self._prev_value:
                if not self._validate_state():
                    self._failed = True
                self._prev_value = current_value
            sleep(0.1)

    def _validate_state(self):
        current_states = self._get_bool_state()
        valid_states = [bool(int(bit)) for bit in bin(self._target)[2:].zfill(self._display_length)]
        return all(cs == vs for cs, vs in zip(current_states, valid_states))

    def _get_int_state(self):
        bool_states = self._get_bool_state()
        return int(''.join(str(int(state)) for state in bool_states), 2)

    def __str__(self):
        current_binary = bin(self._value)[2:].zfill(self._display_length)
        return f"Current: {current_binary} / Target: {bin(self._target)[2:].zfill(self._display_length)}"

# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        self._value = initial_value
        self._paused = False
        self._min = ""
        self._sec = ""
        self._interval = 1

    def run(self):
        self._running = True
        while self._running:
            if not self._paused:
                self._update()
                self._component.print(str(self))
                sleep(self._interval)
                if self._value == 0:
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)

    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    def pause(self):
        self._paused = not self._paused
        self._component.blink_rate = 2 if self._paused else 0

    def __str__(self):
        return f"{self._min}:{self._sec}"

# the keypad phase with sequence recall
class Keypad(PhaseThread):
    def __init__(self, gui, component, target, name="Keypad"):
        super().__init__(gui, name, component, target)
        self._value = ""

    def run(self):
        self._running = True
        while self._running:
            pressed_keys = self._component.pressed_keys  # Simulated method to read keys
            if pressed_keys:
                # Simplifying key processing, assuming pressed_keys provides the currently pressed key
                key = pressed_keys[0]  # Taking the first key pressed
                self._value += str(key)  # Append the pressed key to the value
                # Update the GUI with the current input
                self.gui.display_keypad_challenge(f"Enter sequence: {self._value}")
                # Check if the entered sequence matches the target
                if self._value == self._target:
                    self._defused = True
                    self._running = False  # Stop the thread if defused
                elif not self._target.startswith(self._value):
                    self._failed = True  # Incorrect sequence
                    self.reset_phase()  # Reset for a new attempt
            sleep(0.1)  # Small delay to simulate time between key presses

    def reset_phase(self):
        # Reset the keypad input and inform the user
        self._value = ""
        self._failed = False
        self.gui.display_keypad_challenge("Try again: Enter sequence")

    def __str__(self):
        # String representation based on the defusal status
        return "DEFUSED" if self._defused else self._value


# the jumper wires phase
class Wires(NumericPhase):
    def __init__(self, component, target, display_length, name="Wires"):
        super().__init__(name, component, target, display_length)

    # returns the jumper wires state as a string
    def __str__(self):
        if self._defused:
            return "DEFUSED"
        else:
            # Display wires state as letters A to E, where '.' represents an uncut wire
            return "".join([chr(int(i)+65) if pin.value else "." for i, pin in enumerate(self._component)])

# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        self._value = False
        self._pressed = False
        self._rgb = component_rgb
        self._color = color
        self._timer = timer

    def run(self):
        self._running = True
        # Set the RGB LED color based on the button color
        self._rgb[0].value = self._color == "R"
        self._rgb[1].value = self._color == "G"
        self._rgb[2].value = self._color == "B"
        while self._running:
            self._value = self._component.value
            if self._value:
                self._pressed = True
            else:
                if self._pressed:
                    # Check if the correct timing conditions are met
                    if not self._target or self._target in self._timer._sec:
                        self._defused = True
                    else:
                        self._failed = True
                    self._pressed = False
            sleep(0.1)

    def __str__(self):
        return "DEFUSED" if self._defused else ("Pressed" if self._value else "Released")

# the toggle switches phase
class Toggles(NumericPhase):
    def __init__(self, component, target, display_length, name="Toggles"):
        super().__init__(name, component, target, display_length)

    def run(self):
        self._running = True
        while self._running:
            self._value = self._get_int_state()
            if self._value == self._target:
                self._defused = True
                self._running = False
            elif self._value != self._prev_value:
                if not self._check_state():
                    self._failed = True
                self._prev_value = self._value
            sleep(0.1)

    # Override the check_state method if needed or keep it from the superclass
    def __str__(self):
        return "DEFUSED" if self._defused else f"{bin(self._value)[2:].zfill(self._display_length)}/{self._value}"