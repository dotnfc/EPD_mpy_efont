#
# The Makefile fragment for this module, refer: 
# 
# https://docs.micropython.org/en/latest/develop/cmodules.html#structure-of-an-external-c-module
#

USER_MOD_DIR := $(USERMOD_DIR)

define find_ff2_source_files
    $(wildcard $(1)/*.c) $(foreach dir,$(wildcard $(1)/*),$(call find_ff2_source_files,$(dir)))
endef

SRC_USERMOD_FFT_SRC := $(call find_ff2_source_files, $(USER_MOD_DIR)/freetype)
#$(info FFT_SRC is $(SRC_USERMOD_FFT_SRC))

SRC_USERMOD_C += $(addprefix $(USER_MOD_DIR)/, modefont.c)
SRC_USERMOD_LIB_C += $(addprefix $(USER_MOD_DIR)/, ff2_mpy_system.c)
SRC_USERMOD_LIB_C += $(addprefix $(USER_MOD_DIR)/, image_mpy.c)
SRC_USERMOD_LIB_C += $(addprefix $(USER_MOD_DIR)/tjpgd/, tjpgd.c)
SRC_USERMOD_LIB_C += $(addprefix $(USER_MOD_DIR)/pngle/, miniz.c)
SRC_USERMOD_LIB_C += $(addprefix $(USER_MOD_DIR)/pngle/, pngle.c)
SRC_USERMOD_LIB_C += $(SRC_USERMOD_FFT_SRC)

SRC_USERMOD_LIB_CXX += $(addprefix $(USER_MOD_DIR)/, ff2_mpy.cpp)

# Add our module directory to the include path.
CFLAGS_USERMOD += -I$(USER_MOD_DIR) -I$(USER_MOD_DIR)/freetype -DMODULE_EFONT_ENABLED=1
CFLAGS_USERMOD += -I$(USER_MOD_DIR)/tjpgd -I$(USER_MOD_DIR)/pngle
CXXFLAGS_USERMOD += -I$(USER_MOD_DIR) -I$(USER_MOD_DIR)/freetype -std=c++11

# We use C++ features so have to link against the standard library.
LDFLAGS_USERMOD += -lstdc++

# drop 'unused-variable' as error, you should do 
# refer to: https://forum.micropython.org/viewtopic.php?t=2947
# make CWARN="-Wall -Werror -Wno-error=unused-variable -Wno-error=unused-but-set-variable -Wno-error=unused-const-variable"
# 
