import _thread
import math
import os
import random
import shutil
import threading
import time
import typing

import cv2
import keyboard
import mouse
from mss import mss

FrameLine = typing.List[int]
Frame = typing.List[FrameLine]
Frames = typing.List[Frame]

colors = ("#", "[.", "+", "-", "*.", ". ", "  ")
sign_resolution = (15, 4)
block_resolution = (1, 1)

video_file = "video.mp4"
audio_file = "audio.mp3"
screenshots_dir = "screenshots"
output_file = "output.mp4"

start_keybind = "k"
stop_keybind = 'j'

delay = 0.1
mouse_move_amount = 100

video_resolution = (sign_resolution[0] * block_resolution[0], sign_resolution[1] * block_resolution[1])
colors_len = len(colors)
fps = 0

def exit_on_press():
    keyboard.wait(stop_keybind)
    _thread.interrupt_main()

exit_thread = threading.Thread(target=exit_on_press)
exit_thread.daemon = True

def error(msg: str):
    print(f"[ERROR]: {msg}")

def pad_number(num: int, padding: int) -> str:
    return str(num).rjust(padding, '0')

def get_color(color: int) -> str:
    return colors[round(color / 255 * (colors_len - 1))]

def get_frames(file: str) -> Frames:
    global fps

    video = cv2.VideoCapture(file)
    fps = video.get(cv2.CAP_PROP_FPS)
    frames = []
    success, frame = video.read()

    while success:
        converted_frame = cv2.cvtColor(cv2.resize(frame, video_resolution), cv2.COLOR_BGR2GRAY)

        new_frame = []
        for y in range(video_resolution[1]):
            new_line = []
            for x in range(video_resolution[0]):
                new_line.append(converted_frame[y, x])
            new_frame.append(new_line)

        frames.append(new_frame)
        success, frame = video.read()

    video.release()
    return frames

def random_frame() -> Frame:
    frame = []
    for y in range(video_resolution[1]):
        line = []
        for x in range(video_resolution[0]):
            line.append(random.randint(0, 255))
        frame.append(line)
    return frame

def get_line(frame_line: FrameLine) -> str:
    line = ""
    for x in range(video_resolution[0]):
        line += get_color(frame_line[x])
    return line

def move_mouse_relative(x: float, y: float):
    mouse._os_mouse.move_relative(x, y)

def start(frames: Frames):
    if os.path.isdir(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.mkdir(screenshots_dir)

    total_frames = len(frames)
    frame_padding = len(str(total_frames))

    for frame_count in range(total_frames):
        viewed_frame = frame_count + 1
        frame = frames[frame_count]

        last_movement = (0, 0)

        for block_y in range(block_resolution[1]):
            abs_y = block_y * sign_resolution[1]
            move_y = block_y * 2 - block_resolution[1] / 2
            for block_x in range(block_resolution[0]):
                abs_x = block_x * sign_resolution[0]
                move_x = block_x * 2 - block_resolution[0] / 2

                if block_resolution != (1, 1):
                    new_movement = (move_x * mouse_move_amount, move_y * mouse_move_amount)
                    move_mouse_relative(-last_movement[0] + new_movement[0], -last_movement[1] + new_movement[1])
                    last_movement = new_movement
                    time.sleep(delay)

                if frame_count > 0:
                    # Break previous sign and wait for game to update
                    mouse.click(mouse.LEFT)
                    time.sleep(delay)

                # Place sign and wait for game to update
                mouse.click(mouse.RIGHT)
                time.sleep(delay)

                # Type frame
                for y in range(sign_resolution[1]):
                    line = get_line(frame[abs_y + y])
                    keyboard.write(line[abs_x:(abs_x+sign_resolution[0])])
                    if y < sign_resolution[1] - 1:
                        keyboard.press("enter")

                # Exit screen and wait for game to update
                keyboard.press("esc")
                time.sleep(delay)

        if block_resolution != (1, 1):
            move_mouse_relative(-last_movement[0], -last_movement[1])
            time.sleep(delay)

        # Convert frame count to string
        viewed_frame_str = pad_number(viewed_frame, frame_padding)

        # Take a screenshot and save
        with mss() as sct:
            sct.shot(output=f"{screenshots_dir}/frame_{viewed_frame_str}.png")

        # Print progress
        percentage = math.floor(viewed_frame / total_frames * 10_000) / 100
        if total_frames == 1:
            print(f"{viewed_frame_str} out of {total_frames} frame is done. That is {percentage}% complete.")
        else:
            print(f"{viewed_frame_str} out of {total_frames} frames are done. That is {percentage}% complete.")

    print("Saving to video...")

    os.system(f"ffmpeg -y -framerate {fps} -i {screenshots_dir}/frame_%0{frame_padding}d.png -i {audio_file} -c:v libx264 -c:a aac -shortest -pix_fmt yuv420p {output_file}")
    print(f"Saved to {output_file}!")

def main():
    fail = False

    if not os.path.isfile(video_file):
        error(f"{video_file} does not exist.")
        fail = True

    if not os.path.isfile(audio_file):
        error(f"{audio_file} does not exist.")
        fail = True

    if fail:
        return

    print("Loading video...")
    frames = get_frames(video_file)

    print(f"To stop the program while it's running, press the '{stop_keybind}' key.")

    print(f"Select the sign in your hotbar and press the '{start_keybind}' key to start.")
    keyboard.wait(start_keybind)

    exit_thread.start()
    start(frames)

if __name__ == "__main__":
    main()
