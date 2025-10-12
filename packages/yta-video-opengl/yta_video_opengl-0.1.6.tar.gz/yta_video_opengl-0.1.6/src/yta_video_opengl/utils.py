from yta_validation import PythonValidator
from typing import Union

import numpy as np
import moderngl


def frame_to_texture(
    frame: Union['VideoFrame', 'np.ndarray'],
    context: moderngl.Context,
    numpy_format: str = 'rgb24'
):
    """
    Transform the given 'frame' to an opengl
    texture. The frame can be a VideoFrame
    instance (from pyav library) or a numpy
    array.

    (!) This method is useful to transform a
    frame into a texture quick and for a single
    use, but we have the GPUTextureHandler class
    to handle it in an specific contexto to 
    optimize the performance and avoid creating
    textures but rewriting on them.
    """
    # To numpy RGB inverted for opengl
    frame: np.ndarray = (
        np.flipud(frame.to_ndarray(format = numpy_format))
        if PythonValidator.is_instance_of(frame, 'VideoFrame') else
        np.flipud(frame)
    )

    # Sometimes we have 'float32' values but we need to
    # force 'uint8' to be able to work with
    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    return context.texture(
        size = (frame.shape[1], frame.shape[0]),
        components = frame.shape[2],
        data = frame.tobytes()
    )

# TODO: I should make different methods to
# obtain a VideoFrame or a numpy array frame
def texture_to_frame(
    texture: moderngl.Texture,
    do_include_alpha: bool = True
) -> np.ndarray:
    """
    Transform an opengl texture into a pyav
    VideoFrame instance.

    The `do_include_alpha` will include the
    alpha channel if True.
    """
    data = texture.read(alignment = 1)
    # Read 4 channels always (RGBA8)
    frame = np.frombuffer(data, dtype = np.uint8).reshape((texture.size[1], texture.size[0], 4))
    # TODO: Do this with a utils
    frame = (
        frame
        if do_include_alpha else
        # Discard alpha channel if not needed
        frame[:, :, :3]
    )
    # Opengl gives it with the 'y' inverted
    frame = np.flipud(frame)
    # TODO: This can be returned as a numpy frame

    # This is if we need an 'av' VideoFrame (to
    # export through the demuxer, for example)
    # TODO: I avoid this by now because we don't
    # want to import the pyav library, so this
    # below has to be done with the numpy array
    # received...
    # frame = av.VideoFrame.from_ndarray(frame, format = 'rgba')
    # # TODO: Make this customizable
    # frame = frame.reformat(format = 'yuv420p')

    return frame

def get_fullscreen_quad_vao(
    context: moderngl.Context,
    program: moderngl.Program
) -> moderngl.VertexArray:
    """
    Get the vertex array object of a quad, by
    using the vertices, the indexes, the vbo,
    the ibo and the vao content.
    """
    # Quad vertices in NDC (-1..1) with texture
    # coords (0..1)
    """
    The UV coordinates to build the quad we
    will use to represent the frame by 
    applying it as a texture.
    """
    vertices = np.array(
        object = [
            # pos.x, pos.y, tex.u, tex.v
            -1.0, -1.0, 0.0, 0.0,  # vertex 0 - bottom left
            1.0, -1.0, 1.0, 0.0,  # vertex 1 - bottom right
            -1.0,  1.0, 0.0, 1.0,  # vertex 2 - top left
            1.0,  1.0, 1.0, 1.0,  # vertex 3 - top right
        ],
        dtype = 'f4'
    )

    """
    The indexes of the vertices (see 'vertices'
    property) to build the 2 opengl triangles
    that will represent the quad we need for
    the frame.
    """
    indices = np.array(
        object = [
            0, 1, 2,
            2, 1, 3
        ],
        dtype = 'i4'
    )

    vbo = context.buffer(vertices.tobytes())
    ibo = context.buffer(indices.tobytes())

    vao_content = [
        # 2 floats position, 2 floats texcoords
        (vbo, '2f 2f', 'in_vert', 'in_texcoord'),
    ]

    return context.vertex_array(program, vao_content, ibo)