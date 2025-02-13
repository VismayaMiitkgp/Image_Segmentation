# -*- coding: utf-8 -*-
"""Image_Segmentation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TPsuR4JWPxhfpR8ib8E6_sgJC2faLvNc

Using K means clustering
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def segment_image(image_path, k=3):
    # Read the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Reshape the image to a 2D array of pixels
    pixel_values = image.reshape((-1, 3))
    pixel_values = np.float32(pixel_values)

    # Define the criteria and apply k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert back to 8 bit values
    centers = np.uint8(centers)

    # Map the labels to the centers
    segmented_image = centers[labels.flatten()]
    segmented_image = segmented_image.reshape(image.shape)

    # Show the segmented image
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.title('Original Image')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(segmented_image)
    plt.title('Segmented Image')
    plt.axis('off')

    plt.show()

# Example usage
segment_image('/content/Group 1 R1 150.jpg', k=3)

"""NDVI"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def calculate_ndvi(image_path):
    # Read the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to float32
    image = image.astype(np.float32) / 255.0

    # Separate the channels
    red = image[:, :, 0]
    green = image[:, :, 1]
    blue = image[:, :, 2]

    # Approximate NIR using the green and blue bands
    # This is a simplification, actual NIR should be used if available
    nir = (green + blue) / 2

    # Calculate NDVI
    ndvi = (nir - red) / (nir + red + 1e-10)  # Add a small number to avoid division by zero

    return ndvi

def segment_green_area(ndvi, threshold=0.2):
    # Create a binary mask based on the NDVI threshold
    mask = ndvi > threshold

    return mask

def apply_mask(image_path, mask):
    # Read the image again to apply the mask
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Apply the mask to the image
    segmented_image = np.zeros_like(image)
    segmented_image[mask] = image[mask]

    return segmented_image

# Example usage
image_path = '/content/Group 1 R1 150.jpg'
ndvi = calculate_ndvi(image_path)
mask = segment_green_area(ndvi, threshold=0.2)
segmented_image = apply_mask(image_path, mask)

# Display the original and segmented images
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB))
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(ndvi, cmap='gray')
plt.title('NDVI')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.imshow(segmented_image)
plt.title('Segmented Image')
plt.axis('off')

plt.show()

"""Excess Green Minus Excess Red"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def calculate_exg_exr(image):
    # Convert the image to float32
    image = image.astype(np.float32) / 255.0

    # Separate the channels
    red = image[:, :, 2]
    green = image[:, :, 1]
    blue = image[:, :, 0]

    # Calculate Excess Green (ExG) and Excess Red (ExR)
    exg = 2 * green - red - blue
    exr = 1.4 * red - green

    # Calculate the ExG - ExR index
    exg_exr = exg - exr

    return exg_exr

def segment_green_area(exg_exr, threshold=0.0):
    # Create a binary mask based on the ExG - ExR threshold
    mask = exg_exr > threshold

    return mask

def apply_mask(image, mask):
    # Apply the mask to the image
    segmented_image = np.zeros_like(image)
    segmented_image[mask] = image[mask]

    return segmented_image

# Example usage
image_path = '/content/Group 1 R1 150.jpg'
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

exg_exr = calculate_exg_exr(image_rgb)
mask = segment_green_area(exg_exr, threshold=0.0)
segmented_image = apply_mask(image_rgb, mask)

# Display the original and segmented images
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(image_rgb)
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(exg_exr, cmap='gray')
plt.title('ExG - ExR')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.imshow(segmented_image)
plt.title('Segmented Image')
plt.axis('off')

plt.show()

"""Modified ExG-CIVE with Otsu's threshold"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def calculate_exg_cive(image):
    # Convert the image to float32
    image = image.astype(np.float32) / 255.0

    # Separate the channels
    red = image[:, :, 2]
    green = image[:, :, 1]
    blue = image[:, :, 0]

    # Calculate Excess Green (ExG)
    exg = 2 * green - red - blue

    # Calculate Color Index of Vegetation Extraction (CIVE)
    cive = 0.441 * red - 0.881 * green + 0.385 * blue + 18.78745

    # Calculate ExG - CIVE
    exg_cive = exg - cive

    return exg_cive

def segment_green_area(exg_cive):
    # Normalize the ExG - CIVE to the range [0, 255] for thresholding
    exg_cive_normalized = cv2.normalize(exg_cive, None, 0, 255, cv2.NORM_MINMAX)
    exg_cive_normalized = exg_cive_normalized.astype(np.uint8)

    # Apply Otsu's thresholding
    _, mask = cv2.threshold(exg_cive_normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return mask

def apply_mask(image, mask):
    # Apply the mask to the image
    segmented_image = np.zeros_like(image)
    segmented_image[mask == 255] = image[mask == 255]

    return segmented_image

# Example usage
image_path = '/content/Group 1 R1 150.jpg'
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

exg_cive = calculate_exg_cive(image_rgb)
mask = segment_green_area(exg_cive)
segmented_image = apply_mask(image_rgb, mask)

# Display the original and segmented images
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(image_rgb)
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(exg_cive, cmap='gray')
plt.title('ExG - CIVE')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.imshow(segmented_image)
plt.title('Segmented Image')
plt.axis('off')

plt.show()

"""GAUSSIAN BLUR
#To smoothen image, reduce noise and improve clustering
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def segment_image(image_path, k=3):
    # Read the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Apply Gaussian blur to reduce noise and improve clustering
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)

    # Reshape the image to a 2D array of pixels
    pixel_values = blurred_image.reshape((-1, 3))
    pixel_values = np.float32(pixel_values)

    # Define the criteria and apply k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert back to 8 bit values
    centers = np.uint8(centers)

    # Map the labels to the centers
    segmented_image = centers[labels.flatten()]
    segmented_image = segmented_image.reshape(image.shape)

    # Convert segmented image to grayscale for further processing
    gray_segmented = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2GRAY)

    # Apply thresholding
    _, binary_segmented = cv2.threshold(gray_segmented, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Apply morphological operations to clean up the image
    kernel = np.ones((3, 3), np.uint8)
    cleaned_segmented = cv2.morphologyEx(binary_segmented, cv2.MORPH_CLOSE, kernel)

    # Mask the original image using the cleaned segmentation
    final_segmented = cv2.bitwise_and(image, image, mask=cleaned_segmented)

    # Show the images
    plt.figure(figsize=(15, 10))
    plt.subplot(2, 3, 1)
    plt.imshow(image)
    plt.title('Original Image')
    plt.axis('off')

    plt.subplot(2, 3, 2)
    plt.imshow(blurred_image)
    plt.title('Blurred Image')
    plt.axis('off')

    plt.subplot(2, 3, 3)
    plt.imshow(segmented_image)
    plt.title('Segmented Image (K-means)')
    plt.axis('off')

    plt.subplot(2, 3, 4)
    plt.imshow(gray_segmented, cmap='gray')
    plt.title('Grayscale Segmented Image')
    plt.axis('off')

    plt.subplot(2, 3, 5)
    plt.imshow(cleaned_segmented, cmap='gray')
    plt.title('Cleaned Segmentation Mask')
    plt.axis('off')

    plt.subplot(2, 3, 6)
    plt.imshow(final_segmented)
    plt.title('Final Segmented Image')
    plt.axis('off')

    plt.show()

# Example usage
segment_image('/content/Group 1 R1 150.jpg', k=5)

