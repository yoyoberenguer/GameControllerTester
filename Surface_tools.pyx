# encoding: utf-8
###cython: boundscheck=False, wraparound=False, nonecheck=False, optimize.use_switch=True
from pygame.image import frombuffer

try:
    cimport cython
    from cython.parallel cimport prange
    from cpython cimport PyObject_CallFunctionObjArgs, PyObject, \
        PyList_SetSlice, PyObject_HasAttr, PyObject_IsInstance, \
        PyObject_CallMethod, PyObject_CallObject
    from cpython.dict cimport PyDict_DelItem, PyDict_Clear, PyDict_GetItem, PyDict_SetItem, \
        PyDict_Values, PyDict_Keys, PyDict_Items
    from cpython.list cimport PyList_Append, PyList_GetItem, PyList_Size, PyList_SetItem
    from cpython.object cimport PyObject_SetAttr

except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

import numpy
from numpy import empty, uint8, asarray, \
    dstack, zeros, full_like, int16, putmask
from libc.math cimport sin, sqrt, cos
from libc.stdlib cimport srand, rand

try:
    import pygame
    from pygame import Rect
    from pygame.math import Vector2
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL
    from pygame import Surface, SRCALPHA, mask, RLEACCEL
    from pygame.transform import rotate, scale, smoothscale
    from pygame.surfarray import array3d, pixels3d, array_alpha, pixels_alpha

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

DEF THREAD_NUMBER = 8
DEF SCHEDULE = 'static'



def blend_texture(surface_, float percentage, color_):
    """


    :param surface_  : 32-bit pygame.Surface with alpha channel
    :param percentage: float; Percentage value [1..100]
    :param color_    : Color RGB values, pygame.Color, (r, g, ,b) or [r, g, b]
    :return:
    """

    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("\nCannot reference pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel = pixels_alpha(surface_)
    except Exception as e:
        raise ValueError("\nCannot reference pixel alphas into a 2d array..\n %s " % e)
    # Fill an array with similar shapes than source array.
    # Array uniformly filled with given RGB values (solid filled)
    fill_array = full_like(source_array.shape, color_[:3])

    diff = ((fill_array - source_array)/100.0) * percentage

    rgba_array = dstack((numpy.add(source_array, diff), alpha_channel)).astype(dtype=uint8)
    cdef int w = source_array.shape[:2][0]
    cdef int h = source_array.shape[:2][1]

    return pygame.image.frombuffer((rgba_array.transpose(1, 0, 2)).copy(order='C').astype(uint8),
                                   (w, h), 'RGBA').convert_alpha()



def add_transparency_all(rgb_array, alpha_, int value):
    alpha_ = alpha_.astype(int16)
    alpha_ -= value
    putmask(alpha_, alpha_ < 0, 0)
    return make_surface(make_array(rgb_array, alpha_.astype(numpy.uint8))).convert_alpha()



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef blend_texture_c(surface_, final_color_, int percentage):
    """
    BLEND A TEXTURE COLORS TOWARD A GIVEN SOLID COLOR
    
    COMPATIBLE WITH 32-BIT SURFACE WITH PER-PIXEL ALPHA CHANNEL.
    BLEND A TEXTURE WITH A PERCENTAGE OF GIVEN RGB COLOR (USING LINEAR LERP METHOD)
    BLEND AT 100%, ALL PIXELS FROM THE ORIGINAL TEXTURE WILL MERGE TO THE GIVEN PIXEL COLORS, 
    THE ENTIRE ARRAY WILL BE FILLED UNIFORMLY WITH A SINGLE PIXEL COLOR (FINAL_COLOR).
    BLEND AT 0%, TEXTURE IS UNCHANGED (RETURN)
    THE TEXTURE RETURNED IS NOT FORMATTED FOR A FAST BLIT (CONVERT_ALPHA(), OR CONVERT() ALGORITHM). 
    PLEASE FEEL FREE TO CONVERT IT AFTERWARD AT YOUR CONVENIENCE.
    
    **SOURCE ALPHA CHANNEL WILL BE TRANSFER TO THE DESTINATION SURFACE (NO ALTERATION
      OF THE ALPHA CHANNEL).
    
    :param surface_    : 32-bit pygame.Surface (must contains alpha channels)
    :param final_color_: Destination color. Can be a pygame color with values RGB, a tuple (RGB) or a 
    list [RGB]. RGB values must be type integer [0..255]
    :param percentage  : integer; 0 - 100% of the transformation (lerp)
    :return: return a pygame.surface with per-pixels transparency. Pixel transparency 
    of the source array will be unchanged (**Source alpha channel will be transfer to the 
    destination surface (no alteration of the alpha channel).
    """

    if isinstance(final_color_, pygame.Color):
        final_color_ = (final_color_.r, final_color_.g, final_color_.b)

    elif isinstance(final_color_, (tuple, list)):
        assert len(final_color_)==3, \
            '\nInvalid color format, use format (R, G, B) or [R, G, B].'
        pass
    else:
        raise TypeError('\nColor type argument error.')

    assert isinstance(surface_, Surface), \
        'Argument surface_ must be a Surface got %s ' % type(surface_)

    assert 0<= percentage <=100, "\nIncorrect value for argument percentage should be [0..100]"
    if percentage == 0:
        return surface_

    try:
        source_array = pixels3d(surface_)
    except Exception as e:
        raise ValueError("\nCannot reference pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel = pixels_alpha(surface_)
    except Exception as e:
        raise ValueError("\nCannot reference pixel alphas into a 2d array..\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:, :, :] source = source_array
        unsigned char [:, :, ::1] final_array = empty((h, w, 4), dtype=uint8)
        unsigned char [:, :] alpha = alpha_channel
        unsigned char [:] f_color = numpy.array(final_color_[:3], dtype=uint8)  # take only rgb values
        int c1, c2, c3
        float c4 = 1.0 / 100.0
        int i=0, j=0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                c1 = min(<int> (source[i, j, 0] + ((f_color[0] - source[i, j, 0]) * c4) * percentage), 255)
                c2 = min(<int> (source[i, j, 1] + ((f_color[1] - source[i, j, 1]) * c4) * percentage), 255)
                c3 = min(<int> (source[i, j, 2] + ((f_color[2] - source[i, j, 2]) * c4) * percentage), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                final_array[j, i, 0], final_array[j, i, 1], \
                final_array[j, i, 2], final_array[j, i, 3] = c1, c2, c3, alpha[i, j]

    return pygame.image.frombuffer(final_array, (w, h), 'RGBA')


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef blend_2_textures_c(source_, destination_, int percentage_):
    """
    BLEND A SOURCE TEXTURE TOWARD A DESTINATION TEXTURE 
    
    COMPATIBLE WITH 32-BIT SURFACE CONTAINING PER-PIXEL ALPHA CHANNEL.
    BLEND A TEXTURE COLORS TOWARD ANOTHER TEXTURE COLOR. 
    BLENDED AT 100%, PIXEL [I, J] FROM ORIGINAL TEXTURE WILL HAVE EXACT SAME 
    COLOR THAN DESTINATION PIXEL [I, J] 
    BLEND AT 0%, TEXTURE IS UNCHANGED.
    THE TEXTURE RETURNED IS NOT FORMATTED FOR A FAST BLIT (CONVERT_ALPHA(), OR CONVERT() ALGORITHM). 
    PLEASE FEEL FREE TO CONVERT IT AFTERWARD AT YOUR CONVENIENCE.
    
    **SOURCE ALPHA CHANNEL WILL BE TRANSFER TO THE DESTINATION SURFACE (NO ALTERATION
      OF THE ALPHA CHANNEL).

    :param source_     : pygame.Surface (Source)
    :param destination_: pygame.Surface (Destination)
    :param percentage_ : integer; Percentage value between [0, 100]
    :return: return    : Return a 32 bit pygame.Surface containing alpha channel and blended 
    with a percentage of the destination texture.
    """
    assert isinstance(source_, Surface), \
        'Argument source_ must be a pygame.Surface got %s ' % type(source_)

    assert isinstance(destination_, Surface), \
        'Argument destination_ must be a pygame.Surface got %s ' % type(destination_)

    assert 0<= percentage_ <=100, "\nIncorrect value for argument percentage should be [0..100]"

    if percentage_ == 0:
        return source_

    assert source_.get_size() == destination_.get_size(),\
        'Source and Destination surfaces must have same dimensions: ' \
        'Source (w:%s, h:%s), destination (w:%s, h:%s).' % (*source_.get_size(), *destination_.get_size())

    try:
        source_array      = pixels3d(source_)
    except Exception as e:
        raise ValueError("\nCannot reference source pixels into a 3d array.\n %s " % e)

    try:
        destination_array = pixels3d(destination_)
    except Exception as e:
        raise ValueError("\nCannot reference destination pixels into a 3d array.\n %s " % e)

    try:
        alpha_channel     = pixels_alpha(source_)
    except Exception as e:
        raise ValueError("\nCannot reference source pixel alphas into a 2d array..\n %s " % e)

    try:
        destination_alpha = pixels_alpha(destination_)
    except Exception as e:
        raise ValueError("\nCannot reference destination pixel alphas into a 2d array..\n %s " % e)

    cdef:
        int w = source_array.shape[0]
        int h = source_array.shape[1]
        unsigned char [:, :, :] source = source_array
        unsigned char [:, :, :] destination = destination_array
        unsigned char [:, :, :] final_array = empty((h, w, 4), dtype=uint8)
        unsigned char [:, :] alpha = alpha_channel
        unsigned char [:, :] dest_alpha = destination_alpha
        int c1, c2, c3
        int i=0, j=0
        float c4 = 1.0/100.0

    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):

                c1 = min(<int> (source[i, j, 0] +
                                ((destination[i, j, 0] - source[i, j, 0]) * c4) * percentage_), 255)
                c2 = min(<int> (source[i, j, 1] +
                                ((destination[i, j, 1] - source[i, j, 1]) * c4) * percentage_), 255)
                c3 = min(<int> (source[i, j, 2] +
                                ((destination[i, j, 2] - source[i, j, 2]) * c4) * percentage_), 255)
                if c1 < 0:
                    c1 = 0
                if c2 < 0:
                    c2 = 0
                if c3 < 0:
                    c3 = 0
                final_array[j, i, 0], final_array[j, i, 1], \
                final_array[j, i, 2], final_array[j, i, 3] = c1, c2, c3, alpha[i, j]

    return pygame.image.frombuffer(final_array, (w, h), 'RGBA')


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef make_array_c_code(unsigned char[:, :, :] rgb_array_c, unsigned char[:, :] alpha_c):
    """
    STACK ARRAY RGB VALUES WITH ALPHA CHANNEL.
    CREATE A 3D ARRAY CONTAINING RGBA VALUES THAT CAN BE USED TO CONVERT TO A 32 BIT PNG IMAGE
    FUNCTION IDENTICAL TO NUMPY.DSTACK 
    
    :param rgb_array_c: numpy.ndarray (w, h, 3) uint8 containing RGB values 
    :param alpha_c    : numpy.ndarray (w, h) uint8 containing alpha values 
    :return           : return a numpy.ndarray (w, h, 4) uint8, stack array of RGBA values
    The values are copied into a new array (out array is not transpose).
    """
    cdef int width, height
    try:
        width, height = (<object> rgb_array_c).shape[:2]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    cdef:
        unsigned char[:, :, ::1] new_array =  empty((width, height, 4), dtype=uint8)
        int i=0, j=0
    # EQUIVALENT TO A NUMPY DSTACK
    # USE MULTI-PROCESSING
    with nogil:
        for i in prange(width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(height):
                new_array[i, j, 0], new_array[i, j, 1], new_array[i, j, 2], \
                new_array[i, j, 3] =  rgb_array_c[i, j, 0], rgb_array_c[i, j, 1], \
                                   rgb_array_c[i, j, 2], alpha_c[i, j]
    return asarray(new_array)


#-------------------------------------- STACKING ------------------------------------------------
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef stack_object_c(unsigned char[:, :, :] rgb_array_,
                    unsigned char[:, :] alpha_, bint transpose=False):
    """
    STACK RGB PIXEL VALUES TOGETHER WITH ALPHA VALUES AND RETURN A PYTHON OBJECT,
    NUMPY.NDARRAY (FASTER THAN NUMPY.DSTACK)
    IF TRANSPOSE IS TRUE, TRANSPOSE ROWS AND COLUMNS OF OUTPUT ARRAY.
    
    :param transpose : boolean; Transpose rows and columns
    :param rgb_array_: numpy.ndarray (w, h, 3) uint8 containing RGB values 
    :param alpha_    : numpy.ndarray (w, h) uint8 containing alpha values 
    :return: return a contiguous numpy.ndarray (w, h, 4) uint8, stack array of RGBA pixel values
    The values are copied into a new array.
    """
    cdef int width, height
    try:
        width, height = (<object> rgb_array_).shape[:2]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    cdef:
        unsigned char[:, :, ::1] new_array =  numpy.empty((width, height, 4), dtype=uint8)
        unsigned char[:, :, ::1] new_array_t =  numpy.empty((height, width, 4), dtype=uint8)
        int i=0, j=0
    # Equivalent to a numpy.dstack
    with nogil:
        # Transpose rows and columns
        if transpose:
            for j in prange(0, height, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
                for i in range(0, width):
                    new_array_t[j, i, 0] = rgb_array_[i, j, 0]
                    new_array_t[j, i, 1] = rgb_array_[i, j, 1]
                    new_array_t[j, i, 2] = rgb_array_[i, j, 2]
                    new_array_t[j, i, 3] =  alpha_[i, j]

        else:
            for i in prange(0, width, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
                for j in range(0, height):
                    new_array[i, j, 0] = rgb_array_[i, j, 0]
                    new_array[i, j, 1] = rgb_array_[i, j, 1]
                    new_array[i, j, 2] = rgb_array_[i, j, 2]
                    new_array[i, j, 3] =  alpha_[i, j]

    return asarray(new_array) if transpose == False else asarray(new_array_t)



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef make_array(rgb_array_, alpha_):
    """
    CREATE A 3D ARRAY CONTAINING RGBA VALUES THAT CAN BE USED TO CONVERT TO A 32 BIT PNG IMAGE

    :param rgb_array_ : 3d numpy ndarray type (w, h, 3) containing rgb values (unsigned char)
    :param alpha_     : 2d numpy ndarray type (w, h, 2) containing alpha layer
    :return           : 3d numpy ndarray type (w, h, 4) containing rgba values, this array can be converted
                        to a 32 bit pygame surface.
    """
    return dstack((rgb_array_, alpha_)).astype(dtype=numpy.uint8)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef make_surface(rgba_array: numpy.ndarray):
    """
    CONVERT A 3D NUMPY ARRAY TYPE W x H x 4 INTO A 32bit 
    PYGAME SURFACE CONTAINING PER-PIXEL INFORMATION
    
    :param rgba_array : 3d numpy.ndarray with RGBA values  
    :return           : return a pygame.Surface 32 bit with per-pixel information
    """
    return frombuffer((rgba_array.transpose(1, 0, 2)).copy(order='C').astype(numpy.uint8),
                      (rgba_array.shape[:2][0], rgba_array.shape[:2][1]), 'RGBA')

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef make_transparent(image_, int alpha_):
    """
    MODIFY TRANSPARENCY TO A PYGAME SURFACE (ACTUAL ALPHA PIXEL VALUE - alpha_)
    
    :param image_: Surface; pygame.Surface to modify  
    :param alpha_: integer; integer value representing the new alpha value 
    :return      : Surface with new alpha value
    """
    try:
        rgb = pixels3d(image_)
    except (pygame.error, ValueError):
        raise ValueError('\nInvalid surface.')

    try:
        alpha = pixels_alpha(image_)
    except (pygame.error, ValueError):
        raise ValueError('\nSurface without per-pixel information.')

    cdef int w, h
    w, h = image_.get_size()

    cdef:
        unsigned char [:, :, ::1] new_array = numpy.empty((h, w, 4), dtype=numpy.uint8)
        unsigned char [:, :] alpha_array = alpha
        unsigned char [:, :, :] rgb_array = rgb
        int i=0, j=0, a

    with nogil:

        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                new_array[j, i, 0] = rgb_array[i, j, 0]
                new_array[j, i, 1] = rgb_array[i, j, 1]
                new_array[j, i, 2] = rgb_array[i, j, 2]
                a = alpha_array[i, j] - alpha_
                if a < 0:
                    a = 0
                new_array[j, i, 3] = a


    return frombuffer(new_array, (w, h), 'RGBA')


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef low_pixel_value_filter(unsigned char [:, :, :] rgb_array,
                                                     unsigned char [:, :] alpha_array,
                                                     int new_alpha,
                                                     int threshold):

    """
    ALTER LAYER ALPHA VALUE FOR PIXEL < THRESHOLD 

    Create a mask containing every pixels whom values are equal the following condition :
    r < threshold and g < threshold and b < threshold 
    All pixels flagged into the mask will have a new alpha value 

    :param rgb_array   : 3d numpy ndarray representing the pixels RGB values   
    :param alpha_array : 2d numpy ndarray representing the layer alpha 
    :param new_alpha   : integer; New alpha value 
    :param threshold   : integer; Threshold to compare to the sum RGB 
    :return            : 32bit Pygame Surface  (containing per-pixel information) 
    """

    assert PyObject_IsInstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert PyObject_IsInstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if 0 > new_alpha > 255:
        raise ValueError('\nInvalid value for argument new_alpha, '
                         'should be 0 <= alpha_value <=255 got %s ' % new_alpha)
    if 0 > threshold > 255:
        raise ValueError('\nInvalid value for argument threshold, '
                         'should be 0 <= threshold <=255 got %s ' % threshold)

    rgba = make_array_c_code(rgb_array, alpha_array)
    red, green, blue, alpha_ = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]
    mask1 = (red < threshold) & (green < threshold) & (blue < threshold)
    mask2 = alpha_ > 0
    mask = mask1 & mask2
    rgba[:, :, :][mask] = new_alpha
    return make_surface(rgba.astype(dtype=numpy.uint8))



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef low_pixel_value_filter_m(unsigned char [:, :, :] rgb_array,
                               unsigned char [:, :, :] alpha_array,
                               int new_alpha,
                               int threshold):
    """
    ALTER LAYER ALPHA VALUE FOR PIXEL < THRESHOLD 

    Create a mask containing every pixels whom values are equal the following condition :
    r < threshold and g < threshold and b < threshold 
    All pixels flagged into the mask will have a new alpha value 

    :param rgb_array   : 3d numpy ndarray representing the pixels RGB values   
    :param alpha_array : 3d numpy ndarray representing the layer alpha 
    :param new_alpha   : integer; New alpha value 
    :param threshold   : integer; Threshold to compare to the sum RGB 
    :return            : 32bit Pygame Surface (containing per-pixel information) 
    """

    assert PyObject_IsInstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert PyObject_IsInstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if 0 > new_alpha > 255:
        raise ValueError('\nInvalid value for argument new_alpha, '
                         'should be 0 <= alpha_value <=255 got %s ' % new_alpha)
    if 0 > threshold > 255:
        raise ValueError('\nInvalid value for argument threshold, '
                         'should be 0 <= threshold <=255 got %s ' % threshold)

    cdef:
        int w, h, n, w1, h1, n1

    w, h, n    = (<object>rgb_array).shape
    w1, h1, n1 = (<object>alpha_array).shape
    cdef unsigned char [:, :] output_alpha_array = numpy.empty((w, h), dtype=uint8)

    if w != w1 or h != h1:
        raise ValueError('\nrgb_array (%s, %s, %s) and alpha_array '
                         '(%s, %s, %s) are not equivalent!' % (w, h, n, w1, h1, n1))

    cdef:
        int i=0, j=0, s=0;
    with nogil:
        for i in prange(w, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            for j in range(h):
                s = rgb_array[i, j, 0] + rgb_array[i, j, 1] + rgb_array[i, j, 2]
                if s < threshold:
                    output_alpha_array[i, j] = new_alpha
                else:
                    output_alpha_array[i, j] = alpha_array[i, j, 0]
    return make_surface(make_array_c_code(rgb_array, output_alpha_array))



def black_blanket(rgb_array: numpy.ndarray, alpha_array: numpy.ndarray, new_alpha: int,
                  threshold: int) -> pygame.Surface:
    """
    THIS METHOD IS EQUIVALENT TO low_pixel_value_filter AND low_pixel_value_filter_m
    SLOWER VERSION (CYTHON NOT IMPLEMENTED)
    """
    assert isinstance(rgb_array, numpy.ndarray), \
        'Expecting numpy.array got %s ' % type(rgb_array)
    assert isinstance(alpha_array, numpy.ndarray), \
        ' Expecting numpy.array got %s ' % type(alpha_array)
    assert isinstance(new_alpha, int), 'Expecting int got %s ' % type(new_alpha)
    assert isinstance(threshold, int), 'Expecting int got %s ' % type(threshold)

    if not 0 <= new_alpha <= 255:
        raise ValueError('\n[-] invalid value for argument new_alpha, should be 0 <= alpha_value <=255 got %s '
                    % new_alpha)
    if not 0 <= threshold <= 255:
        raise ValueError('\n[-] invalid value for argument threshold, should be 0 <= threshold <=255 got %s '
                    % threshold)

    rgba = make_array(rgb_array, alpha_array)
    red, green, blue, alpha_ = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]
    mask1 = (red < threshold) & (green < threshold) & (blue < threshold)
    mask2 = alpha_ > 0
    mask = mask1 & mask2
    rgba[:, :, :][mask] = new_alpha

    return make_surface(rgba.astype(dtype=numpy.uint8))




@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef smooth_reshape(sprite_, factor_=1.0):
    """
    RESHAPE ANIMATION OR IMAGE USING PYTHON SMOOTHSCALE ALGORITHM
    
    :param sprite_: list, CREDIT_SPRITE; list containing the surface to rescale
    :param factor_: float, int or tuple; Represent the scale factor (new size)
    :return       : return  animation or a single CREDIT_SPRITE (rescale) 
    """

    cdef:
        float f_factor_
        tuple t_factor_

    if PyObject_IsInstance(factor_, (float, int)):
        # FLOAT OR INT
        try:
            f_factor_ = <float>factor_
            if f_factor_ == 1.0:
                return sprite_
        except ValueError:
            raise ValueError('\nArgument factor_ must be float or int got %s ' % type(factor_))
    # TUPLE
    else:
        try:
            t_factor_ = tuple(factor_)
            if (<float>t_factor_[0] == 0.0 and <float>t_factor_[1] == 0.0):
                return sprite_
        except ValueError:
            raise ValueError('\nArgument factor_ must be a list or tuple got %s ' % type(factor_))

    cdef:
        int i = 0
        int w, h
        int c1, c2
        sprite_copy = sprite_.copy()

    if PyObject_IsInstance(factor_, (float, int)):
        if PyObject_IsInstance(sprite_, list):
            c1 = <int>(sprite_[i].get_width()  * factor_)
            c2 = <int>(sprite_[i].get_height() * factor_)
        else:
            c1 = <int>(sprite_.get_width()  * factor_)
            c2 = <int>(sprite_.get_height() * factor_)

    # ANIMATION
    if PyObject_IsInstance(sprite_copy, list):

        for surface in sprite_copy:
            if PyObject_IsInstance(factor_, (float, int)):
                sprite_copy[i] = smoothscale(surface, (c1, c2))
            elif PyObject_IsInstance(factor_, (tuple, list)):
                sprite_copy[i] = smoothscale(surface, (factor_[0], factor_[1]))
            else:
                raise ValueError('\nArgument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))
            i += 1

    # SINGLE IMAGE
    else:
        if PyObject_IsInstance(factor_, (float, int)):
            sprite_copy = smoothscale(sprite_copy,(c1, c2))
        elif PyObject_IsInstance(factor_, (tuple, list)):
            sprite_copy = smoothscale(sprite_copy,factor_[0], factor_[1])
        else:
            raise ValueError('\nArgument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))

    return sprite_copy

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef reshape(sprite_, factor_=1.0):
    """
    RESHAPE ANIMATION OR IMAGE USING PYGAME SCALE ALGORITHM
    
    :param sprite_: list, CREDIT_SPRITE; list containing the surface to rescale
    :param factor_: float, int or tuple; Represent the scale factor (new size)
    :return       : return  animation or a single CREDIT_SPRITE (rescale) 
    """

    cdef:
        float f_factor_
        tuple t_factor_

    if PyObject_IsInstance(factor_, (float, int)):
        # FLOAT OR INT
        try:
            f_factor_ = <float>factor_
            if f_factor_ == 1.0:
                return sprite_
        except ValueError:
            raise ValueError('\nArgument factor_ must be float or int got %s ' % type(factor_))
    # TUPLE
    else:
        try:
            t_factor_ = tuple(factor_)
            if (<float>t_factor_[0] == 0.0 and <float>t_factor_[1] == 0.0):
                return sprite_
        except ValueError:
            raise ValueError('\nArgument factor_ must be a list or tuple got %s ' % type(factor_))

    cdef:
        int i = 0
        int w, h
        int c1, c2
        sprite_copy = sprite_.copy()

    if PyObject_IsInstance(factor_, (float, int)):
        if PyObject_IsInstance(sprite_, list):
            c1 = <int>(sprite_[i].get_width()  * factor_)
            c2 = <int>(sprite_[i].get_height() * factor_)
        else:
            c1 = <int>(sprite_.get_width()  * factor_)
            c2 = <int>(sprite_.get_height() * factor_)

    # ANIMATION
    if PyObject_IsInstance(sprite_copy, list):

        for surface in sprite_copy:
            if PyObject_IsInstance(factor_, (float, int)):
                sprite_copy[i] = scale(surface, (c1, c2))
            elif PyObject_IsInstance(factor_, (tuple, list)):
                sprite_copy[i] = scale(surface, (factor_[0], factor_[1]))
            else:
                raise ValueError('\nArgument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))
            i += 1

    # SINGLE IMAGE
    else:
        if PyObject_IsInstance(factor_, (float, int)):
            sprite_copy = scale(sprite_copy,(c1, c2))
        elif PyObject_IsInstance(factor_, (tuple, list)):
            sprite_copy = scale(sprite_copy,factor_[0], factor_[1])
        else:
            raise ValueError('\nArgument factor_ incorrect '
                             'type must be float, int or tuple got %s ' % type(factor_))

    return sprite_copy



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef wave_xy_c(texture, float rad, int size):
    """
    Create a wave effect on a texture
    
    e.g:
    for angle in range(0, 360):
        surface = wave_xy(CREDIT_SPRITE, 8 * r * math.pi/180, 10)
        
    :param texture: pygame.Surface, CREDIT_SPRITE compatible format 24, 32-bit without per-pixel information
    :param rad: float,  angle in radian
    :param size: block size to copy (pixels)
    :return: returns a pygame.Surface 24-bit without per-pixel information
    """
    assert isinstance(texture, Surface), \
        'Argument texture must be a Surface got %s ' % type(texture)
    assert isinstance(rad, float), \
        'Argument rad must be a python float got %s ' % type(rad)
    assert isinstance(size, int), \
        'Argument size must be a python int got %s ' % type(size)

    try:
        rgb_array = pixels3d(texture)

    except (pygame.error, ValueError):
        # unsupported colormasks for alpha reference array
        print('\nUnsupported colormasks for alpha reference array.')
        raise ValueError('\nIncompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = rgb_array.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % (w, h, dim)
    cdef:
        unsigned char [:, :, ::1] wave_array = zeros((h, w, 3), dtype=uint8)
        unsigned char [:, :, :] rgb = rgb_array
        int x, y, x_pos, y_pos, xx, yy
        int i=0, j=0
        float c1 = 1.0 / float(size * size)
        int w_1 = w - 1
        int h_1 = h - 1

    with nogil:
        for x in prange(0, w_1 - size, size, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            x_pos = x + size + <int>(sin(rad + <float>(x) * c1) * <float>(size))
            for y in prange(0, h_1 - size, size, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
                y_pos = y + size + <int>(sin(rad + <float>(y) * c1) * <float>(size))
                for i in range(0, size + 1):
                    for j in range(0, size + 1):
                        xx = x_pos + i
                        yy = y_pos + j

                        if xx > w_1:
                            xx = w_1
                        elif xx < 0:
                            xx = 0
                        if yy > h_1:
                            yy = h_1
                        elif yy < 0:
                            yy = 0
                        wave_array[yy, xx, 0] = rgb[x + i, y + j, 0]
                        wave_array[yy, xx, 1] = rgb[x + i, y + j, 1]
                        wave_array[yy, xx, 2] = rgb[x + i, y + j, 2]

    return pygame.image.frombuffer(wave_array, (w, h), 'RGB')



@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef wave_xy_32c(texture, float rad, int size):
    """
    Create a wave effect on a texture
    
    e.g:
    for angle in range(0, 360):
        surface = wave_xy(CREDIT_SPRITE, 8 * r * math.pi/180, 10)
        
    :param texture: pygame.Surface, CREDIT_SPRITE compatible format 24, 32-bit without per-pixel information
    :param rad: float,  angle in radian
    :param size: block size to copy (pixels)
    :return: returns a pygame.Surface 24-bit without per-pixel information
    """
    assert isinstance(texture, Surface), \
        'Argument texture must be a Surface got %s ' % type(texture)
    assert isinstance(rad, float), \
        'Argument rad must be a python float got %s ' % type(rad)
    assert isinstance(size, int), \
        'Argument size must be a python int got %s ' % type(size)

    try:
        rgb_array = pixels3d(texture)
        alpha     = pixels_alpha(texture)

    except (pygame.error, ValueError):
        # unsupported colormasks for alpha reference array
        print('\nUnsupported colormasks for alpha reference array.')
        raise ValueError('\nIncompatible pixel format.')

    cdef int w, h, dim
    try:
        w, h, dim = rgb_array.shape[:3]
    except (ValueError, pygame.error) as e:
        raise ValueError('\nArray shape not understood.')

    assert w != 0 or h !=0,\
            'Array with incorrect shape (w>0, h>0, 3) got (w:%s, h:%s, %s) ' % (w, h, dim)
    cdef:
        unsigned char [:, :, ::1] wave_array = zeros((h, w, 4), dtype=uint8)
        unsigned char [:, :, :] rgb = rgb_array
        unsigned char [:, :] alpha_ = alpha
        int x, y, x_pos, y_pos, xx, yy
        int i=0, j=0
        float c1 = 1.0 / float(size * size)
        int w_1 = w - 1
        int h_1 = h - 1

    with nogil:
        for x in prange(0, w_1 - size, size, schedule=SCHEDULE, num_threads=THREAD_NUMBER):
            x_pos = x + size + <int>(sin(rad + <float>(x) * c1) * <float>(size))
            for y in range(0, h_1 - size, 10):
                y_pos = y + size + <int>(sin(rad + <float>(y) * c1) * <float>(size))
                for i in range(0, size + 1):
                    for j in range(0, size + 1):
                        xx = x_pos + i
                        yy = y_pos + j

                        if xx > w_1:
                            xx = w_1
                        elif xx < 0:
                            xx = 0
                        if yy > h_1:
                            yy = h_1
                        elif yy < 0:
                            yy = 0
                        wave_array[yy, xx, 0] = rgb[x + i, y + j, 0]
                        wave_array[yy, xx, 1] = rgb[x + i, y + j, 1]
                        wave_array[yy, xx, 2] = rgb[x + i, y + j, 2]
                        wave_array[yy, xx, 3] = alpha_[x + i, y + j]
    return pygame.image.frombuffer(wave_array, (w, h), 'RGBA')


def horizontal_glitch(texture_: Surface, rad1_:float,
                      frequency_:float, amplitude_:float)->Surface:
    return horizontal_glitch_c(texture_, rad1_, frequency_, amplitude_)

# horizontal_glitch(surface, 1, 0.3, (50+r)% 20) with r in range [0, 360]
# horizontal_glitch(surface, 1, 0.3, (50-r)% 20) with r in range [0, 360]
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef horizontal_glitch_c(texture_: Surface, double rad1_, double frequency_, double amplitude_):
    """
    HORIZONTAL GLITCH EFFECT
    AFFECT THE ENTIRE TEXTURE BY ADDING PIXEL DEFORMATION
    HORIZONTAL_GLITCH_C(TEXTURE_, 1, 0.1, 10)

    :param texture_  :
    :param rad1_     : Angle deformation in degrees (cos(1) * amplitude will represent the deformation magnitude)
    :param frequency_: Angle in degrees to add every iteration for randomizing the effect
    :param amplitude_: Deformation amplitude, 10 is plenty
    :return:
    """

    try:
        source_array = pygame.surfarray.pixels3d(texture_)
    except (pygame.error, ValueError):
        print('\nIncompatible texture, must be 24-32bit format.')
        raise ValueError('\nMake sure the surface_ contains per-pixel alpha transparency values.')
    cdef int w, h
    w, h = texture_.get_size()

    cdef:
        int i=0, j=0
        double rad = 3.14/180.0
        double angle = 0.0
        double angle1 = 0.0
        unsigned char [:, :, :] rgb_array = source_array
        unsigned char [:, :, ::1] new_array = numpy.empty((w, h, 3), dtype=numpy.uint8)
        int ii=0

    with nogil:
        for j in range(h):
            for i in range(w):
                ii = (i + <int>(cos(angle) * amplitude_))
                if ii > w - 1:
                    ii = w
                if ii < 0:
                    ii = 0

                new_array[i, j, 0],\
                new_array[i, j, 1],\
                new_array[i, j, 2] = rgb_array[ii, j, 0],\
                    rgb_array[ii, j, 1], rgb_array[ii, j, 2]
            angle1 += frequency_ * rad
            angle += rad1_ * rad + rand() % angle1 - rand() % angle1

    return pygame.surfarray.make_surface(numpy.asarray(new_array))



def horizontal_glitch_32(texture_: Surface, rad1_:float,
                      frequency_:float, amplitude_:float)->Surface:
    return horizontal_glitch_32c(texture_, rad1_, frequency_, amplitude_)

# horizontal_glitch(surface, 1, 0.3, (50+r)% 20) with r in range [0, 360]
# horizontal_glitch(surface, 1, 0.3, (50-r)% 20) with r in range [0, 360]
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef horizontal_glitch_32c(texture_: Surface, double rad1_, double frequency_, double amplitude_):
    """
    HORIZONTAL GLITCH EFFECT
    AFFECT THE ENTIRE TEXTURE BY ADDING PIXEL DEFORMATION
    HORIZONTAL_GLITCH_C(TEXTURE_, 1, 0.1, 10)

    :param texture_  :
    :param rad1_     : Angle deformation in degrees (cos(1) * amplitude will represent the deformation magnitude)
    :param frequency_: Angle in degrees to add every iteration for randomizing the effect
    :param amplitude_: Deformation amplitude, 10 is plenty
    :return:
    """

    try:
        source_array = pixels3d(texture_)
        source_alpha = pixels_alpha(texture_)
    except (pygame.error, ValueError):
        print('\nIncompatible texture, must be 32bit format.')
        raise ValueError('\nMake sure the surface_ contains per-pixel alpha transparency values.')
    cdef int w, h
    w, h = texture_.get_size()

    cdef:
        int i=0, j=0
        double rad = 3.14/180.0
        double angle = 0.0
        double angle1 = 0.0
        unsigned char [:, :, :] rgb_array = source_array
        unsigned char [:, :] alpha_array  = source_alpha
        unsigned char [:, :, :] new_array = empty((h, w, 4), dtype=uint8)
        int ii=0

    with nogil:
        for j in range(h):
            for i in range(w):
                ii = (i + <int>(cos(angle) * amplitude_))
                if ii > w - 1:
                    ii = w
                if ii < 0:
                    ii = 0

                new_array[j, i, 0],\
                new_array[j, i, 1],\
                new_array[j, i, 2],\
                new_array[j, i, 3] = rgb_array[ii, j, 0],\
                    rgb_array[ii, j, 1], rgb_array[ii, j, 2], alpha_array[i, j]
            angle1 += frequency_ * rad
            angle += rad1_ * rad + rand() % angle1 - rand() % angle1

    # return pygame.surfarray.make_surface(numpy.asarray(new_array))
    return pygame.image.frombuffer(new_array, (w, h), 'RGBA')