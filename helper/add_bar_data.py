import argparse
import fileinput
import os

parser = argparse.ArgumentParser(description='Add health bar data')
parser.add_argument('--path', metavar='path', default='training/train_bar/labels/', type=str, nargs='?',
                    help='path to the labels dir')
args = parser.parse_args()
path = args.path
bar_data = '''5 0.415234 0.081250 0.016406 0.034722
5 0.437891 0.081250 0.021094 0.040278
5 0.561328 0.077083 0.021094 0.040278
5 0.584375 0.079861 0.018750 0.029167
0 0.645703 0.117361 0.196094 0.031944
0 0.296875 0.117361 0.310937 0.031944
1 0.569141 0.150694 0.042969 0.026389
1 0.432031 0.152778 0.043750 0.025000
2 0.379297 0.175694 0.088281 0.009722
2 0.612500 0.174306 0.100000 0.012500
3 0.208203 0.941667 0.149219 0.025000
3 0.799609 0.943056 0.114844 0.030556
4 0.674609 0.943750 0.133594 0.026389
4 0.335938 0.941667 0.107813 0.025000
7 0.437891 0.174306 0.028906 0.009722
7 0.554688 0.173611 0.014063 0.011111
'''
for file in os.listdir(path):
     if file != "classes.txt":
        f = os.path.join(path, file)
        #for line in fileinput.input(f, inpace=True):
        print(f)
        with open(f,'w') as file:
            file.write(bar_data)
            #print(f"appending to {str(f)}")
