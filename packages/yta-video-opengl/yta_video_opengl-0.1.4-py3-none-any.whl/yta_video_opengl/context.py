"""
Module to simplify the way we obtain a valid
OpenGL context every time we make the call,
being always the same.
"""
from typing import Union

import moderngl


_opengl_context: Union[moderngl.Context, None] = None

def get_opengl_context(
    is_standalone: bool = True,
    do_refresh: bool = False
) -> moderngl.Context:
    """
    Obtain an OpenGL context, that will be the same
    in every call.

    The `do_refresh` method will force the creation
    of a new context that will overwrite any previous
    one.
    """
    global _opengl_context

    if (
        _opengl_context is None or
        do_refresh
    ):
        _opengl_context = moderngl.create_context(standalone = is_standalone)

    return _opengl_context