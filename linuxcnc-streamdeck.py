#!/usr/bin/env python

# Modifications to the Python Stream Deck Library example
# for LinuxCNC by
#   kent.vandervelden@gmail.com, 2021
#
# Original example can be found at 
#   https://github.com/abcminiuser/python-elgato-streamdeck
#
# This code is only for demonstration of the Stream Deck
# with LinuxCNC and should not be relied upon to
# safely operate a machine.

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

# Example script showing basic library usage - updating key images with new
# tiles generated at runtime, and responding to button state change events.

import os
import random
import threading
import time

from PIL import Image, ImageDraw, ImageFont, ImageOps
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
page_num = 0

import os
import time
 
write_path = "/tmp/pipe.in"
read_path = "/tmp/pipe.out"
 
wf = None
rf = None

brake_state_ = False


# Generates an image that is correctly sized to fit across all keys of a given
# StreamDeck.
def create_full_deck_sized_image(deck, key_spacing, image_filename):
    key_rows, key_cols = deck.key_layout()
    key_width, key_height = deck.key_image_format()['size']
    spacing_x, spacing_y = key_spacing

    # Compute total size of the full StreamDeck image, based on the number of
    # buttons along each axis. This doesn't take into account the spaces between
    # the buttons that are hidden by the bezel.
    key_width *= key_cols
    key_height *= key_rows

    # Compute the total number of extra non-visible pixels that are obscured by
    # the bezel of the StreamDeck.
    spacing_x *= key_cols - 1
    spacing_y *= key_rows - 1

    # Compute final full deck image size, based on the number of buttons and
    # obscured pixels.
    full_deck_image_size = (key_width + spacing_x, key_height + spacing_y)

    # Resize the image to suit the StreamDeck's full image size. We use the
    # helper function in Pillow's ImageOps module so that the image's aspect
    # ratio is preserved.
    image = Image.open(os.path.join(ASSETS_PATH, image_filename)).convert("RGBA")
    image = ImageOps.fit(image, full_deck_image_size, Image.LANCZOS)
    return image


# Crops out a key-sized image from a larger deck-sized image, at the location
# occupied by the given key index.
def crop_key_image_from_deck_sized_image(deck, image, key_spacing, key):
    key_rows, key_cols = deck.key_layout()
    key_width, key_height = deck.key_image_format()['size']
    spacing_x, spacing_y = key_spacing

    # Determine which row and column the requested key is located on.
    row = key // key_cols
    col = key % key_cols

    # Compute the starting X and Y offsets into the full size image that the
    # requested key should display.
    start_x = col * (key_width + spacing_x)
    start_y = row * (key_height + spacing_y)

    # Compute the region of the larger deck image that is occupied by the given
    # key, and crop out that segment of the full image.
    region = (start_x, start_y, start_x + key_width, start_y + key_height)
    segment = image.crop(region)

    # Create a new key-sized image, and paste in the cropped section of the
    # larger image.
    key_image = PILHelper.create_image(deck)
    key_image.paste(segment)

    return PILHelper.to_native_format(deck, key_image)


# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
  
    if icon_filename:
        icon_filename = os.path.join(ASSETS_PATH, icon_filename)
        icon = Image.open(icon_filename)
    else:
        icon = PILHelper.create_image(deck)

    if label_text:
        image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image a few pixels from the bottom of the key.
        draw = ImageDraw.Draw(image)
        font_filename = os.path.join(ASSETS_PATH, font_filename)
        font = ImageFont.truetype(font_filename, 14)
        draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")
    else:
        image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 0, 0])

    return PILHelper.to_native_format(deck, image)


# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
   # Last button in the example application is the exit button.
   nr, nc = deck.key_layout()

   if page_num == 1:
    if key == (nr-3) * nc + 0:
        name = "brake"
        icon = "{}.png".format("brake-on" if state else "brake-off")
        font = "Roboto-Regular.ttf"
        label = 'Brake'
    elif key == (nr-2) * nc + 0:
        name = "jog"
        icon = 'jogging_menu.png'
        font = "Roboto-Regular.ttf"
        label = 'Jog'
    elif key == (nr-1) * nc + 0:
        name = "probe"
        icon = 'probe_menu.png'
        font = "Roboto-Regular.ttf"
        label = 'Probe'
    elif key == (nr-3) * nc + nc-1:
        name = ""
        icon = "watermark.png"
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + nc-1:
        name = "coordinates"
        icon = ''
        font = "Roboto-Regular.ttf"
        label = ''
    else:
            name = ""
            icon = ""
            font = "Roboto-Regular.ttf"
            label = ""
   elif page_num == 2:
    exit_key_index = nc - 1

    if key == exit_key_index:
        name = "exit"
        icon = "{}.png".format("Exit")
        font = "Roboto-Regular.ttf"
        label = "Bye" if state else "Exit"
    # elif key == (nr-3) * nc + 0:
    #     name = "brake"
    #     icon = "{}.png".format("brake-on" if state else "brake-off")
    #     font = "Roboto-Regular.ttf"
    #     label = 'Brake'
    elif key == (nr-3) * nc + 0:
        name = "jog_speed"
        icon = ''
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + 0:
        name = "jog_z_+"
        icon = "{}.png".format("jog_z_+" + ('_pressed' if state else ''))
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + 0:
        name = "jog_z_-"
        icon = "{}.png".format("jog_z_-" + ('_pressed' if state else ''))
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + nc-2:
        name = "jog_y_+"
        icon = "{}.png".format("jog_y_+" + ('_pressed' if state else ''))
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + nc-2:
        name = "jog_y_-"
        icon = "{}.png".format("jog_y_-" + ('_pressed' if state else ''))
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + nc-3:
        name = "jog_x_-"
        icon = "{}.png".format("jog_x_-" + ('_pressed' if state else ''))
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + nc-1:
        name = "jog_x_+"
        icon = "{}.png".format("jog_x_+" + ('_pressed' if state else ''))
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + nc-1:
        name = "coordinates"
        icon = ''
        font = "Roboto-Regular.ttf"
        label = ''
    else:
        if False:
            name = "emoji"
            icon = "{}.png".format("Pressed" if state else "Released")
            font = "Roboto-Regular.ttf"
            label = "Pressed!" if state else "Key {}".format(key)
        else:
            name = ""
            icon = ""
            font = "Roboto-Regular.ttf"
            label = ""

   elif page_num == 3:
    exit_key_index = nc - 1

    if key == exit_key_index:
        name = "exit"
        icon = "{}.png".format("Exit")
        font = "Roboto-Regular.ttf"
        label = "Bye" if state else "Exit"
    elif key == (nr-3) * nc + 1:
        name = "probe_7"
        icon = "{}.png".format("probe_7" if state else "probe_7")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-3) * nc + 2:
        name = "probe_8"
        icon = "{}.png".format("probe_8" if state else "probe_8")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-3) * nc + 3:
        name = "probe_9"
        icon = "{}.png".format("probe_9" if state else "probe_9")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + 1:
        name = "probe_4"
        icon = "{}.png".format("probe_4" if state else "probe_4")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + 2:
        name = "probe_5"
        icon = "{}.png".format("probe_5" if state else "probe_5")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + 3:
        name = "probe_5"
        icon = "{}.png".format("probe_5" if state else "probe_5")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + 1:
        name = "probe_1"
        icon = "{}.png".format("probe_1" if state else "probe_1")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + 2:
        name = "probe_2"
        icon = "{}.png".format("probe_2" if state else "probe_2")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-1) * nc + 3:
        name = "probe_3"
        icon = "{}.png".format("probe_3" if state else "probe_3")
        font = "Roboto-Regular.ttf"
        label = ''
    elif key == (nr-2) * nc + nc-1:
        name = "coordinates"
        icon = ''
        font = "Roboto-Regular.ttf"
        label = ''
    else:
        if False:
            name = "emoji"
            icon = "{}.png".format("Pressed" if state else "Released")
            font = "Roboto-Regular.ttf"
            label = "Pressed!" if state else "Key {}".format(key)
        else:
            name = ""
            icon = ""
            font = "Roboto-Regular.ttf"
            label = ""

   return {
        "name": name,
        "icon": icon,
        "font": font,
        "label": label
   }


# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    if not key_style["icon"] and key_style["name"]:
        return

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


def title_page0(deck):
    nr, nc = deck.key_layout()

    logo = Image.open('Assets/linux logo.png')
    im_h = logo.height
    im_w = logo.width
    for r in range(nr):
        for c in range(nc):
            key = r * nc + c

            icon = logo
            image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 0, 0])

            image = PILHelper.to_native_format(deck, image)

            with deck:
                deck.set_key_image(key, image)


def title_page(deck):
        # Approximate number of (non-visible) pixels between each key, so we can
        # take those into account when cutting up the image to show on the keys.
        key_spacing = (0, 0)

        # Load and resize a source image so that it will fill the given
        # StreamDeck.
        image = create_full_deck_sized_image(deck, key_spacing, "linux logo.png")

        # print("Created full deck image size of {}x{} pixels.".format(image.width, image.height))

        # Extract out the section of the image that is occupied by each key.
        key_images = dict()
        for k in range(deck.key_count()):
            key_images[k] = crop_key_image_from_deck_sized_image(deck, image, key_spacing, k)

        with deck:
            for k in range(deck.key_count()):
                deck.set_key_image(k, key_images[k])


state_ = {}

# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    # Print new key state
    # print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)

    # Update the key image based on the new key state.
    update_key_image(deck, key, state)

    key_style = get_key_style(deck, key, state)

    # When an exit button is pressed, close the application.
    if key_style["name"] == "exit" and state:
        set_page(deck, 1)
        # # Use a scoped-with on the deck to ensure we're the only thread
        # # using it right now.
        # with deck:
        #     # Reset deck, clearing all button images.
        #     deck.reset()
        #
        #     # Close deck handle, terminating internal worker threads.
        #     deck.close()
    elif key_style["name"] == "jog" and state:
        set_page(deck, 2)
    elif key_style["name"] == "probe" and state:
        set_page(deck, 3)
    else:
        global state_, brake_state_
        if key_style['name']:
            if key_style['name'] == 'brake':
                if state:
                    # print(key_style["name"], 'toggle')
                    state_[key_style['name']] = not brake_state_
            else:
                # print(key_style["name"], state)
                state_[key_style['name']] = state


def update(deck):
    if True:
        global rf, wf

        if wf is None:
            wf = os.open(write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)
        if rf is None:
            rf = os.open(read_path, os.O_RDONLY)

        global state_
        if state_: 
            msg = '\n'.join([f'{k}:{1 if v else 0}' for k,v in state_.items()])
            state_ = {}
        else:
            msg = '0'
        b = msg.encode('latin-1')
        len_send = os.write(wf, b)

        b = os.read(rf, 1024)
        if len(b) == 0:
            return
        s = b.decode('latin-1')
        # print('Received:', s)
    
        lst = s.split()
        lst[-2] = lst[-2] == '1'
    else:
        lst = [f'{random.random() * 100 :06.4f}' for x in range(3)] + [1]

    nr, nc = deck.key_layout()

    key_width, key_height = deck.key_image_format()['size']

    image = PILHelper.create_image(deck)

    font = "Roboto-Regular.ttf"
    font_filename = os.path.join(ASSETS_PATH, font)

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 16)
    for (i, y) in enumerate([60, 35, 10]):
        label_text = lst[i]
        draw.text((image.width - 5, image.height - y), text=label_text, font=font, anchor="rs", fill="white")
    k = (nr-2) * nc + nc - 1

    key_image = PILHelper.to_native_format(deck, image)
    deck.set_key_image(k, key_image)

    global brake_state_
    brake_state_ = lst[-2]
    if page_num == 1:
        update_key_image(deck, 0, brake_state_)
    jog_vel_ = lst[-2]
    if page_num == 2:
        image = PILHelper.create_image(deck)

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, 16)
        label_text = f'{lst[-1]} ips'
        draw.text((image.width / 2, image.height / 2), text=label_text, font=font, anchor="ms", fill="white")

        key_image = PILHelper.to_native_format(deck, image)
        deck.set_key_image(0, key_image)

    # print(state_)


def set_page(deck, pn):
    global page_num
    page_num = pn
    if pn == 0:
        title_page(deck)
    else:
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

        set_page(deck, 0)
        time.sleep(5)

        # Set initial key images.
        set_page(deck, 1)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            if t is threading.currentThread():
                continue

            while t.is_alive():
                t.join(.1)
                if t.is_alive():
                    update(deck)

os.write(wf, 'exit')
 
os.close(rf)
os.close(wf)

