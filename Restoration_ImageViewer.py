import os
import math
import cv2
import numpy as np
from datetime import datetime

def onMouseMain(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global mouse_y, mouse_x
        mouse_y, mouse_x = y, x
    if event == cv2.EVENT_MOUSEWHEEL:
        global box_min, box_max, box_step
        global box_h, box_w
        global box_mode, box_ratios
        if flags < 0:
            new_h = max(box_min, box_h - box_step)
            new_w = int(new_h * box_ratios[box_mode])
            box_h, box_w = new_h, new_w
        else:
            new_h = min(box_max, box_h + box_step)
            new_w = int(new_h * box_ratios[box_mode])
            box_h, box_w = new_h, new_w

def onMouseSub(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        global mouse_y, mouse_x
        mouse_y, mouse_x = y, x
    if event == cv2.EVENT_MOUSEWHEEL:
        global box_min, box_max, box_step
        global box_size
        if flags < 0:
            box_size = max(box_min, box_size - box_step)
        else:
            box_size = min(box_max, box_size + box_step)

# Basic Configuration
result_names = ['SRCNN', 'EDSR', 'RCAN', 'RRDB', 'Ours', 'HR']
result_paths = ['Set5_SRCNN', 'Set5_EDSR', 'Set5_RCAN', 'Set5_RRDN', 'Set5_Ours', 'Set5_HR']
image_name = 'baby.png'
main_index = -1
n_cols = 3
n_rows = math.ceil(len(result_names) / n_cols)
win_h = 720
box_min, box_max, box_step = int(win_h * 0.1), win_h, int(win_h * 0.01)
box_thickness, box_color = 2, (0, 0, 255)
sub_num, sub_colors = 3, [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
pad_size, pad_color = 2, (0, 0, 0)
sub_size = int(win_h / (n_rows * sub_num))
show_name = True
crop_path = 'crops\%s_%s' % (os.path.splitext(image_name.replace('/', '_'))[0], datetime.now().strftime('%Y%m%d%H%M%S'))
if not os.path.exists(crop_path):
    os.makedirs(crop_path, exist_ok=True)

# Prepare Images
result_images = []
for i in range(len(result_names)):
    image = cv2.imread('%s/%s' % (result_paths[i], image_name))
    result_images.append(image)
image_h, image_w, _ = result_images[main_index].shape
wimage_h, wimage_w = win_h, int(image_w * (win_h / image_h))
wimage = cv2.resize(result_images[main_index], (wimage_w, wimage_h), interpolation=cv2.INTER_CUBIC)

# Crop Main Image (Optional)
box_h, box_w = wimage_h, wimage_w
box_mode = 0
box_ratios = [box_w / box_h, 1 / 1, 4 / 3, 16 / 9]
mouse_y, mouse_x = wimage_h // 2, wimage_w // 2
flag = True
cv2.namedWindow('Crop Main Image')
cv2.setMouseCallback('Crop Main Image', onMouseMain)
while True:
    box_y1, box_x1 = min(max(0, mouse_y - box_h // 2), wimage_h - box_h), min(max(0, mouse_x - box_w // 2), wimage_w - box_w)
    box_y2, box_x2 = box_y1 + box_h, box_x1 + box_w
    canvas = wimage.copy()
    canvas = cv2.rectangle(canvas, (box_x1, box_y1), (box_x2, box_y2), box_color, box_thickness)
    cv2.imshow('Crop Main Image', canvas)
    key = cv2.waitKey(1)
    if key == ord('1') or key == ord('2') or key == ord('3') or key == ord('4'):
        box_mode = key - ord('1')
        if wimage_h < wimage_w:
            box_h, box_w = min(box_h, box_w), int(min(box_h, box_w) * box_ratios[box_mode])
        else:
            box_h, box_w = int(min(box_h, box_w) / box_ratios[box_mode]), min(box_h, box_w)
        continue
    if key == ord('s'):
        ratio = image_h / wimage_h
        main_y1, main_x1 = max(0, int(box_y1 * ratio)), max(0, int(box_x1 * ratio))
        main_y2, main_x2 = min(image_h, int(box_y2 * ratio)), min(image_w, int(box_x2 * ratio))        
        break
    if key == ord('q'):
        cv2.destroyAllWindows()
        exit()
cv2.destroyAllWindows()

# Save Boxed Images
for i in range(len(result_names)):
    rimage_h, rimage_w, _ = result_images[i].shape
    if rimage_h != image_h or rimage_w != image_w:
        result_images[i] = cv2.resize(result_images[i], (image_w, image_h), interpolation=cv2.INTER_CUBIC)
    result_images[i] = result_images[i][main_y1:main_y2, main_x1:main_x2]
    cv2.imwrite('%s/main_%s.png' % (crop_path, result_names[i]), result_images[i])

# Prepare Boxed Main Image
bimage = result_images[main_index].copy()
bimage_h, bimage_w, _ = bimage.shape
wimage_h, wimage_w = win_h, int(bimage_w * (win_h / bimage_h))
wimage = cv2.resize(bimage, (wimage_w, wimage_h), interpolation=cv2.INTER_CUBIC)

# Crop Sub Image
box_size = int(win_h * 0.2)
sub_index = 0
sub_positions = []
scanvas_h, scanvas_w = sub_size * n_rows * sub_num + pad_size * (n_rows * sub_num - 1), sub_size * n_cols + pad_size * n_cols
scanvas = np.full((scanvas_h, scanvas_w, 3), pad_color, dtype='uint8')
scanvas_h, scanvas_w = win_h, int(scanvas_w * (win_h / scanvas_h))
mouse_y, mouse_x = wimage_h // 2, wimage_w // 2
cv2.namedWindow('Crop Sub Image')
cv2.setMouseCallback('Crop Sub Image', onMouseSub)
while True:
    box_y1, box_x1 = min(max(0, mouse_y - box_size // 2), wimage_h - box_size), min(max(0, mouse_x - box_size // 2), wimage_w - box_size)
    box_y2, box_x2 = box_y1 + box_size, box_x1 + box_size
    canvas = wimage.copy()
    ratio = bimage_h / wimage_h
    sub_y1, sub_x1 = max(0, int(box_y1 * ratio)), max(0, int(box_x1 * ratio))
    sub_y2, sub_x2 = min(bimage_h, int(box_y2 * ratio)), min(bimage_w, int(box_x2 * ratio))
    for i in range(len(result_names)):
        sub_y, sub_x = divmod(sub_index * n_rows * n_cols + i, n_cols)
        pos_x1, pos_y1 = sub_size * sub_x + pad_size * (sub_x + 1), sub_size * sub_y + pad_size * sub_y
        pos_x2, pos_y2 = pos_x1 + sub_size, pos_y1 + sub_size
        simage = result_images[i].copy()
        simage = simage[sub_y1:sub_y2, sub_x1:sub_x2]
        simage = cv2.resize(simage, (sub_size, sub_size), interpolation=cv2.INTER_CUBIC)
        cv2.putText(simage, result_names[i], (1, 14), cv2.FONT_HERSHEY_PLAIN, 1.2, sub_colors[sub_index], 1)
        scanvas[pos_y1:pos_y2, pos_x1:pos_x2] = simage
    rscanvas = cv2.resize(scanvas, (scanvas_w, scanvas_h), interpolation=cv2.INTER_CUBIC)
    canvas = np.concatenate((canvas, rscanvas), axis=1)
    cv2.rectangle(canvas, (box_x1, box_y1), (box_x2, box_y2), sub_colors[sub_index], box_thickness)
    cv2.imshow('Crop Sub Image', canvas)
    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.rectangle(wimage, (box_x1, box_y1), (box_x2, box_y2), sub_colors[sub_index], box_thickness)
        ratio = bimage_h / wimage_h
        sub_y1, sub_x1 = max(0, int(box_y1 * ratio)), max(0, int(box_x1 * ratio))
        sub_y2, sub_x2 = min(bimage_h, int(box_y2 * ratio)), min(bimage_w, int(box_x2 * ratio))
        sub_positions.append((sub_y1, sub_x1, sub_y2, sub_x2))
        for i in range(len(result_names)):
            sub_y, sub_x = divmod(sub_index * n_rows * n_cols + i, n_cols)
            pos_x1, pos_y1 = sub_size * sub_x + pad_size * (sub_x + 1), sub_size * sub_y + pad_size * sub_y
            pos_x2, pos_y2 = pos_x1 + sub_size, pos_y1 + sub_size
            simage = result_images[i].copy()
            simage = simage[sub_y1:sub_y2, sub_x1:sub_x2]
            simage = cv2.resize(simage, (sub_size, sub_size), interpolation=cv2.INTER_CUBIC)
            cv2.putText(simage, result_names[i], (1, 14), cv2.FONT_HERSHEY_PLAIN, 1.2, sub_colors[sub_index], 1)
            scanvas[pos_y1:pos_y2, pos_x1:pos_x2] = simage
        sub_index += 1
        if sub_index == sub_num:
            break
    if key == ord('q'):
        cv2.destroyAllWindows()
        exit()
cv2.destroyAllWindows()

# Save Sub Images
cimage = result_images[main_index].copy()
cimage_h, cimage_w, _ = cimage.shape
sub_size = int(cimage_h / (n_rows * sub_num))
scanvas_h, scanvas_w = sub_size * n_rows * sub_num + pad_size * (n_rows * sub_num - 1), sub_size * n_cols + pad_size * n_cols
scanvas = np.full((scanvas_h, scanvas_w, 3), pad_color, dtype='uint8')
scanvas_h, scanvas_w = cimage_h, int(scanvas_w * (cimage_h / scanvas_h))
for i in range(sub_num):
    box_y1, box_x1, box_y2, box_x2 = sub_positions[i]
    cv2.rectangle(cimage, (box_x1, box_y1), (box_x2, box_y2), sub_colors[i], box_thickness)
    for j in range(len(result_names)):
        simage = result_images[j].copy()
        simage = simage[box_y1:box_y2, box_x1:box_x2]
        cv2.imwrite('%s/sub_%d_%s.png' % (crop_path, i + 1, result_names[j]), simage)
        sub_y, sub_x = divmod(i * n_rows * n_cols + j, n_cols)
        pos_x1, pos_y1 = sub_size * sub_x + pad_size * (sub_x + 1), sub_size * sub_y + pad_size * sub_y
        pos_x2, pos_y2 = pos_x1 + sub_size, pos_y1 + sub_size
        simage = cv2.resize(simage, (sub_size, sub_size), interpolation=cv2.INTER_CUBIC)
        if show_name:
            cv2.putText(simage, result_names[j], (1, 14), cv2.FONT_HERSHEY_PLAIN, 1.2, sub_colors[i], 1)
        scanvas[pos_y1:pos_y2, pos_x1:pos_x2] = simage
rscanvas = cv2.resize(scanvas, (scanvas_w, scanvas_h), interpolation=cv2.INTER_CUBIC)
cimage = np.concatenate((cimage, rscanvas), axis=1)
cv2.imwrite('%s/main.png' % crop_path, cimage)
