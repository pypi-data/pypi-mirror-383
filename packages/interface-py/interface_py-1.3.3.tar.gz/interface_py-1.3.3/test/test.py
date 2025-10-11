import unittest
from unittest import TestCase

import pathlib
import sys
path = str(pathlib.Path(__file__).parent.parent.absolute())
sys.path.append(path)

from interface import interface, concrete


# @interface
# class HumanInterface:
#     def talk(self): pass
#     def walk(self): ...

# @interface
# class MilitaryHuman(HumanInterface):
#     def shoot(self): ...

# @concrete
# class Commander(MilitaryHuman):
#     def talk(self): print("talking")
#     def walk(self): print("walking")
#     def shoot(self): print("shooting")

# Raises error:
# Human()
# MilitaryHuman()

# c = Commander()
# c.talk()


class BlahTestCase(TestCase):
    
    def test_(self):
        pass


if __name__ == "__main__":
    unittest.main()
