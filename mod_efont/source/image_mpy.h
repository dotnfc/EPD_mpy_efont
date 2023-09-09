/****************************************************************************
 *
 * image_mpy.h
 *
 * Micropython specific Image middle layer
 *
 * Copyright (C) 2023 by .NFC
 *
 */
#ifndef _IMAGE_MPY_H
#define _IMAGE_MPY_H

#include <stdint.h>
#include <stddef.h>
#include <memory.h>
#include "py/runtime.h"
#include "py/obj.h"
#include "py/reader.h"

#define IMAGE_PNG   1
#define IMAGE_JPG   2

typedef void* image_handle_t;

image_handle_t image_mpy_load(const char *filename, uint16_t *w, uint16_t *h, int8_t *ima_type);
void           image_mpy_set_fbuf_info(image_handle_t hima, int8_t ima_type, uint16_t width, uint16_t height);
bool           image_mpy_draw(image_handle_t hima, int8_t ima_type, bool cropping, void *fbuf, int32_t l, int32_t t, int32_t r, int32_t b);
bool           image_mpy_unload(image_handle_t hima, int8_t ima_type);

#endif // _IMAGE_MPY_H
