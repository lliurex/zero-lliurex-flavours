#!/bin/bash

xgettext --join-existing -L python ./lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy -o ./translations/lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy.pot
xgettext --join-existing ./lliurex-flavours-selector-legacy/python3-lliurexflavourselector/MainWindow.py -o ./translations/lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy.pot
xgettext --join-existing ./lliurex-flavours-selector-legacy/python3-lliurexflavourselector/InstallersBox.py -o ./translations/lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy.pot
xgettext --join-existing ./lliurex-flavours-selector-legacy/python3-lliurexflavourselector/LoadingBox.py -o ./translations/lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy.pot
xgettext --join-existing ./lliurex-flavours-selector-legacy/python3-lliurexflavourselector/EmptyBox.py -o ./translations/lliurex-flavours-selector-legacy/lliurex-flavours-selector-legacy.pot
