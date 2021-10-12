class DocMeta(type):
    def __init__(self, clsname, bases, clsdict):
        for key, value in clsdict.items():
            if key.startswith("__"):
                continue
            if not hasattr(value, "__call__"):
                continue
            if not getattr(value, "__doc__"):
                raise TypeError(f"{key} должен иметь строку документации")

        type.__init__(self, clsname, bases, clsdict)

class Documented(metaclass=DocMeta):
    pass
