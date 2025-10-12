#!/usr/bin/env python3
"""
Create minimal test data for catpic tests.
Run this if test images are missing.

Usage:
    cd python
    uv run python create_test_data.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

def create_test_data_dir():
    """Create test data directory if it doesn't exist."""
    # Check which directory the tests expect
    if Path('tests/fixtures').exists():
        data_dir = Path('tests/fixtures')
    else:
        # Default to fixtures to match test expectations
        data_dir = Path('tests/fixtures')
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def create_solid_image(path, width, height, color):
    """Create a solid color image."""
    img = Image.new('RGB', (width, height), color)
    img.save(path)
    print(f"Created: {path}")

def create_gradient_image(path, width, height):
    """Create a gradient image."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r = int(255 * x / width)
            g = int(255 * y / height)
            b = 128
            pixels[x, y] = (r, g, b)
    
    img.save(path)
    print(f"Created: {path}")

def create_checkerboard_image(path, width, height, cell_size):
    """Create a checkerboard pattern."""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    for y in range(0, height, cell_size):
        for x in range(0, width, cell_size):
            if (x // cell_size + y // cell_size) % 2 == 0:
                draw.rectangle([x, y, x + cell_size, y + cell_size], fill='black')
    
    img.save(path)
    print(f"Created: {path}")

def create_test_animation(path, width, height, frames):
    """Create a simple animated GIF."""
    images = []
    
    for i in range(frames):
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw a moving circle
        x = int(width * i / frames)
        y = height // 2
        radius = min(width, height) // 8
        
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                     fill='red', outline='black')
        
        images.append(img)
    
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=100,  # 100ms per frame
        loop=0
    )
    print(f"Created: {path}")

def create_small_test_images(data_dir):
    """Create small test images for unit tests."""
    # Tiny images for quick tests
    create_solid_image(data_dir / 'red_4x4.png', 4, 4, (255, 0, 0))
    create_solid_image(data_dir / 'green_4x4.png', 4, 4, (0, 255, 0))
    create_solid_image(data_dir / 'blue_4x4.png', 4, 4, (0, 0, 255))
    
    # Slightly larger for visual testing
    create_solid_image(data_dir / 'red_16x16.png', 16, 16, (255, 0, 0))
    create_gradient_image(data_dir / 'gradient_16x16.png', 16, 16)
    create_checkerboard_image(data_dir / 'checker_16x16.png', 16, 16, 4)

def create_medium_test_images(data_dir):
    """Create medium-sized test images for display testing."""
    create_solid_image(data_dir / 'red_64x64.jpg', 64, 64, (255, 0, 0))
    create_gradient_image(data_dir / 'gradient_64x64.jpg', 64, 64)
    create_checkerboard_image(data_dir / 'checker_64x64.png', 64, 64, 8)

def create_test_animations(data_dir):
    """Create test animations."""
    create_test_animation(data_dir / 'bounce_small.gif', 32, 32, 8)
    create_test_animation(data_dir / 'bounce_medium.gif', 64, 64, 16)

def create_edge_case_images(data_dir):
    """Create edge case test images."""
    # 1x1 pixel
    create_solid_image(data_dir / 'tiny_1x1.png', 1, 1, (128, 128, 128))
    
    # Very wide
    create_gradient_image(data_dir / 'wide_128x8.png', 128, 8)
    
    # Very tall
    create_gradient_image(data_dir / 'tall_8x128.png', 8, 128)
    
    # Odd dimensions
    create_solid_image(data_dir / 'odd_13x17.png', 13, 17, (200, 100, 50))

def main():
    print("Creating test data for catpic...")
    print()
    
    data_dir = create_test_data_dir()
    
    print("\n1. Creating small test images...")
    create_small_test_images(data_dir)
    
    print("\n2. Creating medium test images...")
    create_medium_test_images(data_dir)
    
    print("\n3. Creating test animations...")
    create_test_animations(data_dir)
    
    print("\n4. Creating edge case images...")
    create_edge_case_images(data_dir)
    
    print("\n✓ Test data created successfully!")
    print(f"Location: {data_dir.absolute()}")
    print(f"Total files: {len(list(data_dir.glob('*')))}")
    
    # List all created files
    print("\nCreated files:")
    for f in sorted(data_dir.glob('*')):
        size = f.stat().st_size
        print(f"  {f.name:30s} ({size:,} bytes)")

if __name__ == '__main__':
    main()
