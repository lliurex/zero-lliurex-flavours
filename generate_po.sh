#!/bin/bash
xgettext --join-existing -L python ./lliurex-flavours-selector/lliurex-flavours-selector -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/ApplicationOptions.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/FlavoursList.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/FlavoursPanel.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/KonsolePanel.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/ListDelegatePkgItem.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/Loading.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
xgettext --join-existing -kde -ki18nd:2 ./lliurex-flavours-selector/python3-lliurexflavourselector/rsrc/Summary.qml -o ./translations/lliurex-flavours-selector/lliurex-flavours-selector.pot
