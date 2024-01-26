/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2023 Arduino SA
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <string.h>
#include "py/mphal.h"

#include <esp_system.h>
#include <esp_ota_ops.h>
#include <esp_partition.h>

#if 0
#include "double_tap.h"
#include "usb.h"

#include "tinyusb.h"
#include "tusb_cdc_acm.h"

#define LED_BLUE    GPIO_NUM_4
#define DELAY_US    60000

static bool _recovery_marker_found; // double tap detected
static bool _recovery_active;       // running from factory partition

static void rgb_pulse_delay() {

    mp_hal_pin_output(LED_BLUE);

    mp_hal_pin_write(LED_BLUE, 1);
}

void NANO_ESP32_enter_bootloader(void) {
    if (!_recovery_active) {
        // check for valid partition scheme
        const esp_partition_t *ota_part = esp_ota_get_next_update_partition(NULL);
        const esp_partition_t *fact_part = esp_partition_find_first(ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_APP_FACTORY, NULL);
        if (ota_part && fact_part) {
            // set tokens so the recovery FW will find them
            double_tap_mark();
            // invalidate other OTA image
            esp_partition_erase_range(ota_part, 0, 4096);
            // activate factory partition
            esp_ota_set_boot_partition(fact_part);
        }
    }

    esp_restart();
}

void NANO_ESP32_usb_callback_line_state_changed(int itf, void *event_in) {
    extern void mp_usbd_line_state_cb(uint8_t itf, bool dtr, bool rts);
    cdcacm_event_t *event = event_in;
    mp_usbd_line_state_cb(itf, event->line_state_changed_data.dtr, event->line_state_changed_data.rts);
}

void NANO_ESP32_board_startup(void) {
    boardctrl_startup();

    // mark current partition as valid
    const esp_partition_t *running = esp_ota_get_running_partition();
    esp_ota_img_states_t ota_state;
    if (esp_ota_get_state_partition(running, &ota_state) == ESP_OK) {
        if (ota_state == ESP_OTA_IMG_PENDING_VERIFY) {
            esp_ota_mark_app_valid_cancel_rollback();
        }
    }

    const esp_partition_t *part = esp_ota_get_running_partition();
    _recovery_active = (part->subtype == ESP_PARTITION_SUBTYPE_APP_FACTORY);

    double_tap_init();

    _recovery_marker_found = double_tap_check_match();
    if (_recovery_marker_found && !_recovery_active) {
        // double tap detected in user application, reboot to factory
        NANO_ESP32_enter_bootloader();
    }

    // delay with mark set then proceed
    // - for normal startup, to detect first double tap
    // - in recovery mode, to ignore several short presses
    double_tap_mark();
    rgb_pulse_delay();
    double_tap_invalidate();
}
#endif //
