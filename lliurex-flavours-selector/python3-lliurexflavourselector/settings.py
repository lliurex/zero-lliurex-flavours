import sys
import os

relative_path = os.path.dirname(sys.modules[__name__].__file__)
RSRC_DIR = os.path.join(relative_path,'rsrc')
SUPPORTED_FLAVOUR=os.path.join('/usr/share/lliurex-flavours-selector','supported-flavours')
BANNERS=os.path.join('/usr/share/lliurex-flavours-selector','banners')
TEXT_DOMAIN = "lliurex-flavours-selector"
ICONS_THEME="/usr/share/icons/breeze/actions/32"
