import os

source = "training/train_asuka"
dest = "training/valid_asuka"

all_image_names = sorted(os.listdir(f"{dest}/images/"))
for image_name in all_image_names:
    #Create an empty file if there is none, most likely a negative case
    file_name = image_name.split('.jpg')[0]
    lbl_source = f"{source}/labels/{file_name}.txt"
    if (os.path.exists(lbl_source)):
        os.remove(f"{source}/images/{image_name}")
        os.remove(lbl_source)
        print(f"removing {lbl_source}")
        #print (lbl_source)
