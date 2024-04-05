import cv2
from os.path import isfile, join
from os import listdir
import random
from pathlib import Path

asuka_spell_path = "training/spells"
orig_img_path = "training/train_bar/images"
dest_img_path = "training/train_asuka/images"
dest_labels_path = "training/train_asuka/labels"

spells = [asuka_spell_path + "/" + f for f in listdir(asuka_spell_path) if isfile(join(asuka_spell_path, f))]
frames = [orig_img_path + "/" + f for f in listdir(orig_img_path) if isfile(join(orig_img_path, f))]
for spell in spells:
    print(Path(spell).stem)

spell_size = (30, 40)
initial_spell_location = [(320, 620),(840, 620)]
frame_size = (1280, 720)
for frame in frames:
    r = random.random()
    sides = []
    if r < 0.45:
        sides = [0]
    elif r < 0.9:
        sides = [1]
    else:
        sides = [0,1]
    orig_img = cv2.imread(frame)
    for side in sides:
        curr_spells = random.choices(list(enumerate(spells)), k=4)
        frame_name = Path(frame).stem
        
        f = open(f"{dest_labels_path}/{frame_name}.txt", 'a')
        for i, spell in list(enumerate(curr_spells)):
            spell_img =  cv2.resize(cv2.imread(spell[1], flags=cv2.IMREAD_UNCHANGED), spell_size, interpolation = cv2.INTER_AREA)
            spell_class = spell[0]
            # if random.random() < 0.05:
            #     spell_class = 26
            #     spell_img = cv2.cvtColor(spell_img, cv2.COLOR_RGBA2GRAY)
            #     spell_img = cv2.cvtColor(spell_img, cv2.COLOR_GRAY2RGBA)
            x1, x2 = initial_spell_location[side][0] + i * spell_size[0], initial_spell_location[side][0] + i * spell_size[0] + spell_size[0]
            y1, y2 = initial_spell_location[side][1], initial_spell_location[side][1] + spell_size[1]
            print(f'{x1} {x2} {y1} {y2}')
            alpha_s = spell_img[:, :, 3]/255.0
            alpha_l = 1.0-alpha_s 
            for c in range (0, 3):
                orig_img[y1:y2, x1:x2, c] = (alpha_s * spell_img[:, :, c] +
                                    alpha_l * orig_img[y1:y2, x1:x2, c])
            print(f"{spell_class} {round(x1/frame_size[0],5)} {round(y1/frame_size[1], 5)} {round((x2-x1)/frame_size[0], 5)} {round((y2-y1)/frame_size[1], 5)}")
            f.write(f"{spell_class} {(x1 + x2)/2/frame_size[0]} {(y1+y2)/2/frame_size[1]} {(x2-x1)/frame_size[0]} {(y2-y1)/frame_size[1]}\n")
            cv2.imshow("main", orig_img)
            cv2.waitKey(1)
        f.close()
    cv2.imwrite(f"{dest_img_path}/{frame_name}.jpg", orig_img)

# s_img = cv2.imread("smaller_image.png")
# l_img = cv2.imread("larger_image.jpg")
# x_offset=y_offset=50
# l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img