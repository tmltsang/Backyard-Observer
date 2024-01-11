import argparse
import fileinput
import os

parser = argparse.ArgumentParser(description='Remove class from yolo v8')
parser.add_argument('--path', metavar='path', default='training/train/labels/', type=str, nargs='?',
                    help='path to the labels dir')
parser.add_argument('--class_path', default='training/train/labels/classes.txt', type=str, nargs='?', help='path to classes.txt')
parser.add_argument('class_to_remove', metavar='class', type=str, nargs='?', help='class_to_remove')
args = parser.parse_args()
path = args.path

class_f = open(args.class_path, 'r')
classes = list(map(str.rstrip, class_f.readlines()))
try:
    index_to_remove = classes.index(args.class_to_remove)
    classes.remove(args.class_to_remove)
except ValueError:
    print(f"{args.class_to_remove} does not exist in {args.class_path}")
    exit()
print(args.class_to_remove)
class_f.close()

#Just a dry-run for now
for file in os.listdir(path):
     if file != "classes.txt":
        f = os.path.join(path, file)
        #for line in fileinput.input(f, inpace=True):
        print(f)
        with open(f,'r') as file:
            update_file = ''
            for line in file:
                line_split = line.split(' ')
                if int(line_split[0]) > index_to_remove:
                    line_split[0] = str(int(line_split[0]) - 1)
                    update_file += ' '.join(line_split)
            print(update_file)
        with open(f, 'w') as file:
            file.write(update_file)

#finally remove class from classes.txt
with open(args.class_path, 'w') as class_f:
   class_f.write("\n".join(classes))
