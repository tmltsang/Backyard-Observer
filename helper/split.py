import numpy
import random
import os

source = "training/train"
dest = "training/valid"

all_image_names = sorted(os.listdir(f"{source}/images/"))
valid_names = random.sample(all_image_names, int(len(all_image_names)/15))
for image_name in all_image_names:
    #Create an empty file if there is none, most likely a negative case
    file_name = image_name.split('.jpg')[0]
    lbl_source = f"{source}/labels/{file_name}.txt"
    if (os.path.exists(lbl_source) == False):
        f = open(lbl_source, "w") 


for image_name in valid_names:
    file_name = image_name.split('.jpg')[0]
    
    img_source = f"{source}/images/{image_name}"
    lbl_source = f"{source}/labels/{file_name}.txt"
    img_dest = f"{dest}/images/{image_name}"
    lbl_dest = f"{dest}/labels/{file_name}.txt"

    print(f"moving {img_source} to {img_dest}")
    print(f"moving {lbl_source} to {lbl_dest}")
    os.rename(img_source, img_dest)
    os.rename(lbl_source, lbl_dest)