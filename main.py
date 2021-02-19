import os
import math
import cv2
import numpy as np


def get_from_entry(s: str):
    return s[s.index('=') + 1:].strip()


def round_down(number: float):
    return math.floor(number + 0.5)


# 统计处理数量
cnt = 0
# 读取脚本所在文件夹下所有文件
for file_name in os.listdir(os.getcwd()):
    # 如果为 txt 文件
    if file_name.endswith('.txt'):
        print('正在处理 {}'.format(file_name[:-4]))
        # 读取文件
        f = open(file_name)
        lines = f.readlines()
        f.close()
        # 变量定义
        texture_name = alpha_texture_name = ''
        x = y = width = height = cropped_width = cropped_height = -1
        # 遍历文件每一行
        for index, line in enumerate(lines):
            # 为图片宽度和高度赋值
            if 'Rectf m_Rect' in line:
                for entry in lines[index + 1:index + 5]:
                    if 'width' in entry:
                        width = round_down(float(get_from_entry(entry)))
                    if 'height' in entry:
                        height = round_down(float(get_from_entry(entry)))
            # 为图片原材质赋值
            if 'PPtr<Texture2D> texture' in line:
                for entry in lines[index + 1:index + 3]:
                    if 'm_PathID' in entry:
                        texture_name = get_from_entry(entry) + '.png'
            # 为图片 alpha 通道材质赋值
            if 'PPtr<Texture2D> alphaTexture' in line:
                for entry in lines[index + 1:index + 3]:
                    if 'm_PathID' in entry:
                        alpha_texture_name = get_from_entry(entry) + '.png'
            # 为图片 x 坐标位置、y 坐标位置、裁剪宽度和裁剪高度赋值
            if 'Rectf textureRect' in line:
                for entry in lines[index + 1:index + 5]:
                    if 'x' in entry:
                        x = round_down(float(get_from_entry(entry)))
                    if 'y' in entry:
                        y = round_down(float(get_from_entry(entry)))
                    if 'width' in entry:
                        cropped_width = round_down(float(get_from_entry(entry)))
                    if 'height' in entry:
                        cropped_height = round_down(float(get_from_entry(entry)))
        if width == -1 or height == -1:
            raise Exception('图片的宽度或高度未定义，可能是导出文件的对应字段发生了改变')
        if texture_name == '' or alpha_texture_name == '':
            raise Exception('图片的原材质或 alpha 通道材质未定义，可能是导出文件的对应字段发生了改变')
        if x == -1 or y == -1:
            raise Exception('图片的 x 坐标位置或 y 坐标位置未定义，可能是导出文件的对应字段发生了改变')
        if cropped_width == -1 or cropped_height == -1:
            raise Exception('图片的裁剪宽度或裁剪高度未定义，可能是导出文件的对应字段发生了改变')
        # 读取原图
        texture = cv2.imread(texture_name)
        # 以灰度图模式读取 alpha 通道图
        alpha_texture = cv2.imread(alpha_texture_name, 0)
        # 获取原图宽高
        texture_height, texture_width, texture_channel = texture.shape
        # 将 alpha 通道图大小 resize 为原图大小
        alpha_texture = cv2.resize(alpha_texture, (texture_width, texture_height))
        # 根据裁剪宽度和裁剪高度将原图和 alpha 通道图进行裁剪
        cropped_texture = texture[texture_height - y - cropped_height:texture_height - y, x:x + cropped_width]
        cropped_alpha_texture = alpha_texture[texture_height - y - cropped_height:texture_height - y, x:x + cropped_width]
        # 分离 bgr 通道
        b, g, r = cv2.split(cropped_texture)
        # 根据宽度和高度新建 bgra 通道，alpha 通道值为 alpha 通道图的灰度值
        bgra = np.zeros((4, height, width), dtype=texture.dtype)
        bgra[0][height - cropped_height:height, 0:cropped_width] = b
        bgra[1][height - cropped_height:height, 0:cropped_width] = g
        bgra[2][height - cropped_height:height, 0:cropped_width] = r
        bgra[3][height - cropped_height:height, 0:cropped_width] = cropped_alpha_texture
        # 将 bgra 通道合并为图像
        matted_texture = cv2.merge(bgra)
        # 保存图像
        cv2.imwrite(file_name[:-4] + '.png', matted_texture)
        # 处理数量自增
        cnt += 1
# 输出处理数量
print('处理完成，共 {} 个文件'.format(cnt))
# 按任意键继续
os.system('pause')
