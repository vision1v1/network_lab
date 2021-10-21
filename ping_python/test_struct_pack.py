import struct

my_type = 0

# 10 char
my_name = b'helloworld'

my_age = 30

# https://docs.python.org/3/library/struct.html#struct-format-strings
bytes = struct.pack('>I10sI', my_type, my_name, my_age)

print(bytes)

(t, n, a) = struct.unpack('>I10sI', bytes)

print("t = {0}, n = {1}, a = {2}".format(t, str(n), a))
