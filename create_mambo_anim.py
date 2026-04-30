from PIL import Image
import base64
from io import BytesIO

def create_mambo_frames():
    """
    Create two frames of walking mambo pixel art from the original 1024x1024 image.
    Frame 0: Original pose
    Frame 1: Walking pose (feet alternate)
    """
    img = Image.open("mambo.webp").convert('RGBA')
    img_16 = img.resize((16, 16), Image.NEAREST)
    
    # Remove white background
    pixels = img_16.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = pixels[x, y]
            if r > 240 and g > 240 and b > 240:
                pixels[x, y] = (0, 0, 0, 0)
    
    # Frame 0: Original
    frame0 = img_16.copy()
    
    # Frame 1: Walking animation (swap feet pixels)
    frame1 = img_16.copy()
    f1_pixels = frame1.load()
    
    # Find the feet area (bottom rows of the character)
    # Typically feet are around rows 13-15 in a 16x16 pixel art
    # We'll shift the feet pixels to simulate walking
    feet_y_start = 13
    for x in range(16):
        for y in range(feet_y_start, 16):
            # Copy the original pixels but shift them slightly
            if y + 1 < 16:
                f1_pixels[x, y] = pixels[x, y + 1] if y + 1 < 16 else (0, 0, 0, 0)
            else:
                f1_pixels[x, y] = (0, 0, 0, 0)
    
    # Now let's also add a subtle leg movement by shifting some pixels
    # This is a simplified walking animation
    for x in [6, 7, 8, 9]:  # Approximate leg area
        if pixels[x, 12] != (0, 0, 0, 0):  # If there's a leg pixel
            f1_pixels[x, 12] = pixels[x, 13] if pixels[x, 13] != (0, 0, 0, 0) else pixels[x, 12]
    
    return [frame0, frame1]

def create_animated_gif(frames, size=18):
    """Create an animated GIF from frames, scaled to target size."""
    scaled_frames = [f.resize((size, size), Image.NEAREST) for f in frames]
    
    buffered = BytesIO()
    scaled_frames[0].save(
        buffered,
        format='GIF',
        save_all=True,
        append_images=scaled_frames[1:],
        duration=500,  # 500ms per frame
        loop=0,
        transparency=0
    )
    
    b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/gif;base64,{b64}"

def create_two_frame_base64(image_path, target_size=18):
    """Process image and return two-frame animation as base64 GIF."""
    try:
        img = Image.open(image_path).convert('RGBA')
        img_16 = img.resize((16, 16), Image.NEAREST)
        
        # Remove white background
        pixels = img_16.load()
        for y in range(16):
            for x in range(16):
                r, g, b, a = pixels[x, y]
                if r > 240 and g > 240 and b > 240:
                    pixels[x, y] = (0, 0, 0, 0)
        
        # Frame 0: Original
        frame0 = img_16.copy()
        
        # Frame 1: Walking pose
        # We need to analyze the actual pixel structure to make a proper walking animation
        # Let's find where the legs/feet are
        leg_pixels = []
        for y in range(12, 16):
            for x in range(16):
                if pixels[x, y] != (0, 0, 0, 0):
                    leg_pixels.append((x, y, pixels[x, y]))
        
        # Create frame1 with animated legs
        frame1 = img_16.copy()
        f1_pixels = frame1.load()
        
        # Simple animation: shift leg pixels to simulate walking
        # Find left and right leg
        left_leg_x = min([p[0] for p in leg_pixels]) if leg_pixels else 0
        right_leg_x = max([p[0] for p in leg_pixels]) if leg_pixels else 15
        
        # Move left leg up/down
        for x, y, color in leg_pixels:
            if x <= 7:  # Left leg
                # Shift up by 1 pixel to simulate stepping
                new_y = max(0, y - 1)
                f1_pixels[x, new_y] = color
                f1_pixels[x, y] = (0, 0, 0, 0)
            else:  # Right leg
                # Keep in place or shift down
                new_y = min(15, y + 1)
                f1_pixels[x, new_y] = color
                f1_pixels[x, y] = (0, 0, 0, 0)
        
        # Scale frames
        frame0_scaled = frame0.resize((target_size, target_size), Image.NEAREST)
        frame1_scaled = frame1.resize((target_size, target_size), Image.NEAREST)
        
        # Create animated GIF
        buffered = BytesIO()
        frame0_scaled.save(
            buffered,
            format='GIF',
            save_all=True,
            append_images=[frame1_scaled],
            duration=400,
            loop=0,
            transparency=0
        )
        
        b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/gif;base64,{b64}"
    except Exception as e:
        print(f"Warning: Could not create animated mambo. {e}")
        return None

if __name__ == "__main__":
    result = create_two_frame_base64("mambo.webp", target_size=18)
    if result:
        print("Successfully created animated mambo!")
        print(f"Base64 length: {len(result)}")
        # Save to file for testing
        with open("mambo_animated.gif", "wb") as f:
            import base64
            f.write(base64.b64decode(result.split(',')[1]))
        print("Saved mambo_animated.gif")
