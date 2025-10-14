import numpy as np
import cv2
import os
import tensorflow as tf


def load_malaria_filenames(load_data_dir, labels, tot_images):
    X = []
    Y = []

    for l_idx, label in enumerate(labels):
        image_names = os.listdir(os.path.join(load_data_dir, label))

        for i, image_name in enumerate(image_names[:tot_images]):
            if not image_name.endswith('.png'):
                continue
            img_name = os.path.join(load_data_dir, label, image_name)
            X.append(img_name)
            Y.append(l_idx)

    print('Loading filenames completed.')

    return X, Y

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



def normalize_img(image):
    return tf.cast(image, tf.float32) / 255.