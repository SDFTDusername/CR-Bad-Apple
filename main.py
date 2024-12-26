import os
from random import randrange

import keyboard
import mouse
import time
import shutil
import math
from mss import mss

colors = ("#", "[.", "+", "-", "*.", ". ", "  ")
resolution = (15, 4)
fps = 24

colors_len = len(colors)

screenshots_dir = "screenshots"
start_keybind = "k"

def error(msg: str):
    print(f"[ERROR]: {msg}")

def pad_number(num: int, padding: int) -> str:
    return str(num).rjust(padding, '0')

def get_color(color: int) -> str:
    return colors[round(color / 255 * (colors_len - 1))]

def random_frame() -> list[list[int]]:
    frame = []
    for y in range(resolution[1]):
        line = []
        for x in range(resolution[0]):
            line.append(randrange(0, 256))
        frame.append(line)
    return frame

def get_line(frame_line: list[int]) -> str:
    line = ""
    for x in range(resolution[0]):
        line += get_color(frame_line[x])
    return line

def start():
    if os.path.isdir(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.mkdir(screenshots_dir)

    total_frames = 10
    frame_padding = len(str(total_frames))

    for frame_count in range(total_frames):
        viewed_frame = frame_count + 1

        if frame_count > 0:
            # Break previous sign and wait for game to update
            mouse.click(mouse.LEFT)
            time.sleep(0.2)

        # Place sign and wait for game to update
        mouse.click(mouse.RIGHT)
        time.sleep(0.2)

        # Get frame
        frame = random_frame()

        # Type frame
        for y in range(resolution[1]):
            keyboard.write(get_line(frame[y]))
            if y < resolution[1] - 1:
                keyboard.press("enter")

        # Exit screen and wait for game to update
        keyboard.press("esc")
        time.sleep(0.2)

        # Convert frame count to string
        viewed_frame_str = pad_number(viewed_frame, frame_padding)

        # Take a screenshot and save
        with mss() as sct:
            sct.shot(output=f"{screenshots_dir}/frame_{viewed_frame_str}.png")

        # Print progress
        percentage = math.floor(viewed_frame / total_frames * 1_000) / 10
        if total_frames == 1:
            print(f"{viewed_frame_str} out of {total_frames} frame is done. That is {percentage}% complete.")
        else:
            print(f"{viewed_frame_str} out of {total_frames} frames are done. That is {percentage}% complete.")

    print("We are done!")

def main():
    fail = False

    if not os.path.isfile("video.mp4"):
        error("video.mp4 does not exist.")
        fail = True

    if not os.path.isfile("audio.mp3"):
        error("audio.mp3 does not exist.")
        fail = True

    if fail:
        return

    print(f"Select the sign in your hotbar and press the '{start_keybind}' key to start.")
    keyboard.wait(start_keybind)

    start()

if __name__ == "__main__":
    main()
