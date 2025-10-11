from yta_video_opengl.uniforms.enum import UniformType
from yta_validation import PythonValidator
from typing import Union

import numpy as np
import moderngl


class _Uniforms:
    """
    *For internal use only*

    Class to wrap the functionality related to
    handling the opengl program uniforms.
    """

    @property
    def uniforms(
        self
    ) -> dict:
        """
        The uniforms in the program, as a dict, in
        the format `{key, value}`.
        """
        return {
            key: self.program[key].value
            for key in self.program
            if PythonValidator.is_instance_of(self.program[key], moderngl.Uniform)
        }

    def __init__(
        self,
        program: moderngl.Program
    ):
        self.program: moderngl.Program = program
        """
        The program instance this handler class
        belongs to.
        """

    def get(
        self,
        name: str
    ) -> Union[any, None]:
        """
        Get the value of the uniform with the
        given 'name'.
        """
        return self.uniforms.get(name, None)

    def set(
        self,
        name: str,
        # TODO: Include type of the values
        value: any,
        type: Union[UniformType, None] = None
    ) -> '_Uniforms':
        """
        Set the provided uniform according to the given
        'type'. The 'type' will be autodetect if None
        provided. Nothing will be set if there is not
        uniform with the 'name' given.
        """
        if name not in self.program:
            print(f'The uniform with the name "{name}" is not registered in the program shader.')
            # TODO: Raise exception instead (?)
            #raise Exception(f'The uniform with the name "{name}" is not registered in the program shader.')
            return self
        
        type = (
            UniformType.autodetect(value)
            if type is None else
            UniformType.to_enum(type)
        )
        
        # Parse and prepare value to be stored (this
        # could go wrong and modify the value, be
        # careful at this point)
        value = type.prepare_value(value)

        if type in [
            UniformType.BOOL,
            UniformType.INT,
            UniformType.FLOAT,
            UniformType.VECTOR2,
            UniformType.VECTOR3,
            UniformType.VECTOR4,
        ]:
            self.program[name].value = value
        elif type in [
            UniformType.MATRIX2,
            UniformType.MATRIX3,
            UniformType.MATRIX4
        ]:
            self.program[name].write(value.tobytes())

        return self

    def print(
        self
    ) -> '_Uniforms':
        """
        Print the defined uniforms in console.
        """
        for key, value in self.uniforms.items():
            print(f'"{key}": {str(value)}')


"""
Note for the developer about GLSL:

By now we are not accepting nor handling
all the existing types in GLSL but some
of them. Here below is an intersting list:

SCALARS:
bool, int, uint
float, double

VECTORS:
bvec2, bvec3, bvec4
ivec2, ivec3, ivec4
uvec2, uvec3, uvec4
vec2, vec3, vec4
dvec2, dvec3, dvec4

MATRIXES:
mat2, mat3, mat4
mat2x3, mat2x4
mat3x2, mat3x4
mat4x2, mat4x3
dmat2, dmat3, dmat4
dmat2x3, dmat2x4, dmat3x2, dmat3x4, dmat4x2, dmat4x3

SAMPLERS:
sampler1D, sampler2D, sampler3D
samplerCube, sampler2DRect
sampler1DShadow, sampler2DShadow, samplerCubeShadow
sampler1DArray, sampler2DArray
sampler1DArrayShadow, sampler2DArrayShadow
isampler2D, usampler2D, isampler3D, usampler3D
sampler2DMS, sampler2DMSArray
samplerBuffer, isamplerBuffer, usamplerBuffer
"""