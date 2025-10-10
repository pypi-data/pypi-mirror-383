class Cython:
    compiled = False

    def cfunc(self, func):
        return func

    def ccall(self, func):
        return func

    def inline(self, func):
        return func

    def declare(self, value_type, value):
        return value

    def __getattr__(self, type_name):
        return "object"
