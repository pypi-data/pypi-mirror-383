import numpy as np
import cv2




def load_malaria_image(img_name):
    num_row = 100
    num_col = 100

    if isinstance(img_name, bytes):
        img_name = img_name.decode()

    # Load the image in color (loads as BGR by default)
    img = cv2.imread(img_name, cv2.IMREAD_COLOR)

    # Check if image loaded successfully
    if img is None:
        print(f"Warning: Could not load image {img_name}")
        return None # Or raise an error

    # Convert the color space from BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize the image
    img = cv2.resize(img, (num_row, num_col))

    # Convert to a float32 NumPy array
    img = np.array(img, dtype='float32')

    return img