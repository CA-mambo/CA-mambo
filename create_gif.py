from PIL import Image
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# 打开三张图片
left_path = os.path.join(script_dir, 'mambo_32x32_left.png')
stand_path = os.path.join(script_dir, 'mambo_32x32_stand.png')
right_path = os.path.join(script_dir, 'mambo_32x32_right.png')

print('Loading images...')
left = Image.open(left_path).convert('RGBA')
stand = Image.open(stand_path).convert('RGBA')
right = Image.open(right_path).convert('RGBA')

print(f'left: {left.size}')
print(f'stand: {stand.size}')
print(f'right: {right.size}')

# 确保尺寸一致
assert left.size == stand.size == right.size, "Image sizes don't match!"


frames =  [left, stand, right]

# 保存 GIF 动画（带透明背景）
output_path = os.path.join(script_dir, 'mambo_32x32.gif')
print(f'Saving GIF to {output_path}...')

# 转换为 P 模式并设置透明索引
frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=400,
    loop=0,
    transparency=0,  # 调色板索引 0 作为透明色
    disposal=2,  # 每帧后恢复为背景
    optimize=True
)
print('Done! Saved mambo_32x32.gif with transparent background')