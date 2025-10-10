"The key constants and inputmaps"

# silly keys
ESCAPE = 27
ENTER = 13
SPACE = 32
BACKSPACE = 8
TAB = 9
DELETE = 127
SHIFT = 304
CTRL = 306
ALT = 308
OPTION = ALT
COMMAND = 310
CAPSLOCK = 301

# arrow
LEFT = 276
RIGHT = 275
UP = 273
DOWN = 274

# alphabet keys
A = 97
B = 98
C = 99
D = 100
E = 101
F= 102
G= 103
H= 104
I= 105
J= 106
K= 107
L= 108
M= 109
N= 110
O= 111
P= 112
Q= 113
R= 114
S= 115
T= 116
U= 117
V= 118
W= 119
X= 120
Y= 121
Z= 122

#input maps
class InputMap:
    def __init__(self, inputs:list[int]=[A, D]) -> None:
        self.inputs = inputs
    def is_down(self,keys):
        for i in self.inputs:
            if keys[i]:
                return True
        return False

def get_axis(keys, negative:InputMap, positive:InputMap):
    return (int(positive.is_down(keys)) - int(negative.is_down(keys)))

def get_vector(keys, left:InputMap, right:InputMap, up:InputMap, down:InputMap):
    return [get_axis(keys, left, right), get_axis(keys, up, down)]