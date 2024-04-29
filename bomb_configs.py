#################################
# CSC 102 Defuse the Bomb Project
# Configuration file
# Team: 
#################################

# constants
DEBUG = False        # debug mode?
RPi = True           # is this running on the RPi?
ANIMATE = True       # animate the LCD text?
SHOW_BUTTONS = False # show the Pause and Quit buttons on the main LCD GUI?
COUNTDOWN = 300      # the initial bomb countdown value (seconds)
NUM_STRIKES = 5      # the total strikes allowed before the bomb "explodes"
NUM_PHASES = 4       # the total number of initial active bomb phases

# Wire Riddles Configuration
WIRE_RIDDLES = {
    "From first to last, I describe a journey from seed to stone.": ['A', 'B', 'C', 'D', 'E'],
    "I start with the end of forever and end with the beginning of eternity.": ['E', 'D', 'C', 'B', 'A'],
    "Arrange me from the smallest to the largest: Mouse, Elephant, Rabbit, Cat, Dog.": ['A', 'E', 'C', 'B', 'D']
}

# Mapping of wire labels to actual GPIO pin settings or logical identifiers in the game
WIRE_CUT_SEQUENCE = {
    'A': 0,  
    'B': 1,  
    'C': 2,
    'D': 3,
    'E': 4
}

# Map letters to keypad numbers
KEYPAD_LETTER_TO_NUMBER = {
    'A': '2', 'B': '2', 'C': '2',
    'D': '3', 'E': '3', 'F': '3',
    'G': '4', 'H': '4', 'I': '4',
    'J': '5', 'K': '5', 'L': '5',
    'M': '6', 'N': '6', 'O': '6',
    'P': '7', 'Q': '7', 'R': '7', 'S': '7',
    'T': '8', 'U': '8', 'V': '8',
    'W': '9', 'X': '9', 'Y': '9', 'Z': '9'
}

# imports
from random import randint, shuffle, choice
from string import ascii_uppercase
if (RPi):
    import board
    from adafruit_ht16k33.segments import Seg7x4
    from digitalio import DigitalInOut, Direction, Pull
    from adafruit_matrixkeypad import Matrix_Keypad

#################################
# setup the electronic components
#################################
# 7-segment display
# 4 pins: 5V(+), GND(-), SDA, SCL
#         ----------7SEG---------
if (RPi):
    i2c = board.I2C()
    component_7seg = Seg7x4(i2c)
    # set the 7-segment display brightness (0 -> dimmest; 1 -> brightest)
    component_7seg.brightness = 0.5

# keypad
# 8 pins: 10, 9, 11, 5, 6, 13, 19, NA
#         -----------KEYPAD----------
if (RPi):
    # the pins
    keypad_cols = [DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
    keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
    # the keys
    keypad_keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))

    component_keypad = Matrix_Keypad(keypad_rows, keypad_cols, keypad_keys)

# jumper wires
# 10 pins: 14, 15, 18, 23, 24, 3V3, 3V3, 3V3, 3V3, 3V3
#          -------JUMP1------  ---------JUMP2---------
# the jumper wire pins
if (RPi):
    # the pins
    component_wires = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    for pin in component_wires:
        # pins are input and pulled down
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN

# pushbutton
# 6 pins: 4, 17, 27, 22, 3V3, 3V3
#         -BUT1- -BUT2-  --BUT3--
if (RPi):
    # the state pin (state pin is input and pulled down)
    component_button_state = DigitalInOut(board.D4)
    component_button_state.direction = Direction.INPUT
    component_button_state.pull = Pull.DOWN
    # the RGB pins
    component_button_RGB = [DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
    for pin in component_button_RGB:
        # RGB pins are output
        pin.direction = Direction.OUTPUT
        pin.value = True

# toggle switches
# 3x3 pins: 12, 16, 20, 21, 3V3, 3V3, 3V3, 3V3, GND, GND, GND, GND
#           -TOG1-  -TOG2-  --TOG3--  --TOG4--  --TOG5--  --TOG6--
if (RPi):
    # the pins
    component_toggles = [DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]
    for pin in component_toggles:
        # pins are input and pulled down
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN


###########
# functions
###########

# Generates a random riddle and its corresponding wire sequence for the wires phase
def select_riddle_and_sequence():
    # Dictionary mapping riddles to specific wire sequences
    riddle_to_sequence = {
        "From first to last, I describe a journey\nfrom seed to stone.": ['A', 'B', 'C', 'D', 'E'],
        "I start with the end of forever and end\nwith the beginning of eternity.": ['E', 'D', 'C', 'B', 'A'],
        "Arrange me from the smallest to the largest:\nMouse, Elephant, Rabbit, Cat, Dog.": ['A', 'E', 'C', 'B', 'D']
    }
    # Select a random riddle
    riddle = choice(list(riddle_to_sequence.keys()))
    # Get the sequence corresponding to the chosen riddle
    sequence = riddle_to_sequence[riddle]
    # Return both for use in the game
    return riddle, sequence

# This function maps riddle sequences to GPIO pin settings or logical identifiers
def map_sequence_to_pins(sequence):
    wire_mapping = {
        'A': component_wires[0],  # Assuming each letter corresponds to a specific GPIO pin
        'B': component_wires[1],
        'C': component_wires[2],
        'D': component_wires[3],
        'E': component_wires[4]
    }
    return [wire_mapping[wire] for wire in sequence]

# No longer need the serial number and keypad combination generators as they do not fit the current gameplay mechanics

# New function to set up game phases based on riddles and sequences
def setup_game_phases():
    riddle, sequence = select_riddle_and_sequence()
    mapped_pins = map_sequence_to_pins(sequence)
    # Use this information to set up game logic for wire cutting
    # Example pseudocode:
    # wire_phase.setup(riddle, mapped_pins)
    return riddle, mapped_pins

# You may place any additional needed functions here, such as those handling game logic or UI updates based on the riddle and wire interactions.

###############################
# generate the bomb's specifics
###############################

# No longer generating serial numbers or using them to determine game mechanics
# Instead, setting up riddles directly for the wire phase
riddle, wire_sequence = setup_game_phases()  # This uses the setup function defined previously

# Set up the keypad phase to challenge players based on sequence recall
# Generates a random sequence of letters and expects inputs corresponding to the keypad mapping
keypad_sequence = ''.join(choice(ascii_uppercase) for _ in range(5))  # E.g., "BDFHJ"
keypad_target = ''.join(KEYPAD_LETTER_TO_NUMBER.get(char, '') for char in keypad_sequence)

# Pushbutton color choice is randomized for visual feedback only (does not affect mechanics directly)
button_color = choice(["Red", "Green", "Blue"])
# Pushbutton functionality might involve displaying colors or patterns, not necessarily game logic

if (DEBUG):
    print(f"Wire Riddle: {riddle}")
    print(f"Wire Sequence to Cut: {wire_sequence}")
    print(f"Keypad Sequence: {keypad_sequence} -> Expected Input: {keypad_target}")
    print(f"Button Color: {button_color}")

# set the bomb's LCD bootup text
boot_text = "Booting...\n\x00\x00" \
            "*Kernel v3.1.4-159 loaded.\n" \
            "Initializing subsystems...\n\x00" \
            "*System model: 102BOMBv4.2\n" \
            "Setting challenges...\n\x00" \
            f"*Wire challenge: {riddle}\n" \
            f"*Key sequence: {' '.join(keypad_sequence)}\n" \
            "Rendering phases...\x00"