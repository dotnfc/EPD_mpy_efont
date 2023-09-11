/****************************************************************************
 *
 * ff2_mpy.cpp
 *
 * Micropython specific FreeType middle layer, based on the OpenFontRender library
 *
 * Copyright (C) 2023 by .NFC
 *
 */
#include "ff2_mpy.h"
#include <ft2build.h>
#include FT_CONFIG_CONFIG_H
#include FT_CACHE_H
#include FT_FREETYPE_H
#include FT_SYNTHESIS_H
#include <freetype/internal/ftdebug.h>
#include <freetype/internal/ftstream.h>
#include <freetype/ftsystem.h>
#include <freetype/fterrors.h>
#include <freetype/fttypes.h>
#include "ff2_array.hpp"
#include <string>


#define INIT_MAGIC (uint16_t)0x55AA

typedef struct _ff2_rect_t
{
    int16_t x, y;
    int16_t w, h;
} ff2_rect_t, *ff2_rect_p;

typedef struct Cursor_t
{
    int32_t x; ///< x-coordinate
    int32_t y; ///< y-coordinate
} Cursor;

typedef struct _ff2_context_t
{
    const char *font_file;

    // framebuf->setpixel()
    mp_obj_t method_setpixel;

    // ff2 context
    uint16_t g_FtLibraryLoaded;
    FT_Library g_FtLibrary;
    FTC_Manager _ftc_manager;
    FTC_CMapCache _ftc_cmap_cache;
    FTC_ImageCache _ftc_image_cache;
    FTC_FaceID _face_id;

    // mpy fb.pixel() context
    mp_obj_t mpy_fb;
    mp_obj_t mpy_pixel;

    // api context
    int16_t font_height;
    int16_t font_size;
    uint16_t fg, bg;   // fore/back ground
    ff2_rect_t rc;     // bounding box for rendering
    bool style_mono;   // text mono
    bool style_bold;   // text bold
    bool style_italic; // text italic

    // internal status
    bool is_measure_width; // measure text width before drawing.

} ff2_context_t, *ff2_context_p;

#define CACHE_SIZE_NO_LIMIT 0
#define CACHE_SIZE_MINIMUM 1

static uint16_t ff2_mpy_decode_UTF8(const uint8_t *buf, uint16_t *index, uint16_t remaining);
static FT_Error ftc_face_requester(FTC_FaceID face_id,
                                   FT_Library library,
                                   FT_Pointer request_data,
                                   FT_Face *face);
static void ff2_mpy_adjustOffset(int8_t align,
                                 Cursor &current_line_position,
                                 FT_Vector bearing_left,
                                 FT_BBox bbox,
                                 FT_Vector &offset);
// static uint16_t alphaBlend(uint8_t alpha, uint16_t fgc, uint16_t bgc);
static void drawPixel(ff2_context_p pctx, int32_t x, int32_t y, uint16_t color);
static uint16_t draw2screenMono(ff2_context_p pctx, FT_GlyphSlot glyph, uint32_t x, uint32_t y, uint16_t fg, uint16_t bg);
static uint16_t ff2_mpy_internalDrawWString(
    ff2_context_p pctx,
    ArrayWstr &wchars,
    FT_Pos ascender,
    FT_Int cmap_index,
    FT_Vector offset);

void *ff2_mpy_loadFont(const char *file, void *old_ctx)
{
    FT_Face face;
    FT_Error error;

    ff2_mpy_unloadFont(old_ctx);

    ff2_context_p pctx = (ff2_context_p)m_malloc(sizeof(ff2_context_t));
    if (pctx == NULL)
    {
        m_malloc_fail(sizeof(ff2_context_t));
    }

    memset(pctx, 0, sizeof(ff2_context_t));
    pctx->font_height = -1;
    pctx->font_file = file;

    if (pctx->g_FtLibraryLoaded != INIT_MAGIC)
    {
        error = FT_Init_FreeType(&pctx->g_FtLibrary);
        if (error)
        {
            MP_RAISE_ERROR("FT_Init_FreeType error: 0x%02X\n", error);
            ff2_mpy_unloadFont(pctx);
        }
        pctx->g_FtLibraryLoaded = INIT_MAGIC;
    }

    error = FTC_Manager_New(pctx->g_FtLibrary, CACHE_SIZE_MINIMUM, CACHE_SIZE_MINIMUM, CACHE_SIZE_MINIMUM,
                            &ftc_face_requester, (FT_Pointer)pctx, &pctx->_ftc_manager);
    if (error)
    {
        MP_RAISE_ERROR("FTC_Manager_New error: 0x%02X\n", error);
        ff2_mpy_unloadFont(pctx);
        return NULL;
    }

    error = FTC_Manager_LookupFace(pctx->_ftc_manager, NULL, &face);
    if (error)
    {
        MP_RAISE_ERROR("FTC_Manager_LookupFace error: 0x%02X\n", error);
        ff2_mpy_unloadFont(pctx);
        return NULL;
    }

    error = FTC_CMapCache_New(pctx->_ftc_manager, &pctx->_ftc_cmap_cache);
    if (error)
    {
        MP_RAISE_ERROR("FTC_CMapCache_New error: 0x%02X\n", error);
        ff2_mpy_unloadFont(pctx);
        return NULL;
    }

    error = FTC_ImageCache_New(pctx->_ftc_manager, &pctx->_ftc_image_cache);
    if (error)
    {
        MP_RAISE_ERROR("FTC_ImageCache_New error: 0x%02X\n", error);
        ff2_mpy_unloadFont(pctx);
        return NULL;
    }

    ff2_mpy_getLineHeight(pctx);    // update line height
    return pctx;
}

void ff2_mpy_unloadFont(void *ctx)
{
    if (ctx == NULL)
    {
        return;
    }

    ff2_context_p pctx = (ff2_context_p)ctx;

    if (pctx->g_FtLibraryLoaded == INIT_MAGIC)
    {
        if (pctx->_ftc_manager)
        {
            FTC_Manager_RemoveFaceID(pctx->_ftc_manager, pctx->_face_id);
            FTC_Manager_Reset(pctx->_ftc_manager);
            FTC_Manager_Done(pctx->_ftc_manager);
        }

        if (pctx->g_FtLibrary)
        {
            FT_Done_FreeType(pctx->g_FtLibrary);
        }

        pctx->_ftc_manager = NULL;
        pctx->g_FtLibrary = NULL;
    }
    pctx->g_FtLibraryLoaded = 0;
    free(ctx);
}

int16_t ff2_mpy_getLineHeight(void *ctx)
{
    FT_Error error;
    FT_Face face;
    FTC_ScalerRec scaler;
    FT_Size asize = NULL;

    if (ctx == NULL)
    {
        return 0;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;

    if (pctx->font_height > 0)
    {
        return pctx->font_height;
    }

    scaler.face_id = pctx->_face_id;
    scaler.width = 0;
    scaler.height = pctx->font_height;
    scaler.pixel = true;
    scaler.x_res = 0;
    scaler.y_res = 0;

    error = FTC_Manager_LookupSize(pctx->_ftc_manager, &scaler, &asize);
    if (error)
    {
        return 0;
    }
    face = asize->face;

    int bbox_ymax = FT_MulFix(face->bbox.yMax, face->size->metrics.y_scale) >> 6;
    int bbox_ymin = FT_MulFix(face->bbox.yMin, face->size->metrics.y_scale) >> 6;

    pctx->font_height = (bbox_ymax - bbox_ymin);
    return pctx->font_height;
}

uint16_t ff2_mpy_getTextWidth(void *ctx, const char *text)
{
    return ff2_mpy_drawString(ctx, text, 0, 0, true);
}

void ff2_mpy_setTextColor(void *ctx, uint16_t fg, uint16_t bg)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->fg = fg;
    pctx->bg = bg;
}

void ff2_mpy_setTextSize(void *ctx, uint16_t size)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->font_size = size;
}

void ff2_mpy_setRender(void *ctx, mp_obj_t fb, mp_obj_t pixel)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->mpy_fb = fb;
    pctx->mpy_pixel = pixel;
}

void ff2_mpy_setSize(void *ctx, uint16_t size)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->font_size = size;
}

void ff2_mpy_setBold(void *ctx, bool bold)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->style_bold = bold;
}

void ff2_mpy_setMono(void *ctx, bool mono)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->style_mono = mono;
}

void ff2_mpy_setItalic(void *ctx, bool italic)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->style_italic = italic;
}

void ff2_mpy_setTextBBox(void *ctx, int16_t x, int16_t y, uint16_t w, uint16_t h)
{
    if (ctx == NULL)
    {
        return;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->rc.x = x;
    pctx->rc.y = y;
    pctx->rc.w = w;
    pctx->rc.h = h;
}

uint16_t drawWCharUtil(const uint32_t wchar, FT_BBox *abbox)
{
    return 0;
}

bool getCmapInfo(ff2_context_p pctx, FT_Int &cmap_index, FT_Pos &ascender)
{
    FT_Error error;
    FT_Size asize = NULL;
    FTC_ScalerRec scaler;

    scaler.face_id = pctx->_face_id;
    scaler.width = 0;
    scaler.height = pctx->font_size;
    scaler.pixel = true;
    scaler.x_res = 0;
    scaler.y_res = 0;

    error = FTC_Manager_LookupSize(pctx->_ftc_manager, &scaler, &asize);
    if (error)
    {
        DMSG("FTC_Manager_LookupSize error: 0x%02X\n", error);
        return false;
    }
    cmap_index = FT_Get_Charmap_Index(asize->face->charmap);
    ascender = asize->face->size->metrics.ascender;

    return true;
}

bool updateGlyphInfo(ff2_context_p pctx, bool &bFirstChar, const wchar_t wchar, FT_BBox &bbox, 
                    FTC_ImageTypeRec &image_type, FT_Int cmap_index, FT_Vector &bearing_left)
{
    FT_Glyph aglyph;
    FT_UInt glyph_index;
    FT_BBox glyph_bbox;
    FT_Error error;
    glyph_index = FTC_CMapCache_Lookup(pctx->_ftc_cmap_cache,
                                       pctx->_face_id,
                                       cmap_index,
                                       wchar);

    error = FTC_ImageCache_Lookup(pctx->_ftc_image_cache, &image_type, glyph_index, &aglyph, NULL);
    if (error)
    {
        DMSG("FTC_ImageCache_Lookup error: 0x%02X\n", error);
        return false;
    }

    FT_Glyph_Get_CBox(aglyph, FT_GLYPH_BBOX_PIXELS, &glyph_bbox);
    if (bFirstChar == true)
    {
        // Get bearing X
        FT_Face aface;
        FTC_Manager_LookupFace(pctx->_ftc_manager, pctx->_face_id, &aface);
        bearing_left.x = (aface->glyph->metrics.horiBearingX >> 6);
        // nothing to do for bearing.y
        bFirstChar = false;
    }

    // Move coordinates on the grid
    glyph_bbox.xMin += pctx->rc.x;
    glyph_bbox.xMax += pctx->rc.x;
    glyph_bbox.yMin += pctx->rc.y;
    glyph_bbox.yMax += pctx->rc.y;

    // Merge bbox
    bbox.xMin = std::min(bbox.xMin, glyph_bbox.xMin);
    bbox.yMin = std::min(bbox.yMin, glyph_bbox.yMin);
    bbox.xMax = std::max(bbox.xMax, glyph_bbox.xMax);
    bbox.yMax = std::max(bbox.yMax, glyph_bbox.yMax);

    pctx->rc.x += (aglyph->advance.x >> 16);

    return true;
}

void normalizeBBox(ff2_context_p pctx, FT_BBox &bbox, FT_Vector &offset, int8_t align,
                   FT_Pos &ascender, Cursor &current_line_position, FT_Vector &bearing_left)
{
    int16_t y = pctx->rc.y;

    // Check that we really grew the string bbox
    if (bbox.xMin > bbox.xMax)
    {
        // Failed
        bbox.xMin = bbox.yMin = 0;
        bbox.xMax = bbox.yMax = 0;
    }
    else
    {
        // Transform coordinate space differences
        bbox.yMax = y - (bbox.yMax - y) + ((ascender) >> 6);
        bbox.yMin = y + (y - bbox.yMin) + ((ascender) >> 6);
        if (bbox.yMax < bbox.yMin)
        {
            std::swap(bbox.yMax, bbox.yMin);
        }
        // Correct slight misalignment of X-axis
        offset.x = bbox.xMin - current_line_position.x;
    }

    ff2_mpy_adjustOffset(align, current_line_position, bearing_left, bbox, offset);

    bbox.xMin -= offset.x;
    bbox.xMax -= offset.x;
    bbox.yMin -= offset.y;
    bbox.yMax -= offset.y;
}

uint16_t drawWStringUtil(void *ctx, const wchar_t *str, FT_BBox &abbox)
{
    uint16_t next_x = 0;
    if (ctx == NULL)
    {
        return 0;
    }
    ff2_context_p pctx = (ff2_context_p)ctx;
    FT_Pos ascender = 0;
    bool detect_control_char = false;
    FT_Int cmap_index;
    Cursor initial_position = {pctx->rc.x, pctx->rc.y};

    abbox.xMin = abbox.yMin = LONG_MAX;
    abbox.xMax = abbox.yMax = LONG_MIN;

    FTC_ImageTypeRec image_type = {
        .face_id = pctx->_face_id,
        .width = 0,
        .height = (FT_UInt)pctx->font_size,
        .flags = FT_LOAD_DEFAULT};

    if (!getCmapInfo(pctx, cmap_index, ascender))
    {
        return 0;
    }

    wchar_t wchar = 0;
    // for each chars
    while (*str)
    {
        FT_Vector offset = {0, 0};
        FT_Vector bearing_left = {0, 0};
        FT_BBox bbox;
        Cursor current_line_position = {pctx->rc.x, pctx->rc.y};

        bbox.xMin = bbox.yMin = LONG_MAX;
        bbox.xMax = bbox.yMax = LONG_MIN;

        detect_control_char = false;
        image_type.flags = pctx->style_mono ? FT_LOAD_TARGET_MONO : FT_LOAD_DEFAULT;
        bool isLineFirstChar = true;
        ArrayWstr  one_line_wchars;

        // get one line
        while (*str)
        {
            wchar = *str++;

            if ((wchar == '\r') || (wchar == '\n'))
            {
                detect_control_char = true;
                break; // line chars filled, do measure or draw.
            }
            else
            {
                if (!updateGlyphInfo(pctx, isLineFirstChar, wchar, bbox, image_type, cmap_index, bearing_left))
                {
                    return 0;
                }
                one_line_wchars.Append(wchar);
            }
        }

        // process one line
        normalizeBBox(pctx, bbox, offset, EFONT_ALIGN_LEFT, ascender, current_line_position, bearing_left);

        // Restore coordinates
        pctx->rc.x = current_line_position.x;
        pctx->rc.y = current_line_position.y;

        next_x += ff2_mpy_internalDrawWString(pctx, one_line_wchars, ascender, cmap_index, offset);

        if (detect_control_char)
        {
            if (wchar == L'\r')
            {
                pctx->rc.x = initial_position.x;
            }
            else if (wchar == L'\n')
            {
                pctx->rc.x = initial_position.x;
                pctx->rc.y += pctx->font_height;
            }
        }

        // Merge bbox
        abbox.xMin = std::min(bbox.xMin, abbox.xMin);
        abbox.yMin = std::min(bbox.yMin, abbox.yMin);
        abbox.xMax = std::max(bbox.xMax, abbox.xMax);
        abbox.yMax = std::max(bbox.yMax, abbox.yMax);
    } // End of rendering loop

    if (detect_control_char && (wchar == L'\n'))
    {
        // If string end with '\n' control char, expand bbox
        abbox.yMax += pctx->font_height;
    }

    return next_x;
}

uint16_t ff2_mpy_drawString(void *ctx, const char *str, int16_t x, int16_t y, bool is_measure_width)
{
    uint16_t unicode;
    ArrayWstr wstr;

    if (ctx == NULL)
    {
        return 0;
    }

    uint16_t len = (uint16_t)strlen(str);
    uint16_t n = 0;
    while (n < len)
    {
        unicode = ff2_mpy_decode_UTF8((const uint8_t *)str, &n, len - n);
        wstr.Append(unicode);
    }
    wstr.Append(L'\0');

    ff2_context_p pctx = (ff2_context_p)ctx;
    pctx->rc.x = x;
    pctx->rc.y = y;

    return ff2_mpy_drawWString(ctx, wstr, x, y, is_measure_width);
}

uint16_t ff2_mpy_drawWChar(void *ctx, const wchar_t wchar, int16_t x, int16_t y)
{
    wchar_t wstr[2] = {wchar, '\0'};

    return ff2_mpy_drawWString(ctx, wstr, x, y, false);
}

uint16_t ff2_mpy_drawWString(void *ctx, const wchar_t *wstr, int16_t x, int16_t y, bool is_measure_width)
{
    if (ctx == NULL)
    {
        return 0;
    }
    FT_BBox abbox;
    ff2_context_p pctx = (ff2_context_p)ctx;

    pctx->rc.x = x;
    pctx->rc.y = y;
    pctx->is_measure_width = is_measure_width;
    return drawWStringUtil(ctx, wstr, abbox);
}

FT_Error ftc_face_requester(FTC_FaceID face_id, FT_Library library, FT_Pointer request_data, FT_Face *aface)
{
    FT_Error error = FT_Err_Ok;

    const uint8_t FACE_INDEX = 0;
    ff2_context_p pctx = (ff2_context_p)request_data;
    if (pctx == NULL)
    {
        MP_RAISE_ERROR("invalid request data\n");
        return FT_THROW(Invalid_Argument);
    }

    error = FT_New_Face(library, pctx->font_file, FACE_INDEX, aface); // create face object
    if (error)
    {
        DMSG("Font load Failed: 0x%02X", error);
    }
    else
    {
        // the FTC_FaceID
        // `typically used to point to a user-defined structure containing a font file path, and face index.`
        pctx->_face_id = pctx; // (*aface)->face_index;
    }

    return error;
}

uint16_t ff2_mpy_decode_UTF8(const uint8_t *buf, uint16_t *index, uint16_t remaining)
{
    uint16_t c = buf[(*index)++];

    // 7 bit Unicode
    if ((c & 0x80) == 0x00)
    {
        return c;
    }

    // 11 bit Unicode
    if (((c & 0xE0) == 0xC0) && (remaining > 1))
    {
        return ((c & 0x1F) << 6) | (buf[(*index)++] & 0x3F);
    }

    // 16 bit Unicode
    if (((c & 0xF0) == 0xE0) && (remaining > 2))
    {
        c = ((c & 0x0F) << 12) | ((buf[(*index)++] & 0x3F) << 6);
        return c | ((buf[(*index)++] & 0x3F));
    }

    // 21 bit Unicode not supported so fall-back to extended ASCII
    // if ((c & 0xF8) == 0xF0) return c;

    return c; // fall-back to extended ASCII
}

void ff2_mpy_adjustOffset(int8_t align,
                          Cursor &current_line_position,
                          FT_Vector bearing_left,
                          FT_BBox bbox,
                          FT_Vector &offset)
{
    // Calculate alignment offset
    switch (align)
    {
    case EFONT_ALIGN_TOPLEFT:
        // Nothing to do
        offset.x -= bearing_left.x;
        break;
    case EFONT_ALIGN_MIDDLELEFT:
        offset.x -= bearing_left.x;
        offset.y += ((bbox.yMax - bbox.yMin) / 2);
        break;
    case EFONT_ALIGN_BOTTOMLEFT:
        offset.x -= bearing_left.x;
        offset.y += (bbox.yMax - bbox.yMin);
        break;

    case EFONT_ALIGN_CENTER:
        offset.x += ((bbox.xMax - bbox.xMin) / 2);
        offset.x -= bearing_left.x;
        current_line_position.x -= (bearing_left.x / 2);
        break;
    case EFONT_ALIGN_MIDDLECENTER:
        offset.x += ((bbox.xMax - bbox.xMin) / 2);
        offset.x -= bearing_left.x;
        current_line_position.x -= (bearing_left.x / 2);

        offset.y += ((bbox.yMax - bbox.yMin) / 2);
        break;
    case EFONT_ALIGN_BOTTOMCENTER:
        offset.x += ((bbox.xMax - bbox.xMin) / 2);
        offset.x -= bearing_left.x;
        current_line_position.x -= (bearing_left.x / 2);

        offset.y += (bbox.yMax - bbox.yMin);
        break;
    case EFONT_ALIGN_TOPRIGHT:
        offset.x += (bbox.xMax - bbox.xMin);
        offset.x -= bearing_left.x;
        current_line_position.x -= bearing_left.x;
        break;
    case EFONT_ALIGN_MIDDLERIGHT:
        offset.x += (bbox.xMax - bbox.xMin);
        offset.x -= bearing_left.x;
        current_line_position.x -= bearing_left.x;

        offset.y += ((bbox.yMax - bbox.yMin) / 2);
        break;
    case EFONT_ALIGN_BOTTOMRIGHT:
        offset.x += (bbox.xMax - bbox.xMin);
        offset.x -= bearing_left.x;
        current_line_position.x -= bearing_left.x;
        offset.y += (bbox.yMax - bbox.yMin);
        break;
    default:
        break;
    }
}

#define RENDER_MODE_MONO (FT_LOAD_RENDER | FT_LOAD_TARGET_MONO | FT_LOAD_NO_AUTOHINT | FT_OUTLINE_HIGH_PRECISION)
uint16_t ff2_mpy_internalDrawWString(
    ff2_context_p pctx,
    ArrayWstr &wchars,
    FT_Pos ascender,
    FT_Int cmap_index,
    FT_Vector offset)
{

    int32_t x = pctx->rc.x;
    int32_t y = pctx->rc.y;
    FT_Error error;
    FTC_ImageTypeRec image_type = {
        .face_id = pctx->_face_id,
        .width = 0,
        .height = (FT_UInt)pctx->font_size,
        .flags = (FT_Int32)(pctx->style_mono ? RENDER_MODE_MONO : FT_LOAD_RENDER)};

    uint16_t written_char_num = 0;

    for (int32_t i = 0; i < wchars.Size(); i ++)
    {
        FT_UInt glyph_index = FTC_CMapCache_Lookup(pctx->_ftc_cmap_cache,
                                                   pctx->_face_id,
                                                   cmap_index,
                                                   wchars[i]);
        FT_Glyph aglyph;
        error = FTC_ImageCache_Lookup(pctx->_ftc_image_cache, &image_type, glyph_index, &aglyph, NULL);

        if (error)
        {
            DMSG("FTC_ImageCache_Lookup error: 0x%02X\n", error);
            return 0;
        }
        FT_Vector pos = {(x - offset.x), (y - offset.y)};
        // Change baseline to left top
        pos.y += ((ascender) >> 6);
        int32_t adv_x = 0;

        if (pctx->style_mono)
        {
            FT_Face face;
            error = FTC_Manager_LookupFace(pctx->_ftc_manager, pctx->_face_id, &face);
            error = FT_Render_Glyph(face->glyph, FT_RENDER_MODE_MONO);
            if (error)
            {
                DMSG("FT_Load_Char error: 0x%02X\n", error);
                return 0;
            }
            FT_GlyphSlot glyph = face->glyph;
            if (pctx->style_bold)
                FT_GlyphSlot_Embolden(glyph);
            if (pctx->style_italic)
                FT_GlyphSlot_Oblique(glyph);

            if (!pctx->is_measure_width)
            {
                draw2screenMono(pctx, glyph, pos.x, pos.y, pctx->fg, pctx->bg);
            }
        }
        else
        {
            // if (pctx->is_measure_width) {
            //     FT_BitmapGlyph bit = (FT_BitmapGlyph)aglyph;
            //     draw2screen(bit, pos.x, pos.y, pctx->fg, pctx->bg);
            // }
        }
        adv_x = (aglyph->advance.x >> 16);

        written_char_num++;
        x += adv_x;
    }

    return (uint16_t)x;
}

uint16_t draw2screenMono(ff2_context_p pctx, FT_GlyphSlot glyph, uint32_t x, uint32_t y, uint16_t fg, uint16_t bg)
{
    FT_Bitmap *bitmap = &(glyph->bitmap);
    int32_t rows = bitmap->rows;
    int32_t width = bitmap->width;
    int32_t byte;
    uint8_t bit;

    for (int32_t _y = 0; _y < rows; ++_y)
    {
        for (int32_t _x = 0; _x < width; ++_x)
        {
            byte = _x >> 3; // _x / 8;
            bit = 0x80 >> (_x & 7);
            if (bitmap->buffer[_y * bitmap->pitch + byte] & bit)
            {
                drawPixel(pctx, _x + x + glyph->bitmap_left, _y + y - glyph->bitmap_top, fg);
            }
            else
            {
                //_drawPixel(_x + x + glyph->bitmap_left, _y + y - glyph->bitmap_top, bg);
            }
        }
    }
    return glyph->advance.x >> 6;
}

#define color565(r, g, b) ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
void draw2screen(bool optimized_drawing, FT_BitmapGlyph glyph, uint32_t x, uint32_t y, uint16_t fg, uint16_t bg)
{
#if 0
	if (optimized_drawing) {
		// Start of new render code for efficient rendering of pixel runs to a TFT
		// Background fill code commented out thus //-bg-// as it is only filling the glyph bounding box
		// Code for this will need to track the last background end x as glyphs may overlap
		// Ideally need to keep track of the cursor position and use the font height for the fill box
		// Could also then use a line buffer for the glyph image (entire glyph buffer could be large!)

		int16_t fxs = x; // Start point of foreground x-coordinate
		uint32_t fl = 0; // Foreground line length
		int16_t bxs = x; // Start point of background x-coordinate
		uint32_t bl = 0; // Background line length

		for (int32_t _y = 0; _y < glyph->bitmap.rows; ++_y) {
			for (int32_t _x = 0; _x < glyph->bitmap.width; ++_x) {
				uint8_t alpha = glyph->bitmap.buffer[_y * glyph->bitmap.pitch + _x];
				DMSG("%c", (alpha == 0x00 ? ' ' : 'o'));

				if (alpha) {
					if (bl) {
						_drawFastHLine(bxs, _y + y - glyph->top, bl, bg);
						bl = 0;
					}
					if (alpha != 0xFF) {
						// Draw anti-aliasing area
						if (fl) {
							if (fl == 1) {
								_drawPixel(fxs, _y + y - glyph->top, fg);
							} else {
								_drawFastHLine(fxs, _y + y - glyph->top, fl, fg);
							}
							fl = 0;
						}
						_drawPixel(_x + x + glyph->left, _y + y - glyph->top, alphaBlend(alpha, fg, bg));
					} else {
						if (fl == 0) {
							fxs = _x + x + glyph->left;
						}
						fl++;
					}
				} else {
					if (fl) {
						_drawFastHLine(fxs, _y + y - glyph->top, fl, fg);
						fl = 0;
					}
					if (_text.bg_fill_method == BgFillMethod::Minimum) {
						if (_saved_state.drawn_bg_point.x <= (x + _x)) {
							if (bl == 0) {
								bxs = _x + x + glyph->left;
							}
							bl++;
						}
					}
				}
				// End of new render code
			}

			if (fl) {
				_drawFastHLine(fxs, _y + y - glyph->top, fl, fg);
				fl = 0;
			} else if (bl) {
				_drawFastHLine(bxs, _y + y - glyph->top, bl, bg);
				bl = 0;
			}
			DMSG("\n");
		}
	} else {
		// The old draw method
		// Not optimized, but can work with minimal method definitions
		for (int32_t _y = 0; _y < glyph->bitmap.rows; ++_y) {
			for (int32_t _x = 0; _x < glyph->bitmap.width; ++_x) {
				uint8_t alpha = glyph->bitmap.buffer[_y * glyph->bitmap.pitch + _x];
				DMSG("%c", (alpha == 0x00 ? ' ' : 'o'));

				if (alpha) {
					_drawPixel(_x + x + glyph->left, _y + y - glyph->top, alphaBlend(alpha, fg, bg));
				} else if (_text.bg_fill_method == BgFillMethod::Minimum) {
					if (_saved_state.drawn_bg_point.x <= (x + _x)) {
						_drawPixel(_x + x + glyph->left, _y + y - glyph->top, bg);
					}
				}
			}
			DMSG("\n");
		}
	}
#endif // 0
}

#if 0
uint16_t color565(uint8_t r, uint8_t g, uint8_t b) {
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

uint16_t alphaBlend(uint8_t alpha, uint16_t fgc, uint16_t bgc) 
{
	// For speed use fixed point maths and rounding to permit a power of 2 division
	uint16_t fgR = ((fgc >> 10) & 0x3E) + 1;
	uint16_t fgG = ((fgc >> 4) & 0x7E) + 1;
	uint16_t fgB = ((fgc << 1) & 0x3E) + 1;

	uint16_t bgR = ((bgc >> 10) & 0x3E) + 1;
	uint16_t bgG = ((bgc >> 4) & 0x7E) + 1;
	uint16_t bgB = ((bgc << 1) & 0x3E) + 1;

	// Shift right 1 to drop rounding bit and shift right 8 to divide by 256
	uint16_t r = (((fgR * alpha) + (bgR * (255 - alpha))) >> 9);
	uint16_t g = (((fgG * alpha) + (bgG * (255 - alpha))) >> 9);
	uint16_t b = (((fgB * alpha) + (bgB * (255 - alpha))) >> 9);

	// Combine RGB565 colours into 16 bits
	// return ((r&0x18) << 11) | ((g&0x30) << 5) | ((b&0x18) << 0); // 2 bit greyscale
	// return ((r&0x1E) << 11) | ((g&0x3C) << 5) | ((b&0x1E) << 0); // 4 bit greyscale
	return (r << 11) | (g << 5) | (b << 0);
}
#endif //

#define MAKE_MP_STR(STR) mp_obj_new_str(STR, strlen(STR))
#define MAKE_MP_INT(NUMBER) mp_obj_new_int(NUMBER)
// void modApi_setpixel(const mp_obj_framebuf_t *fb, unsigned int x, unsigned int y, uint32_t col);

void drawPixel(ff2_context_p pctx, int32_t x, int32_t y, uint16_t color)
{
    if (mp_obj_is_callable(pctx->mpy_pixel))
    {
        mp_obj_t args[3] = {MAKE_MP_INT(x), MAKE_MP_INT(y), MAKE_MP_INT(color)};
        mp_call_function_n_kw(pctx->mpy_pixel, 3, 0, args);
    }
    else
    {
        mp_raise_TypeError(MP_ERROR_TEXT("Method is not callable"));
    }
}

