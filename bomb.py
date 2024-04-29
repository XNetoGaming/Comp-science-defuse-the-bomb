#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team:
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    # if we're not animating (or we're at the end of the bootup text)
    if (not ANIMATE or n == len(boot_text)):
        # if we're not animating, render the entire text at once (and don't process \x00)
        if (not ANIMATE):
            gui._lscroll["text"] = boot_text.replace("\x00", "")
        # configure the remaining GUI widgets
        gui.setup()
        # setup the phase threads, execute them, and check their statuses
        if (RPi):
            gui.after(1000, setup_phases)
    # if we're animating
    else:
        # add the next character (but don't render \x00 since it specifies a longer pause)
        if (boot_text[n] != "\x00"):
            gui._lscroll["text"] += boot_text[n]

        # scroll the next character after a slight delay (\x00 is a longer delay)
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)

# Define a function to display GPIO pin information
def display_pin_config():
    print("GPIO Pin Configuration:")
    print("7-Segment Display Pins: SDA and SCL on I2C interface.")
    print("Keypad Rows Pins: " + ", ".join([str(pin.pin) for pin in keypad_rows]))
    print("Keypad Cols Pins: " + ", ".join([str(pin.pin) for pin in keypad_cols]))
    print("Jumper Wires Pins: " + ", ".join([str(pin.pin) for pin in component_wires]))
    print("Button State Pin: " + str(component_button_state.pin))
    print("Button RGB Pins: " + ", ".join([str(pin.pin) for pin in component_button_RGB]))
    print("Toggle Switches Pins: " + ", ".join([str(pin.pin) for pin in component_toggles]))
    
# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles
   
    # setup the timer thread
    timer = Timer(component_7seg, COUNTDOWN)
    # bind the 7-segment display to the LCD GUI so that it can be paused/unpaused from the GUI
    gui.setTimer(timer)
    # setup the keypad thread, now including the gui object
    keypad = Keypad(gui, component_keypad, keypad_target)
    # setup the jumper wires thread
    wires = Wires(component_wires, wires_target, 5)
    # setup the pushbutton thread
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    # bind the pushbutton to the LCD GUI so that its LED can be turned off when we quit
    gui.setButton(button)
    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target, 4)

    # start the phase threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()
   
    # play the tick audio
    pygame.mixer.music.load(TICK)
    pygame.mixer.music.play(-1)

    # check the phases
    gui.after(100, check_phases)


# checks the phase threads
def check_phases():
    global active_phases, exploding

    # restart the tick audio if needed
    if (not exploding and not pygame.mixer.music.get_busy()):
        pygame.mixer.music.load(TICK)
        pygame.mixer.music.play(-1)
       
    # check the timer
    if (timer._running):
        # update the GUI
        gui._ltimer["text"] = f"Time left: {timer}"
        # play the exploding audio at t-10s
        if (not exploding and timer._value <= 10):
            exploding = True
            component_7seg.blink_rate = 1
            pygame.mixer.music.load(EXPLODING)
            pygame.mixer.music.play(1)
        if (timer._value == 60):
            gui._ltimer["fg"] = "#ff0000"
    else:
        # the countdown has expired -> explode!
        turn_off()
        gui.after(100, gui.conclusion, True)
        # don't check any more phases
        return

    # check the keypad
    if (keypad._running):
        # update the GUI
        gui._lkeypad["text"] = f"Combination: {keypad}"
        # the phase is defused -> stop the thread
        if (keypad._defused):
            keypad._running = False
            gui._lkeypad["fg"] = "#00ff00"
            defused()
        # the phase has failed -> strike
        elif (keypad._failed):
            strike()
            keypad.reset_phase()

    # check the wires
    if (wires._running):
        # update the GUI
        gui._lwires["text"] = f"Wires: {wires}"
        # the phase is defused -> stop the thread
        if (wires._defused):
            wires._running = False
            gui._lwires["fg"] = "#00ff00"
            defused()
        # the phase has failed -> strike
        elif (wires._failed):
            strike()
            wires.reset_phase()

    # check the button
    if (button._running):
        # update the GUI
        gui._lbutton["text"] = f"Button: {button}"
        # the phase is defused -> stop the thread
        if (button._defused):
            button._running = False
            gui._lbutton["fg"] = "#00ff00"
            defused()
        # the phase has failed -> strike
        elif (button._failed):
            strike()
            button.reset_phase()

    # check the toggles
    if (toggles._running):
        # update the GUI
        gui._ltoggles["text"] = f"Toggles: {toggles}"
        # the phase is defused -> stop the thread
        if (toggles._defused):
            toggles._running = False
            gui._ltoggles["fg"] = "#00ff00"
            defused()
        # the phase has failed -> strike
        elif (toggles._failed):
            strike()
            toggles.reset_phase()

    # note the strikes on the GUI
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    # too many strikes -> explode!
    if (strikes_left == 0):
        turn_off()
        gui.after(1000, gui.conclusion, True)
        # stop checking phases
        return

    # check the phases again after a slight delay
    gui.after(100, check_phases)

# handles a strike
def strike():
    global strikes_left
   
    # note the strike
    strikes_left -= 1
    # play the strike audio
    pygame.mixer.music.load(STRIKE)
    pygame.mixer.music.play(1)

# handles when a phase is defused
def defused():
    global active_phases

    # note that the phase is defused
    active_phases -= 1
    # play the defused audio
    pygame.mixer.music.load(DEFUSED)
    pygame.mixer.music.play(1)

# turns off the bomb
def turn_off():
    # stop all threads
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    # turn off the 7-segment display
    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    # turn off the pushbutton's LED
    for pin in button._rgb:
        pin.value = True


######
# MAIN
######

# initialize pygame
pygame.init()

# initialize the LCD GUI
window = Tk()
gui = Lcd(window)

# initialize the bomb strikes, active phases (i.e., not yet defused), and if the bomb is exploding
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES
exploding = False

# "boot" the bomb
gui.after(1000, bootup)

# display the LCD GUI
window.mainloop()