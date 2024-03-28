import re
from os import listdir, rename
from os.path import exists

video_path = "training/videos/gg_matches/"
for f in listdir(video_path):
    #print(f)
    x = re.search("[^(]*(\([^(]*\s|\()([^)]+)\)[^(]*(\([^(]*\s|\()([^)]+)\).*", f)
    counter = 1
    new_name = "%s_%s_%d.mkv" % (x.group(2).replace('.','').lower(), x.group(4).replace('.','').lower(), counter)
    full_path = video_path + new_name
    while exists(full_path):
        counter += 1
        new_name = "%s_%s_%d.mkv" % (x.group(2).lower(), x.group(4).lower(), counter)
        full_path = video_path + new_name
    print("Moving %s to %s" % (f, full_path))
    rename(video_path+f, full_path)