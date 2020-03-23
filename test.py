import string

s = ''
for i in range(128):
    s += chr(i)
print(s)
print(string.printable)
