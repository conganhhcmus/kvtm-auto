from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO

import cv2
import numpy as np
import pytesseract
from PIL import Image


class ImageController:
    """Image processing utilities for template matching and screen analysis"""

    @staticmethod
    def read_image_bytes(file_path: str) -> bytes:
        """Read image file and return raw bytes"""
        with open(file_path, "rb") as f:
            return f.read()

    @staticmethod
    def read_asset_image_bytes(asset_filename: str) -> bytes:
        """
        Read image from assets folder and return raw bytes

        Args:
            asset_filename: Filename in the assets folder (e.g., 'test')

        Returns:
            Image bytes

        Raises:
            FileNotFoundError: If asset file doesn't exist
        """
        # Build path to assets folder relative to this file
        # backend/src/libs/image_controller.py -> backend/src/assets/
        current_file = Path(__file__)
        assets_path = current_file.parent.parent / "assets" / f"{asset_filename}.png"
        assets_path = assets_path.resolve()

        if not assets_path.exists():
            raise FileNotFoundError(f"Asset file not found: {assets_path}")

        return ImageController.read_image_bytes(str(assets_path))

    @staticmethod
    def _bytes_to_image(image_bytes: bytes) -> np.ndarray:
        """Convert bytes to OpenCV image array"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode image from bytes")
        return image

    @staticmethod
    def _preprocess_image(image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale for faster processing"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    @staticmethod
    def _multi_scale_match(
        screen: np.ndarray, template: np.ndarray, threshold: float
    ) -> Optional[Tuple[int, int]]:
        """Perform template matching with rotation support and early termination"""
        template_h, template_w = template.shape
        screen_h, screen_w = screen.shape

        # Check if template is larger than screen (considering rotation)
        if (template_h > screen_h or template_w > screen_w) and (
            template_w > screen_h or template_h > screen_w
        ):
            return None

        best_match = None
        best_confidence = 0

        # Try different rotations (no scaling for performance)
        rotations = [0, 90, 180, 270]  # Common device rotations

        for rotation in rotations:
            # Rotate template
            if rotation == 0:
                rotated_template = template
            elif rotation == 90:
                rotated_template = cv2.rotate(template, cv2.ROTATE_90_CLOCKWISE)
            elif rotation == 180:
                rotated_template = cv2.rotate(template, cv2.ROTATE_180)
            else:  # 270
                rotated_template = cv2.rotate(template, cv2.ROTATE_90_COUNTERCLOCKWISE)

            rot_h, rot_w = rotated_template.shape

            # Skip if rotated template is larger than screen
            if rot_h > screen_h or rot_w > screen_w:
                continue

            # Perform template matching
            result = cv2.matchTemplate(screen, rotated_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Early termination if we found a good match
            if max_val >= threshold:
                center_x = max_loc[0] + rot_w // 2
                center_y = max_loc[1] + rot_h // 2
                return (center_x, center_y)

            # Keep track of best match even if below threshold
            if max_val > best_confidence:
                best_confidence = max_val
                center_x = max_loc[0] + rot_w // 2
                center_y = max_loc[1] + rot_h // 2
                best_match = (center_x, center_y)

        # Return best match only if above threshold
        return best_match if best_confidence >= threshold else None

    @staticmethod
    def get_coordinate(
        screen_bytes: bytes, template_bytes: bytes, threshold: float = 0.9
    ) -> Optional[Tuple[int, int]]:
        """
        Find template image within screen capture with similarity threshold

        Args:
            screen_bytes: Screen capture bytes from adb.capture_screen()
            template_bytes: Template image bytes from file
            threshold: Similarity threshold (default 0.9 for 90% similarity)

        Returns:
            Tuple of (x, y) center coordinates if match found, None otherwise
        """
        try:
            # Convert bytes to images
            screen_img = ImageController._bytes_to_image(screen_bytes)
            template_img = ImageController._bytes_to_image(template_bytes)

            # Convert to grayscale for faster processing
            screen_gray = ImageController._preprocess_image(screen_img)
            template_gray = ImageController._preprocess_image(template_img)

            # Perform multi-scale template matching
            return ImageController._multi_scale_match(
                screen_gray, template_gray, threshold
            )

        except Exception as e:
            print(f"Error in get_coordinate: {e}")
            return None

    @staticmethod
    def find_text_in_image_bytes(
        screen_bytes: bytes, target_text: str, lang: str = "eng"
    ) -> Optional[Tuple[int, int]]:
        """
        Find text position in screen bytes using OCR

        Args:
            screen_bytes: Screen capture bytes from adb.capture_screen()
            target_text: Text to search for
            lang: Language for OCR (default "eng")

        Returns:
            Tuple of (x, y) center coordinates if text found, None otherwise
        """
        try:
            # Convert bytes to PIL Image
            img = Image.open(BytesIO(screen_bytes))

            # Use pytesseract to extract text data
            data = pytesseract.image_to_data(
                img, lang=lang, output_type=pytesseract.Output.DICT
            )

            # Search for target text in OCR results
            for i in range(len(data["text"])):
                if target_text.lower() in data["text"][i].lower():
                    x = data["left"][i] + data["width"][i] // 2
                    y = data["top"][i] + data["height"][i] // 2
                    return (x, y)
            return None

        except Exception as e:
            print(f"Error in find_text_in_image_bytes: {e}")
            return None


# Global ImageController instance
image_controller = ImageController()
