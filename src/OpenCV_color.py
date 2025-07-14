import cv2
import numpy as np
from picamera2 import Picamera2

# Program captures video from the camera and detects red and green colored blocks in the frame.
# It then decided which colored block is bigger to determine the direction to turn.
# Red block means turn right, green block means turn left.
# It also checks for the size of the bounding box of the detected color 
# so as to avoid detecting objects that are too small or too far

# Further tmprovements needed: 
# - Send the turn direction data over serial port to the MCU
# - Depending on how close the object is, calculate rate of turn and communicate to avoid hitting the blocks

cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Function to calculate the midpoint of the bounding box
# and return the coordinates relative to the center of the frame
# Returns None if no bounding box is provided
# Returns a tuple (x, y) where x is the horizontal offset and y is the vertical offset
# x < 0 means the object is to the right of the center
# x > 0 means the object is to the left of the center
# y < 0 means the object is above the center
# y > 0 means the object is below the center
def midXPoint(bbox):
    fr_width = picam2.stream_configuration("main").get("size")[0]

    if bbox is None:
        return None
    
    x1, y1, x2, y2 = bbox
    return (int((x1 + x2) - fr_width) / 2)

# Function to determine the navigation direction based on the bounding box
# - Returns "LEFT" if the object is to the right of the center of the frame
# - Returns "RIGHT" if the object is to the left of the center of the frame
# - Returns "KEEP" if the object is centered
# - Returns "No object detected" if no bounding box is provided
def getNavDirection(bbox):
    fr_width = picam2.stream_configuration("main").get("size")[0]
    fr_height = picam2.stream_configuration("main").get("size")[1]

    if bbox is None:
        return "No object detected"

    x1, y1, x2, y2 = bbox
    mid_x = (x1 + x2) - fr_width/ 2

    if mid_x < 0:
        return "RIGHT"
    elif mid_x > 0:
        return "LEFT"
    else:
        return "KEEP"

# Function to calculate the size of the bounding box
# Returns 0 if no bounding box is provided
# Returns the area of the bounding box as an integer
def getSize(bbox):
    if bbox is None:
        return 0
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)

# Define green and red color ranges in HSV
lower_green = np.array([50, 120, 70])
upper_green = np.array([90, 255, 255])

lower_red1 = np.array([0, 160, 120])
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([170, 160, 120])
upper_red2 = np.array([180, 255, 255])

bbox_size_threshold = 4000  # Minimum size of the bounding box to consider

while True:

    cap = picam2.capture_array("main")

    if cap is None:
        print("No image captured")
        break

    # Convert to HSV color space
    hsv = cv2.cvtColor(cap, cv2.COLOR_BGR2HSV)

    # Morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)

    # Create masks for green color 
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_G = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    mask_G = cv2.morphologyEx(mask_green, cv2.MORPH_DILATE, kernel)

    # Create masks for lower bound and upper bound of red color in HSV spectrum
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    mask_R = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_R = cv2.morphologyEx(mask_red, cv2.MORPH_DILATE, kernel)

    # Find contours
    contours_g, _ = cv2.findContours(mask_G, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    green_bbox = None
    
    if contours_g:
        largest_contour_g = max(contours_g, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour_g)
        green_bbox = (x, y, x + w, y + h)

    contours_r, _ = cv2.findContours(mask_R, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    red_bbox = None

    if contours_r:
        largest_contour_r = max(contours_r, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour_r)
        red_bbox = (x, y, x + w, y + h)
    
    if red_bbox is not None and getSize(red_bbox) > bbox_size_threshold and (getSize(red_bbox) >= getSize(green_bbox)):
        x, y, w, h = red_bbox
        cv2.rectangle(cap, (x, y), (w, h), (0, 0, 255), 1)
        print ("TURN RIGHT")
    elif green_bbox is not None and getSize(green_bbox) > bbox_size_threshold and (getSize(green_bbox) > getSize(red_bbox)):
        x, y, w, h = green_bbox
        cv2.rectangle(cap, (x, y), (w, h), (0, 255, 0), 1)
        print ("TURN LEFT")
    
    # print(midXPoint(bbox))

    cv2.imshow("Video Frame", cap)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
