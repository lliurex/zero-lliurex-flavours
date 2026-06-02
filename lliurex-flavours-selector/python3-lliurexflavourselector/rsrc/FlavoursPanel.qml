import org.kde.plasma.core 2.1 as PlasmaCore
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Rectangle{
    color:"transparent"

    ColumnLayout{
       id: mainContent
       anchors.fill:parent
       anchors.rightMargin:5
       anchors.bottomMargin:10
       spacing:25

       Text{ 
           text:i18nd("lliurex-flavours-selector","List of Flavours availables")
           font.pointSize: 16
       }

       FlavoursList{
           id:flavoursList
           Layout.fillHeight:true
           Layout.fillWidth:true
           flavoursModel:flavourStackBridge.flavoursModel
       }
    
    }
} 
