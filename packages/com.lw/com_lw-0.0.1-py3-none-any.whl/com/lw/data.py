import enum

class DataBook:
    def __init__(self, name, author):
        self.name = name
        self.author = author

    def __str__(self):
        return self.name + ' ' + self.author


class BookType:
    def __init__(self, type_name, type_note):
        self.__type_name = type_name
        self.__type_note = type_note

    def __str__(self):
        return self.__type_name + ' ' + self.__type_note

# @enum.unique
# class ItemBook(enum.Enum):
#     JAVA = 0
#     PYTHON = 1
#     CPP = 2

@enum.unique
class ItemBook(enum.Enum):
    JAVA = BookType('java', 'java notes')
    PYTHON = BookType('python', 'python notes')
    CPP = BookType('cpp', 'c++ notes')

