import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


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
