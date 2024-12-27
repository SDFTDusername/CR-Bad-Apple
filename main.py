import _thread
import json
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

resolution = (45, 4)

creative = True
max_stack = 1_000
current_hotbar_slot = 1

video_file = "video.mp4"
audio_file = "audio.mp3"
screenshots_dir = "screenshots"
output_file = "output.mp4"

start_keybind = "k"
stop_keybind = 'j'

delay = 0.1

with open("characters.json") as file:
    colors = tuple(json.load(file))

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
        converted_frame = cv2.cvtColor(cv2.resize(frame, resolution), cv2.COLOR_BGR2GRAY)

        new_frame = []
        for y in range(resolution[1]):
            new_line = []
            for x in range(resolution[0]):
                new_line.append(converted_frame[y, x])
            new_frame.append(new_line)

        frames.append(new_frame)
        success, frame = video.read()

    video.release()
    return frames

def random_frame() -> Frame:
    frame = []
    for y in range(resolution[1]):
        line = []
        for x in range(resolution[0]):
            line.append(random.randint(0, 255))
        frame.append(line)
    return frame

def get_line(frame_line: FrameLine) -> str:
    line = ""
    for x in range(resolution[0]):
        line += get_color(frame_line[x])
    return line

def start(frames: Frames):
    global current_hotbar_slot

    if os.path.isdir(screenshots_dir):
        print("Deleting screenshots folder...")
        shutil.rmtree(screenshots_dir)
    os.mkdir(screenshots_dir)

    print("Starting!")

    average_time = []
    current_stack_size = max_stack

    total_frames = len(frames)
    frame_padding = len(str(total_frames))

    for frame_count in range(total_frames):
        start_time = time.time()
        viewed_frame = frame_count + 1

        if frame_count > 0:
            if current_stack_size <= 0:
                current_stack_size = max_stack
                current_hotbar_slot += 1
                keyboard.press(str(current_hotbar_slot))
                time.sleep(delay)

            # Break previous sign and wait for game to update
            mouse.click(mouse.LEFT)

            if not creative:
                current_stack_size -= 1

        # Place sign and wait for game to update
        mouse.click(mouse.RIGHT)
        time.sleep(delay)

        # Get frame
        frame = frames[frame_count]

        # Type frame
        for y in range(resolution[1]):
            keyboard.write(get_line(frame[y]))
            if y < resolution[1] - 1:
                keyboard.press("enter")

        # Exit screen and wait for game to update
        keyboard.press("esc")
        time.sleep(delay)

        # Convert frame count to string
        viewed_frame_str = pad_number(viewed_frame, frame_padding)

        # Take a screenshot and save
        with mss() as sct:
            sct.shot(output=f"{screenshots_dir}/frame_{viewed_frame_str}.png")

        end_time = time.time()
        total_time = end_time - start_time

        if len(average_time) > 25:
            average_time.pop(0)
        average_time.append(total_time)

        avg_time = sum(average_time) / len(average_time) * (total_frames - frame_count)
        estimated_time = f"{pad_number(int(avg_time / 60 / 60), 2)}h, {pad_number(int(avg_time / 60) % 60, 2)}m, {pad_number(int(avg_time % 60), 2)}s"

        # Print progress
        percentage = "{0:.2f}".format(math.floor(viewed_frame / total_frames * 10_000) / 100)
        if total_frames == 1:
            print(f"{viewed_frame_str} out of {total_frames} frame is done. Estimated to be done in {estimated_time}. We are {percentage}% complete")
        else:
            print(f"{viewed_frame_str} out of {total_frames} frames are done. Estimated to be done in {estimated_time}. We are {percentage}% complete")

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

    print("Loading video into memory...")
    frames = get_frames(video_file)

    print(f"To stop the program while it's running, press the '{stop_keybind}' key.")

    print(f"Select the sign in your hotbar and press the '{start_keybind}' key to start.")
    keyboard.wait(start_keybind)

    exit_thread.start()
    start(frames)

if __name__ == "__main__":
    main()
