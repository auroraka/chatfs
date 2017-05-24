LOG_OUTPUT = 1


def Log(*args, **kwargs):
    if 'level' in kwargs.keys():
        if kwargs['level'] < LOG_OUTPUT:
            return
    print(*args)
