import os
from ctypes import *
import ctypes
so=ctypes.CDLL("./libdecrypter.so")
print so.TestWinningPrice("")
