import dis

def f():
    x = 1 + 2
    return x

dis.dis(f)