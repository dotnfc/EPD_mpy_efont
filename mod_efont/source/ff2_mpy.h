/****************************************************************************
 *
 * ff2_mpy.h
 *
 * Micropython specific FreeType middle layer, based on the OpenFontRender library
 *
 * Copyright (C) 2023 by .NFC
 *
 */
#ifndef FF2_MPY_H
#define FF2_MPY_H 

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

#define EFONT_ALIGN_LEFT            0
#define EFONT_ALIGN_CENTER          1
#define EFONT_ALIGN_RIGHT           2
#define EFONT_ALIGN_TOPLEFT         0
#define EFONT_ALIGN_TOPCENTER       1
#define EFONT_ALIGN_TOPRIGHT        2

#define EFONT_ALIGN_MIDDLELEFT      3
#define EFONT_ALIGN_MIDDLECENTER    4
#define EFONT_ALIGN_MIDDLERIGHT     5
#define EFONT_ALIGN_BOTTOMLEFT      6
#define EFONT_ALIGN_BOTTOMCENTER    7 
#define EFONT_ALIGN_BOTTOMRIGHT     8


#include <stdint.h>
#include <stddef.h>

#include "py/runtime.h"
#include "py/obj.h"
#include "py/reader.h"

#define EF_DMSG(fmt, ...)          // mp_printf(&mp_plat_print, fmt "\n", ##__VA_ARGS__)
#define DMSG                       EF_DMSG
#define MP_RAISE_ERROR(FMT, ...)   mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT(FMT), ##__VA_ARGS__)

//
// memory porting
// 
#define ft_smalloc  malloc // m_malloc
#define ft_scalloc  calloc // m_malloc	
#define ft_srealloc realloc  // m_realloc
#define ft_sfree    free // m_free

//
// filesystem porting
// 
#define FT_FILE fileclass_t
#define ft_fclose ff2_fclose
#define ft_fopen ff2_fopen
#define ft_fread ff2_fread
#define ft_fseek ff2_fseek
#define ft_ftell ff2_ftell

typedef struct {
    mp_obj_t     file;
} fileclass_t;

fileclass_t *ff2_from_file_obj(mp_obj_t file_obj);
fileclass_t *ff2_fopen(const char *Filename, const char *mode);
void ff2_fclose(fileclass_t *stream);
size_t ff2_fread(void *ptr, size_t size, size_t nmemb, fileclass_t *stream);
int ff2_fseek(fileclass_t *stream, long int offset, int whence);
long int ff2_ftell(fileclass_t *stream);

// helper 
typedef void * ff2_handler;
void*    ff2_mpy_loadFont(const char *file, void *old_ctx);
void     ff2_mpy_unloadFont(void *ctx);
int16_t  ff2_mpy_getLineHeight(void *ctx);
uint16_t ff2_mpy_getTextWidth(void *ctx, const char *text);

void     ff2_mpy_setTextColor(void* ctx, uint16_t fg, uint16_t bg);
void     ff2_mpy_setTextSize(void* ctx, uint16_t size);
void     ff2_mpy_setTextBBox(void* ctx, int16_t x, int16_t y, uint16_t w, uint16_t h);

void     ff2_mpy_setRender(void* ctx, mp_obj_t fb, mp_obj_t pixel);
void     ff2_mpy_setSize(void* ctx, uint16_t size);
void     ff2_mpy_setBold(void* ctx, bool bold);
void     ff2_mpy_setMono(void* ctx, bool mono);
void     ff2_mpy_setItalic(void* ctx, bool italic);

uint16_t ff2_mpy_drawString(void* ctx, const char *str, int16_t x, int16_t y, bool is_measure_width);
uint16_t ff2_mpy_drawWChar(void* ctx, const wchar_t wchar, int16_t x, int16_t y);
uint16_t ff2_mpy_drawWString(void* ctx, const wchar_t *wstr, int16_t x, int16_t y, bool is_measure_width);

#ifdef __cplusplus
}
#endif // __cplusplus

#endif // FF2_MPY_H
