"""
Bounding box utilities for object detection in videos.
Based on Google's Gemini bounding box detection patterns.
"""

import io
import base64
from typing import List, Dict, Any
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw
from pydantic import BaseModel


class BoundingBox(BaseModel):
    """
    Represents a bounding box with its 2D coordinates and associated label.

    Attributes:
        box_2d (list[int]): A list of integers representing the 2D coordinates of the bounding box,
                            typically in the format [y_min, x_min, y_max, x_max] (normalized to 1000).
        label (str): A string representing the label or class associated with the object within the bounding box.
    """

    box_2d: list[int]
    label: str


def plot_bounding_boxes_on_image(
    image_data: bytes, bounding_boxes: List[BoundingBox]
) -> str:
    """
    Plots bounding boxes on an image with labels, using PIL and normalized coordinates.

    Args:
        image_data: Raw image data as bytes
        bounding_boxes: A list of BoundingBox objects. Each box's coordinates are in
                       normalized [y_min, x_min, y_max, x_max] format (0-1000).

    Returns:
        str: Base64-encoded JPEG image with bounding boxes
    """
    # Open image from bytes
    with Image.open(io.BytesIO(image_data)) as im:
        width, height = im.size
        draw = ImageDraw.Draw(im)

        colors = list(ImageColor.colormap.keys())

        for i, bbox in enumerate(bounding_boxes):
            # Scale normalized coordinates (0-1000) to image dimensions
            abs_y_min = int(bbox.box_2d[0] / 1000 * height)
            abs_x_min = int(bbox.box_2d[1] / 1000 * width)
            abs_y_max = int(bbox.box_2d[2] / 1000 * height)
            abs_x_max = int(bbox.box_2d[3] / 1000 * width)

            color = colors[i % len(colors)]

            # Draw the rectangle using the correct (x, y) pairs
            draw.rectangle(
                ((abs_x_min, abs_y_min), (abs_x_max, abs_y_max)),
                outline=color,
                width=4,
            )
            if bbox.label:
                # Position the text at the top-left corner of the box
                draw.text((abs_x_min + 8, abs_y_min + 6), bbox.label, fill=color)

        # Convert to base64
        img_buffer = io.BytesIO()
        im.save(img_buffer, format="JPEG", quality=95)
        img_buffer.seek(0)

        return base64.b64encode(img_buffer.read()).decode("utf-8")


def create_bounding_box_prompt(query: str, timestamp: str = None) -> str:
    """Create a prompt for object detection with bounding boxes"""
    base_prompt = f"""
    Return bounding boxes as an array with labels for: {query}
    Never return masks. Limit to 25 objects.
    If an object is present multiple times, give each object a unique label
    according to its distinct characteristics (colors, size, position, etc.).
    """

    if timestamp:
        base_prompt += f"\n\nFocus on the frame at timestamp {timestamp}."

    return base_prompt.strip()


def extract_frame_from_video_at_timestamp(video_path: Path, timestamp: str) -> bytes:
    """
    Extract a frame from video at specific timestamp.

    Args:
        video_path: Path to the video file
        timestamp: Timestamp in format "MM:SS" or "HH:MM:SS"

    Returns:
        bytes: JPEG image data
    """
    import cv2

    # Convert timestamp to seconds
    time_parts = timestamp.split(":")
    if len(time_parts) == 2:  # MM:SS
        seconds = int(time_parts[0]) * 60 + int(time_parts[1])
    elif len(time_parts) == 3:  # HH:MM:SS
        seconds = (
            int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
        )
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp}")

    # Open video and seek to timestamp
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    # Set frame position
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(seconds * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read frame
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError(f"Could not extract frame at timestamp {timestamp}")

    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to PIL Image and then to bytes
    pil_image = Image.fromarray(frame_rgb)

    # Compress to JPEG bytes
    img_buffer = io.BytesIO()
    pil_image.save(img_buffer, format="JPEG", quality=95)

    return img_buffer.getvalue()


