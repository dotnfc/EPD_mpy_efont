/****************************************************************************
 *
 * image_mpy.h
 *
 * Micropython specific Image middle layer
 *
 * Copyright (C) 2023 by .NFC
 *
 */

#include "image_mpy.h"
#include "tjpgdcnf.h"
#include "tjpgd/tjpgd.h"
#include "pngle/pngle.h"
#include "ff2_mpy.h"
#include <ctype.h>

#define MAKE_MP_INT(NUMBER)         mp_obj_new_int(NUMBER)
#define IMAGE_BUF_SIZE (4 * 1024)
#define ASSERT_BUF_PTR(BUF, MSG) \
    if (BUF == NULL)             \
        MP_RAISE_ERROR(MSG);

typedef struct _IMA_IO
{
    ff2_file_t *fp; // File pointer for input function

    uint16_t dst_fbuf_width;  // Width of  the destination FrameBuffer [pix]
    uint16_t dst_fbuf_height; // Height of the destination FrameBuffer [pix]

    uint16_t left;   // canvas left column
    uint16_t top;    // canvas top row
    uint16_t right;  // canvas right column
    uint16_t bottom; // canvas bottom row

    uint8_t *work_buf; // Pointer to JPDec working buffer
    pngle_t *hpng;     // PNG Handle

    mp_fun_var_t fbuf_pixel_method; // destination FrameBuffer pixel() method to invoke
    mp_obj_t dst_fbuf;              // destination FrameBuffer instance
    mp_obj_t src_fbuf;              // source FrameBuffer instance, aka JPG/PNG decoded frame

    bool mono;       // true if target fbuf is monochrome
    uint16_t fg, bg; // when mono is true, map color to draw
} IMA_IO;

// Match definition to modframebuf.c
typedef struct _mp_obj_framebuf_t
{
    mp_obj_base_t base;
    mp_obj_t buf_obj; // need to store this to prevent GC from reclaiming buf
    void *buf;
    uint16_t width, height, stride;
    uint8_t format;
} mp_obj_framebuf_t;
// constants for formats
#define FRAMEBUF_MVLSB (0)
#define FRAMEBUF_RGB565 (1)
#define FRAMEBUF_GS2_HMSB (5)
#define FRAMEBUF_GS4_HMSB (2)
#define FRAMEBUF_GS8 (6)
#define FRAMEBUF_MHLSB (3)
#define FRAMEBUF_MHMSB (4)


static mp_obj_t image_mpy_framebuf_new(const mp_obj_type_t *type, void *data, uint16_t w, uint16_t h, uint8_t format);
static bool image_mpy_blit(IMA_IO *imaIo, int32_t x, int32_t y);
static bool image_mpy_create_source(JDEC *jdec, int32_t cx, int32_t cy);
static void image_mpy_update_source(JDEC *jdec, uint8_t *buf, int32_t w, int32_t h);

static bool isImageFile(const char *filename, const char *ext);

static void *image_mpy_init_dest_fbuf(image_handle_t hima);
static image_handle_t image_mpy_load_jpg(const char *filename, uint16_t *w, uint16_t *h, bool is_mono);
static image_handle_t image_mpy_load_png(const char *filename, uint16_t *w, uint16_t *h, bool is_mono);
static bool image_mpy_draw_jpg(image_handle_t hima, bool cropping, void *fbuf, int32_t l, int32_t t, int32_t r, int32_t b, 
                                uint16_t fg, uint16_t bg);
static bool image_mpy_draw_png(image_handle_t hima, bool cropping, void *fbuf, int32_t l, int32_t t, int32_t r, int32_t b, 
                                uint16_t fg, uint16_t bg);
static bool image_mpy_unload_jpg(image_handle_t hima);
static bool image_mpy_unload_png(image_handle_t hima);
static void image_mpy_set_fbuf_info_jpg(image_handle_t hima, uint16_t width, uint16_t height);
static void image_mpy_set_fbuf_info_png(image_handle_t hima, uint16_t width, uint16_t height);

///////////////////////////////////////////////////////////////////////////////
// JPG

//
// file input function
//

STATIC size_t file_in_func( // Returns number of bytes read (zero on error)
    JDEC *jd,               // Decompression object
    uint8_t *buff,          // Pointer to the read buffer (null to remove data)
    size_t nbyte)
{                                       // Number of bytes to read/remove
    IMA_IO *dev = (IMA_IO *)jd->device; // Device identifier for the session (5th argument of jd_prepare function)
    size_t nread;

    if (buff)
    { // Read data from input stream
        nread = ff2_fread(buff, nbyte, 1, dev->fp);
        return nread;
    }

    // Remove data from input stream if buff was NULL
    ff2_fseek(dev->fp, nbyte, SEEK_CUR);
    return nbyte;
}

//
// jpg output function
//

STATIC int jpg_out( // 1:Ok, 0:Aborted
    JDEC *jd,       // Decompression object
    void *bitmap,   // Bitmap data to be output
    JRECT *rect)
{ // Rectangular region of output image
    IMA_IO *imaIo = (IMA_IO *)jd->device;

    image_mpy_update_source(jd, bitmap, rect->right - rect->left + 1, rect->bottom - rect->top + 1);
    image_mpy_blit(imaIo, imaIo->left + rect->left, imaIo->top + rect->top);

    return 1; /* Continue to decompress */
}

STATIC int jpg_out_cropping( // 1:Ok, 0:Aborted
    JDEC *jd,                // Decompression object
    void *bitmap,            // Bitmap data to be output
    JRECT *rect)
{ // Rectangular region of output image
    IMA_IO *imaIo = (IMA_IO *)jd->device;

    if (imaIo->left <= rect->right &&
        imaIo->right >= rect->left &&
        imaIo->top <= rect->bottom &&
        imaIo->bottom >= rect->top)
    {
        image_mpy_update_source(jd, bitmap, rect->right - rect->left + 1, rect->bottom - rect->top + 1);
        image_mpy_blit(imaIo, imaIo->left + rect->left, imaIo->top + rect->top);
    }
    return 1; // Continue to decompress
}

image_handle_t image_mpy_load_jpg(const char *filename, uint16_t *w, uint16_t *h, bool is_mono)
{
    JRESULT res;
    IMA_IO *imaIo;

    JDEC *jdec = m_malloc(sizeof(JDEC));
    ASSERT_BUF_PTR(jdec, "failed to alloc jpg memory");

    imaIo = m_malloc(sizeof(IMA_IO));
    jdec->device = imaIo;
    ASSERT_BUF_PTR(imaIo, "failed to alloc jpg io");

    imaIo->work_buf = m_malloc(IMAGE_BUF_SIZE);
    ASSERT_BUF_PTR(imaIo->work_buf, "failed to alloc jpg work buffer");

    imaIo->fp = ff2_fopen(filename, "rb");

    imaIo->mono = is_mono;
    imaIo->fg = 1;
    imaIo->bg = 0;

    // Prepare to decompress
    res = jd_prepare(jdec, file_in_func, imaIo->work_buf, IMAGE_BUF_SIZE, imaIo);
    if (res == JDR_OK)
    {
        *w = jdec->width;
        *h = jdec->height;
        jdec->color_format = JDF_RGB565; // default to RGB565, will be changed later

        return jdec;
    }

    MP_RAISE_ERROR("unsupported image file");
}

bool image_mpy_draw_jpg(image_handle_t hima, bool cropping, void *fbuf, 
                        int32_t l, int32_t t, int32_t r, int32_t b, 
                        uint16_t fg, uint16_t bg)
{
    JRESULT res;
    JDEC *jdec = (JDEC *)hima;
    IMA_IO *imaIo = (IMA_IO *)jdec->device;

    imaIo->left = l;
    imaIo->top = t;
    imaIo->right = r;
    imaIo->bottom = b;
    imaIo->bg = bg;
    imaIo->fg = fg;

    // check for canvas is within the dest_fbuf
    if (imaIo->right > imaIo->dst_fbuf_width)
    {
        imaIo->right = imaIo->dst_fbuf_width - 1;
    }

    if (imaIo->bottom > imaIo->dst_fbuf_height)
    {
        imaIo->bottom = imaIo->dst_fbuf_height - 1;
    }

    imaIo->dst_fbuf = MP_OBJ_FROM_PTR(fbuf);
    image_mpy_create_source(jdec, jdec->msx * 8, jdec->msy * 8);

    if (cropping)
    {
        res = jd_decomp(jdec, jpg_out_cropping, 0);
    }
    else
    {
        res = jd_decomp(jdec, jpg_out, 0);
    }

    return (res == JDR_OK);
}

static void MPY_AUTO_FREE(void *PTR, size_t SIZE)
{
#if MICROPY_MALLOC_USES_ALLOCATED_SIZE
    m_free(PTR, SIZE);
#else
    m_free(PTR);
#endif
}

void image_mpy_set_fbuf_info_jpg(image_handle_t hima, uint16_t width, uint16_t height)
{
    JDEC *jdec = (JDEC *)hima;
    IMA_IO *imaIo = (IMA_IO *)jdec->device;

    imaIo->dst_fbuf_width = width;
    imaIo->dst_fbuf_height = height;
}

///////////////////////////////////////////////////////////////////////////////
// PNG
//
// PNG Routines using the pngle library from https://github.com/kikuchan/pngle
// licensed under the MIT License
//
#define MAP_RGB565(R, G, B)         (uint16_t) ((R & 0xF8) << 8) | ((G & 0xFC) << 3) | ((B & 0xF8) >> 3)
#define MAP_MONO(R, G, B)           (uint8_t)  ((R * 77 + G * 151 + B * 28) >> 8)
void image_mpy_draw_pngle(pngle_t *pngle, uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint8_t rgba[4])
{
    IMA_IO *imaIo = pngle_get_user_data(pngle);

    mp_obj_t args_setpixel[4] = {imaIo->dst_fbuf};

    if (( (x + imaIo->left) >= imaIo->right) || ( (y + imaIo->top) >= imaIo->bottom))
    { // Out of bounds, no-op.
        return ;
    }

    // dest.pixel(cx0, y0, bgcol/fgcol)
    args_setpixel[1] = MAKE_MP_INT(x + imaIo->left);
    args_setpixel[2] = MAKE_MP_INT(y + imaIo->top);

    mp_obj_t ocolor;
    if (imaIo->mono)
    {
        uint16_t color = MAP_MONO(rgba[0], rgba[1], rgba[2]);
        ocolor = MP_OBJ_NEW_SMALL_INT((color >= 192) ? imaIo->fg : imaIo->bg);
    }
    else
    {
        ocolor = MAKE_MP_INT (MAP_RGB565(rgba[0], rgba[1], rgba[2]));
    }
    
    args_setpixel[3] = ocolor;
    mp_call_function_n_kw(imaIo->fbuf_pixel_method, 4, 0, args_setpixel);
}

image_handle_t image_mpy_load_png(const char *filename, uint16_t *w, uint16_t *h, bool is_mono)
{
    IMA_IO *imaIo = m_malloc(sizeof(IMA_IO));
    ASSERT_BUF_PTR(imaIo, "failed to alloc png io");

    imaIo->work_buf = m_malloc(IMAGE_BUF_SIZE);
    ASSERT_BUF_PTR(imaIo->work_buf, "failed to alloc jpg work buffer");

    imaIo->hpng = pngle_new();
    ASSERT_BUF_PTR(imaIo->hpng, "failed to alloc jpg work buffer");

    imaIo->fp = ff2_fopen(filename, "rb");
    
    imaIo->mono = is_mono;
    imaIo->fg = 1;
    imaIo->bg = 0;

    char buf[64];
    int len = ff2_fread(buf, sizeof(buf), 1, imaIo->fp);
    if (len <= 0)
    {
        MP_RAISE_ERROR("failed to read image file");
    }

    int fed = pngle_feed(imaIo->hpng, buf, len);
    if (fed < 0)
    {
        MP_RAISE_ERROR("failed to read image header");
    }

    *w = pngle_get_width(imaIo->hpng);
    *h = pngle_get_height(imaIo->hpng);

    return imaIo;
}


bool image_mpy_draw_png(image_handle_t hima, bool cropping, void *fbuf, 
                        int32_t l, int32_t t, int32_t r, int32_t b, 
                        uint16_t fg, uint16_t bg)
{
    IMA_IO *imaIo = (IMA_IO *)hima;

    imaIo->left = l;
    imaIo->top = t;
    imaIo->right = r;
    imaIo->bottom = b;
    imaIo->bg = bg;
    imaIo->fg = fg;

    // check for canvas is within the dest_fbuf
    if (imaIo->right > imaIo->dst_fbuf_width)
    {
        imaIo->right = imaIo->dst_fbuf_width - 1;
    }

    if (imaIo->bottom > imaIo->dst_fbuf_height)
    {
        imaIo->bottom = imaIo->dst_fbuf_height - 1;
    }

    imaIo->dst_fbuf = MP_OBJ_FROM_PTR(fbuf);
    // mp_obj_framebuf_t *dest = MP_OBJ_TO_PTR(imaIo->dst_fbuf);
    image_mpy_init_dest_fbuf(imaIo);

    pngle_set_draw_callback(imaIo->hpng, image_mpy_draw_pngle);
    pngle_set_user_data(imaIo->hpng, imaIo);

    ff2_fseek( imaIo->fp, 0, SEEK_END );
    long int flen = ff2_ftell(imaIo->fp);
    ff2_fseek(imaIo->fp, 0, SEEK_SET); // rewind to the beginning
    pngle_reset(imaIo->hpng);

    long int read_len = 0;
    bool result = true;

    while (flen > 0)
    {
        if (flen > IMAGE_BUF_SIZE)
        {
            read_len = IMAGE_BUF_SIZE;
        }
        else
        {
            read_len = flen;
        }
        read_len = ff2_fread(imaIo->work_buf, read_len, 1, imaIo->fp);
        if (read_len <= 0)
        {
            break;
        }

        int fed = pngle_feed(imaIo->hpng, imaIo->work_buf, read_len);
        if (fed < 0)
        {
            result = false; // failed to handle image
            // printf("ERROR: %s", pngle_error(pngle));
            break;
        }

        flen -= read_len;
    }

    pngle_destroy(imaIo->hpng);
    return result;
}

bool image_mpy_unload_png(image_handle_t hima)
{
    IMA_IO *imaIo = (IMA_IO *)hima;
    if (imaIo != NULL)
    {
        if (imaIo->fp != NULL)
        {
            ff2_fclose(imaIo->fp);
            imaIo->fp = NULL;
        }

        if (imaIo->work_buf != NULL)
        {
            MPY_AUTO_FREE(imaIo->work_buf, IMAGE_BUF_SIZE);
        }

        // mp_obj_framebuf_t *source = MP_OBJ_TO_PTR(imaIo->src_fbuf);
        if (imaIo->src_fbuf != NULL)
        {
            MPY_AUTO_FREE(imaIo->src_fbuf, sizeof(mp_obj_framebuf_t));
        }

        MPY_AUTO_FREE(imaIo, sizeof(IMA_IO));
    }

    return true;
}

void image_mpy_set_fbuf_info_png(image_handle_t hima, uint16_t width, uint16_t height)
{
    IMA_IO *imaIo = (IMA_IO *)hima;

    imaIo->dst_fbuf_width = width;
    imaIo->dst_fbuf_height = height;
}

///////////////////////////////////////////////////////////////////////////////
// public

/**
 * @brief load image and get the image width, height, type.
 * @param filename, image filename
 * @param w, h, [out] image width, height
 * @param type, [out] image type
 * @param monochrome draw image as monochrome or RGB565
 * @return the image handle or NULL if failed.
 */
image_handle_t image_mpy_load(const char *filename, uint16_t *w, uint16_t *h, int8_t *ima_type, bool is_mono)
{
    bool isPng = isImageFile(filename, "png");
    bool isJpg = isImageFile(filename, "jpg");
    bool isJpeg = isImageFile(filename, "jpeg");

    if (isPng)
    {
        *ima_type = IMAGE_PNG;
        return image_mpy_load_png(filename, w, h, is_mono);
    }
    else if (isJpg || isJpeg)
    {
        *ima_type = IMAGE_JPG;
        return image_mpy_load_jpg(filename, w, h, is_mono);
    }
    else
    {
        return NULL;
    }
}

/**
 * @brief draw image
 * @param hima, image handle
 * @param type, image type
 * @param cropping, cropping the image when drawing
 * @param fbuf, frame buffer to draw
 * @param x, y, w, h, drawing zone in frame buffer
 * @param fg, bg, fore/background color
 * @return drawing status, true if successful
 */
bool image_mpy_draw(image_handle_t hima, int8_t ima_type, bool cropping, void *fbuf, 
                    int32_t l, int32_t t, int32_t r, int32_t b, uint16_t fg, uint16_t bg)
{
    if (ima_type == IMAGE_JPG)
    {
        return image_mpy_draw_jpg(hima, cropping, fbuf, l, t, r, b, fg, bg);
    }
    else if (ima_type == IMAGE_PNG)
    {
        return image_mpy_draw_png(hima, cropping, fbuf, l, t, r, b, fg, bg);
    }
    else
    {
        return false;
    }
}

/**
 * @brief free image resources
 * @param hima, image handle
 * @param type, image type
 * @return unload status, true if successful
 */
bool image_mpy_unload(image_handle_t hima, int8_t ima_type)
{
    if (ima_type == IMAGE_JPG)
    {
        return image_mpy_unload_jpg(hima);
    }
    else if (ima_type == IMAGE_PNG)
    {
        return image_mpy_unload_png(hima);
    }
    else
    {
        return false;
    }
}

void image_mpy_set_fbuf_info(image_handle_t hima, int8_t ima_type, uint16_t width, uint16_t height)
{
    if (ima_type == IMAGE_JPG)
    {
        return image_mpy_set_fbuf_info_jpg(hima, width, height);
    }
    else if (ima_type == IMAGE_PNG)
    {
        return image_mpy_set_fbuf_info_png(hima, width, height);
    }
}

///////////////////////////////////////////////////////////////////////////////
// utils
bool isImageFile(const char *filename, const char *ext)
{
    size_t len = strlen(filename);
    const char *dot = strrchr(filename, '.');
    if (dot == NULL || dot == filename + len - 1)
    {
        return false;
    }

    size_t ext_len = strlen(ext);
    if (len - (dot - filename + 1) != ext_len)
    {
        return false;
    }

    for (const char *p = dot + 1; *ext != '\0'; ++p, ++ext)
    {
        if (tolower(*p) != tolower(*ext))
        {
            return false;
        }
    }

    return true;
}

///////////////////////////////////////////////////////////////////////////////
// reference:
//   https://github.com/jimmo/micropython/blob/framebuf_utils/examples/natmod/framebuf_utils/framebuf_utils.c

bool image_mpy_unload_jpg(image_handle_t hima)
{
    JDEC *jdec = (JDEC *)hima;
    if (jdec == NULL)
    {
        return true;
    }

    IMA_IO *imaIo = (IMA_IO *)jdec->device;
    if (imaIo != NULL)
    {
        if (imaIo->fp != NULL)
        {
            ff2_fclose(imaIo->fp);
            imaIo->fp = NULL;
        }

        if (imaIo->work_buf != NULL)
        {
            MPY_AUTO_FREE(imaIo->work_buf, IMAGE_BUF_SIZE);
        }

        // mp_obj_framebuf_t *source = MP_OBJ_TO_PTR(imaIo->src_fbuf);
        if (imaIo->src_fbuf != NULL)
        {
            MPY_AUTO_FREE(imaIo->src_fbuf, sizeof(mp_obj_framebuf_t));
        }

        MPY_AUTO_FREE(imaIo, sizeof(IMA_IO));
    }
    MPY_AUTO_FREE(jdec, sizeof(JDEC));

    return true;
}

mp_obj_t image_mpy_framebuf_new(const mp_obj_type_t *type, void *data, uint16_t w, uint16_t h, uint8_t format)
{
    mp_obj_framebuf_t *o = mp_obj_malloc(mp_obj_framebuf_t, type);
    o->buf_obj = 0;
    o->buf = data;

    o->width = w;
    o->height = h;
    o->format = format;
    o->stride = w;

    switch (o->format)
    {
    case FRAMEBUF_MVLSB:
    case FRAMEBUF_RGB565:
        break;
    case FRAMEBUF_MHLSB:
    case FRAMEBUF_MHMSB:
        o->stride = (o->stride + 7) & ~7;
        break;
    case FRAMEBUF_GS2_HMSB:
        o->stride = (o->stride + 3) & ~3;
        break;
    case FRAMEBUF_GS4_HMSB:
        o->stride = (o->stride + 1) & ~1;
        break;
    case FRAMEBUF_GS8:
        break;
    default:
        mp_raise_ValueError(MP_ERROR_TEXT("invalid format"));
    }

    return MP_OBJ_FROM_PTR(o);
}

bool image_mpy_blit(IMA_IO *imaIo, int32_t x, int32_t y)
{
    mp_obj_framebuf_t *dest = MP_OBJ_TO_PTR(imaIo->dst_fbuf);
    mp_obj_framebuf_t *source = MP_OBJ_TO_PTR(imaIo->src_fbuf);

    // Pre-build args list for calling framebuf.pixel().
    mp_obj_t args_getpixel[3] = {imaIo->src_fbuf};
    mp_obj_t args_setpixel[4] = {imaIo->dst_fbuf};

    if (
        (x >= dest->width) ||
        (y >= dest->height) ||
        (-x >= source->width) ||
        (-y >= source->height))
    {
        // Out of bounds, no-op.
        return false;
    }

    // Clip.
    int x0 = MAX(0, x);
    int y0 = MAX(0, y);
    int x1 = MAX(0, -x);
    int y1 = MAX(0, -y);
    int x0end = MIN(dest->width, x + source->width);
    int y0end = MIN(dest->height, y + source->height);

    for (; y0 < y0end; ++y0)
    {
        int cx1 = x1;
        for (int cx0 = x0; cx0 < x0end; ++cx0)
        {
            // source.pixel(cx1, y1)
            args_getpixel[1] = MAKE_MP_INT(cx1);
            args_getpixel[2] = MAKE_MP_INT(y1);

            uint32_t col = mp_obj_get_int(mp_call_function_n_kw(imaIo->fbuf_pixel_method, 3, 0, args_getpixel));

            // dest.pixel(cx0, y0, bgcol/fgcol)
            args_setpixel[1] = MAKE_MP_INT(cx0);
            args_setpixel[2] = MAKE_MP_INT(y0);

            if (imaIo->mono)
            {
                if (col == 0)
                {
                    args_setpixel[3] = MAKE_MP_INT(imaIo->fg);
                }
                else
                {
                    args_setpixel[3] = MAKE_MP_INT(imaIo->bg);
                }
            }
            else
            {
                args_setpixel[3] = MAKE_MP_INT(col);
            }
            mp_call_function_n_kw(imaIo->fbuf_pixel_method, 4, 0, args_setpixel);

            ++cx1;
        }
        ++y1;
    }

    return true;
}

void *image_mpy_init_dest_fbuf(image_handle_t hima)
{
    IMA_IO *imaIo = (IMA_IO *)hima;

    // load FrameBuffer object type
    mp_obj_t objFBuf = mp_load_name(MP_QSTR_FrameBuffer);
    mp_obj_type_t *framebuf_type = MP_OBJ_TO_PTR(objFBuf);
    if (framebuf_type == NULL)
    {
        MP_RAISE_ERROR("failed to get FrameBuffer type");
    }

    // Get the "pixel" method from the FrameBuffer.
    mp_obj_t framebuf_pixel_obj = mp_load_attr(framebuf_type, MP_QSTR_pixel);

    mp_obj_fun_builtin_var_t *var_fun = MP_OBJ_TO_PTR(framebuf_pixel_obj);
    imaIo->fbuf_pixel_method = var_fun->fun.var;

    // cast dst_fbuf to framebuf object
    imaIo->dst_fbuf = mp_obj_cast_to_native_base(imaIo->dst_fbuf, MP_OBJ_FROM_PTR(framebuf_type));
    if (imaIo->dst_fbuf == MP_OBJ_NULL)
    {
        mp_raise_TypeError(NULL);
    }

    return framebuf_type;
}

bool image_mpy_create_source(JDEC *jdec, int32_t cx, int32_t cy)
{
    IMA_IO *imaIo = (IMA_IO *)jdec->device;

    mp_obj_type_t *framebuf_type = image_mpy_init_dest_fbuf(imaIo);

    mp_obj_framebuf_t *dest = MP_OBJ_TO_PTR(imaIo->dst_fbuf);
    uint8_t src_format = FRAMEBUF_GS8;
    if (dest->format == FRAMEBUF_MHLSB)
    {
        jdec->color_format = JDF_MONO;
        src_format = FRAMEBUF_GS8; // tjpgd ouput one byte per pixel for MONO format
    }
    else if (dest->format == FRAMEBUF_RGB565)
    {
        jdec->color_format = JDF_RGB565;
        src_format = FRAMEBUF_RGB565;
    }
    // else if (dest->format == FRAMEBUF_RGB565)
    //     jdec->color_format = JDF_RGB888;
    else
    {
        MP_RAISE_ERROR("unsupported image format");
    }

    // create source (ljpgd mcu) fbuf object
    imaIo->src_fbuf = image_mpy_framebuf_new(framebuf_type, NULL, cx, cy, src_format);

    return true;
}

void image_mpy_update_source(JDEC *jdec, uint8_t *buf, int32_t w, int32_t h)
{
    IMA_IO *imaIo = (IMA_IO *)jdec->device;
    mp_obj_framebuf_t *o = MP_OBJ_TO_PTR(imaIo->src_fbuf);

    if (jdec->color_format == JDF_MONO)
    {
        // The decoded data is 8-bit grayscale, which will be binarized here
        uint32_t siz = w * h;
        for (int i = 0; i < siz; i++)
        {
            buf[i] = (buf[i] > 192) ? 0xff : 0x00;
        }
    }

    o->buf = buf;

    if (o->width != w)
    {
        o->width = w;
        o->stride = o->width; // FRAMEBUF_RGB565, FRAMEBUF_GS8 only
    }

    o->height = h;
}
