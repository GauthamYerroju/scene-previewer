import cv2
import numpy as np
import sys, os
import imageio
import shutil


# mean squared error
def calculate_difference_mse(im1, im2):
    mse = ((im1 - im2) ** 2).mean(axis=None)
    return mse


# pixel count variation
def calculate_simple_difference(im1, im2):
    err = np.sum(cv2.absdiff(im1, im2))
    return err


def calculate_difference(im1, im2, mode):
    if mode == 'simple':
        return calculate_simple_difference(im1, im2)
    elif mode == 'mse':
        return calculate_difference_mse(im1, im2)


def transform_to_gif(duration, output):
    images = []
    temp_folder = os.getcwd() + "/temp/"
    output_path = "%s/output/%s.gif" % (os.getcwd(), output)
    for filename in os.listdir(temp_folder):
        images.append(imageio.imread(temp_folder + filename))
    imageio.mimsave(output_path, images, duration=duration )
    print "Gif has been successfully generated at %s" % output_path


def main():
    if len(sys.argv) < 5:
        print "Not enough parameters"
        exit(0)

    # video path
    video_path = str(sys.argv[1])

    if video_path is None:
        print "You need to specify the video path"
        exit(0)

    # video information
    video_name = video_path.split('.')[0]
    video_capture = cv2.VideoCapture(video_path)
    total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

    # mode
    mode = str(sys.argv[2])

    # mode selection
    if mode == 'simple':
        max_error = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH) * video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT) * 255
    elif mode == 'mse':
        max_error = 255
    else:
        max_error = 0
        print "Wrong mode selected."
        exit(0)

    # threshold
    threshold = float(sys.argv[3])
    if threshold < 0 or threshold > 1:
        print "Wrong threshold selected."
        exit(0)

    # gif duration
    duration = float(sys.argv[4])

    # working directory
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.makedirs("temp")

    if not os.path.exists("output"):
        os.makedirs("output")

    if video_capture.isOpened() is False:
        print "Invalid file"
        exit(0)

    # init variables for the while-loop
    captured_frames = 0
    previous_frame = None
    frame_index = 1
    while frame_index < total_frames:
        ret, frame = video_capture.read(frame_index)
        if frame is None:
            break
        current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if previous_frame is not None:
            diff_ratio = calculate_difference(current_frame, previous_frame, mode) / max_error
            if diff_ratio > threshold:
                captured_frames += 1
                file_name = "temp\%s_%d_%d.png" %( video_name, captured_frames, frame_index)
                cv2.imwrite(file_name, frame)
        previous_frame = current_frame
        frame_index += 1
    video_capture.release()
    print "Captured Scene Changes: %d" %captured_frames
    transform_to_gif(duration, video_name)
    shutil.rmtree("temp")


if __name__ == "__main__":
    main()