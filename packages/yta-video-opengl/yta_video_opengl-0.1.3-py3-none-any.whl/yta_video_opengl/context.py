"""
Module to simplify the way we obtain a valid
OpenGL context every time we make the call,
being always the same.
"""
from typing import Union

import moderngl


_opengl_context: Union[moderngl.Context, None] = None

def get_context(
) -> moderngl.Context:
    """
    Obtain an OpenGL context, that will be the
    same in every call.
    """
    global _opengl_context

    if _opengl_context is None:
        _opengl_context = moderngl.create_context(standalone = True)

    return _opengl_context