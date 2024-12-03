import base64
import io

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


# Define function to save the output
def save_image(base64_image, output_file):
    image_bytes = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_bytes))
    image.save(output_file)


# Define different types of plot function
def plot_images(
    generated_images, ref_image_path=None, original_title=None, processed_title=None
):
    if ref_image_path:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    else:
        fig, axes = plt.subplots(1, 1, figsize=(6, 5))
        axes = [axes]

    if ref_image_path:
        reference_image = Image.open(ref_image_path)
        max_size = (512, 512)
        reference_image.thumbnail(max_size)
        axes[0].imshow(np.array(reference_image))
        axes[0].set_title(original_title or "Reference Image")
        axes[0].axis("off")

    generated_image_index = 1 if ref_image_path else 0
    axes[generated_image_index].imshow(np.array(generated_images[0]))
    axes[generated_image_index].set_title(processed_title or "Processed Image")
    axes[generated_image_index].axis("off")

    plt.tight_layout()
    plt.show()


def plot_image_conditioning(
    ref_image_path,
    base_images=None,
    prompt=None,
    generated_images=None,
    control_strength_values=None,
    comparison_mode=False,
):
    if comparison_mode:
        num_images = len(control_strength_values) + 1
        fig, axes = plt.subplots(1, num_images, figsize=((num_images) * 4, 5))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    reference_image = Image.open(ref_image_path)
    max_size = (300, 300)
    reference_image.thumbnail(max_size)

    axes[0].imshow(np.array(reference_image))
    axes[0].set_title("Condition Image")
    axes[0].axis("off")

    if comparison_mode:
        if generated_images is None or len(generated_images) != len(
            control_strength_values
        ):
            raise ValueError(
                "The length of generated_images must match the length of control_strength_values."
            )
        for i, (image, strength) in enumerate(
            zip(generated_images, control_strength_values), start=1
        ):
            axes[i].imshow(np.array(image))
            axes[i].set_title(f"Control Strength: {strength}")
            axes[i].axis("off")
    else:
        axes[1].imshow(np.array(base_images[0]))
        axes[1].set_title("Result of Conditioning")
        axes[1].axis("off")

    if prompt:
        print("Prompt:{}\n".format(prompt))

    plt.tight_layout()
    plt.show()


def plot_color_conditioning(base_images, color_codes, prompt, ref_image_path=None):
    if ref_image_path:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    else:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot Hex Color
    num_colors = len(color_codes)
    color_width = 0.8 / num_colors
    for i, color_code in enumerate(color_codes):
        x = i * color_width
        rect = plt.Rectangle(
            (x, 0), color_width, 1, facecolor=f"{color_code}", edgecolor="white"
        )
        axes[0].add_patch(rect)
    axes[0].set_xlim(0, 0.8)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("Color Codes")
    axes[0].axis("off")

    if ref_image_path:
        reference_image = Image.open(ref_image_path)
        max_size = (300, 300)
        reference_image.thumbnail(max_size)
        axes[1].imshow(np.array(reference_image))
        axes[1].set_title("Reference Image")
        axes[1].axis("off")
        image_index = 2
    else:
        image_index = 1

    axes[image_index].imshow(np.array(base_images[0]))
    if ref_image_path:
        axes[image_index].set_title(f"Image Generated Based on Reference")
    else:
        axes[image_index].set_title(f"Image Generated")
    axes[image_index].axis("off")

    print(f"Prompt: {prompt}\n")
    plt.tight_layout()
    plt.show()


def create_color_palette_image(
    colors, width=400, height=50, border_color="#cccccc", border_width=2
):
    """
    Create a color palette image from a list of hex color codes.

    Args:
        colors (list): List of hex color codes (e.g., ["#FFFFFF", "#B066AC"])
        width (int): Total width of the image in pixels
        height (int): Total height of the image in pixels
        border_color (str): Hex color code for the border
        border_width (int): Width of the border in pixels

    Returns:
        PIL.Image: Color palette image with border
    """
    # Convert border color from hex to RGB
    border_rgb = tuple(int(border_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))

    # Create image with border (add border_width*2 to dimensions to account for borders)
    total_width = width + (border_width * 2)
    total_height = height + (border_width * 2)
    img = Image.new("RGB", (total_width, total_height), border_rgb)

    # Calculate the width of each color segment
    num_colors = len(colors)
    segment_width = width // num_colors

    # Convert hex colors to RGB
    rgb_colors = [
        tuple(int(color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        for color in colors
    ]

    # Create the inner image (without border)
    inner_img = Image.new("RGB", (width, height))

    # Draw each color segment
    for i, color in enumerate(rgb_colors):
        start_x = i * segment_width
        end_x = start_x + segment_width if i < num_colors - 1 else width

        # Create and paste each color segment
        segment = Image.new("RGB", (end_x - start_x, height), color)
        inner_img.paste(segment, (start_x, 0))

    # Paste the inner image onto the bordered image
    img.paste(inner_img, (border_width, border_width))

    return img


def plot_images_for_comparison(
    ref_image_path=None,
    base_images=None,
    custom_images=None,
    generated_images=None,
    labels=None,
    prompt=None,
    comparison_mode=False,
    title_prefix="Image",
):
    if comparison_mode:
        num_images = len(generated_images) + (1 if ref_image_path else 0)
        _, axes = plt.subplots(1, num_images, figsize=(num_images * 4, 5))
    else:
        _, axes = plt.subplots(1, 3, figsize=(15, 5))

    if not isinstance(axes, np.ndarray):
        axes = [axes]

    if ref_image_path:
        reference_image = Image.open(ref_image_path)
        max_size = (300, 300)
        reference_image.thumbnail(max_size)

        axes[0].imshow(np.array(reference_image))
        axes[0].set_title("Reference Image")
        axes[0].axis("off")

    if comparison_mode:
        start_index = 1 if ref_image_path else 0
        for i, img in enumerate(generated_images):
            axes[i + start_index].imshow(np.array(img))
            title = f"{title_prefix} {labels[i]}" if labels else f"{title_prefix} {i+1}"
            axes[i + start_index].set_title(title)
            axes[i + start_index].axis("off")
    else:
        if base_images:
            axes[1].imshow(np.array(base_images[0]))
            axes[1].set_title("Without Reference")
            axes[1].axis("off")

        if custom_images:
            axes[2].imshow(np.array(custom_images[0]))
            axes[2].set_title("With Reference")
            axes[2].axis("off")

    if prompt:
        print(f"Prompt: {prompt}\n")
    plt.tight_layout()
    plt.show()
