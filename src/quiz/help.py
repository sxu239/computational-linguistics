dict = {'a':'f','d':'e'}
for pos in dict.get('c',list()):
    a = 10+pos*2
    print(a)
