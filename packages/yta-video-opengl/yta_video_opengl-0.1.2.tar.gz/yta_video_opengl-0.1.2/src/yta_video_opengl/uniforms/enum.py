from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from yta_constants.enum import YTAEnum as Enum
from typing import Union

import numpy as np


class UniformType(Enum):
    """
    The type of the uniform we accept to set
    in our OpenGL program.

    By now we are accepting a few of the types
    that are actually available in GLSL, check
    the note at the bottom to see a more list
    containing more options that could be 
    implemented in a near future.
    """

    # Scalars
    BOOL = 'bool'
    INT = 'int'
    FLOAT = 'float'
    # Vectors
    VECTOR2 = 'vec2'
    VECTOR3 = 'vec3'
    VECTOR4 = 'vec4'
    # Matrixes
    MATRIX2 = 'mat2'
    MATRIX3 = 'mat3'
    MATRIX4 = 'mat4'

    def prepare_value(
        self,
        # TODO: Set the different types we accept
        value: any
    ) -> Union[bool, int, float, tuple, np.ndarray]:
        """
        Parse the given `value` and prepare it to be able
        to be stored as a valid uniform value according
        to this type.
        """
        if self == UniformType.BOOL:
            value = bool(value)
        elif self == UniformType.INT:
            value = int(value)
        elif self == UniformType.FLOAT:
            value = float(value)
        elif self == UniformType.VECTOR2:
            # Previously this is what was being done
            #self.program[name].write(np.array(value, dtype = 'f4').tobytes())
            value = tuple(map(float, value))[:2]
        elif self == UniformType.VECTOR3:
            value = tuple(map(float, value))[:3]
        elif self == UniformType.VECTOR4:
            value = tuple(map(float, value))[:4]
        elif self == UniformType.MATRIX2:
            value = np.array(value, dtype = 'f4').reshape((2, 2))
        elif self == UniformType.MATRIX3:
            value = np.array(value, dtype = 'f4').reshape((3, 3))
        elif self == UniformType.MATRIX4:
            value = np.array(value, dtype = 'f4').reshape((4, 4))

        return value
    
    @staticmethod
    def autodetect(
        # TODO: Include type of the values
        value: any
    ) -> Union['UniformType', None]:
        """
        Detect the GLSL type we are able to handle
        according to the type of the `value` provided.
        Detect the GLSL-like uniform type from a Python value.
        """
        type: Union['UniformType', None] = None

        if PythonValidator.is_boolean(value):
            type = UniformType.BOOL
        elif NumberValidator.is_int(value):
            type = UniformType.INT
        elif NumberValidator.is_float(value):
            type = UniformType.FLOAT
        else:
            if (
                PythonValidator.is_list(value) or
                PythonValidator.is_tuple(value)
            ):
                value = np.array(value, dtype = np.float32)

            if PythonValidator.is_numpy_array(value):
                if value.ndim == 1:
                    # Vector
                    l = len(value)

                    if l == 2:
                        type = UniformType.VECTOR2
                    elif l == 3:
                        type = UniformType.VECTOR3
                    elif l == 4:
                        type = UniformType.VECTOR4
                elif value.ndim == 2:
                    # Matrix
                    shape = value.shape

                    if shape == (2, 2):
                        type = UniformType.MATRIX2
                    elif shape == (3, 3):
                        type = UniformType.MATRIX3
                    elif shape == (4, 4):
                        type = UniformType.MATRIX4

        return type