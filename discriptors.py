class ServerVerifier:
    def __init__(self, name, value = 7777):
        self.name = "_" + name
        if value >= 5000 and int(value) == float(value):
            self._value = value
        else:
            raise ValueError("Порт дожен быть целым неотрицательным числом")

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not (value>= 0 and int(value) == float(value)):
            raise ValueError("Порт дожен быть целым неотрицательным числом")
        setattr(instance, self.name, value)

# class NonNegative:
#     def __get__(self, instance, owner):
#         return instance.__dict__[self.name]
#     def __set__(self, instance, value):
#         if value < 0:
#             raise ValueError('Cannot be negative.')
#         instance.__dict__[self.name] = value
#     def __set_name__(self, owner, name):
#         self.name = name
#
# class MyClass:
#     port = ServerVerifier('server')
#
#     def __init__(self, port):
#         self.port = port
#
# if __name__ == '__main__':
#     soc = MyClass(-7777)
#     print(soc.port)
