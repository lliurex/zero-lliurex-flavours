import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("lliurex-flavours-selector","List of Flavours availables")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:generalFlavoursLayout
        rows:1
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        width:parent.width-15
        height:parent.height-45
        enabled:true

        FlavoursList{
            id:flavoursList
            Layout.fillHeight:true
            Layout.fillWidth:true
            flavoursModel:flavourStackBridge.flavoursModel
        }
    
    }
} 
