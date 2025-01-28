import cv2

def play_video(video_path, screen_width, screen_height, window_name):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Could not open video.")
        return

    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    video_aspect_ratio = frame_width / frame_height
    screen_aspect_ratio = screen_width / screen_height

    if video_aspect_ratio > screen_aspect_ratio:
        scale_factor = screen_width / frame_width
    else:
        scale_factor = screen_height / frame_height

    new_width = int(frame_width * scale_factor)
    new_height = int(frame_height * scale_factor)

    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, screen_width, screen_height)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        resized_frame = cv2.resize(frame, (new_width, new_height))
        background = cv2.resize(frame, (screen_width, screen_height))
        background[:] = 0
        background[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame

        cv2.imshow(window_name, background)

        if cv2.waitKey(25) & 0xFF == 27:
            break

    video.release()
    cv2.destroyAllWindows()

video_path = "input.mp4"
screen_width = 800
screen_height = 600