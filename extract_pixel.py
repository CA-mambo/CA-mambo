from PIL import Image
import os

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 打开图片
img = Image.open(os.path.join(script_dir, 'mambo.png')).convert('RGBA')
pixels = img.load()
width, height = img.size

# 找到非白色背景的边界
min_x, min_y = width, height
max_x, max_y = 0, 0

for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        # 非白色且非透明
        if not (r > 240 and g > 240 and b > 240) and a > 0:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

subject_w = max_x - min_x + 1
subject_h = max_y - min_y + 1
print(f'Subject bounds: ({min_x}, {min_y}) - ({max_x}, {max_y})')
print(f'Subject size: {subject_w} x {subject_h}')

# 裁剪主体区域
subject = img.crop((min_x, min_y, max_x + 1, max_y + 1))

# 创建 32x32 的 pixel art
target_size = 32
# 先将主体区域缩小到 32x32，使用 NEAREST 保持像素风格
pixel_art = subject.resize((target_size, target_size), Image.NEAREST)

# 去除白色背景（变为透明）
pa_pixels = pixel_art.load()
for y in range(target_size):
    for x in range(target_size):
        r, g, b, a = pa_pixels[x, y]
        if r > 240 and g > 240 and b > 240:
            pa_pixels[x, y] = (0, 0, 0, 0)

# 保存结果
output_32 = os.path.join(script_dir, 'mambo_32x32.png')
output_preview = os.path.join(script_dir, 'mambo_32x32_preview.png')
pixel_art.save(output_32, 'PNG')
print('Saved mambo_32x32.png')

# 放大预览（可选）- 放大到 512x512 方便查看
preview = pixel_art.resize((512, 512), Image.NEAREST)
preview.save(output_preview, 'PNG')
print('Saved mambo_32x32_preview.png (512x512 preview)')
