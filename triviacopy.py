import os

path = 'C:/Users/gregj/Google Drive/trivia/out'
filepath = os.path.join(path, "test2.txt")

os.chdir(path)

print filepath
print os.curdir
print os.name
print os.environ


fh = open("test2.txt", 'a')
fh.write("this is a test\n")
fh.close


