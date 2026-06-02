import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15 
import org.kde.plasma.components 3.0 as PC
import org.kde.kirigami 2.16 as Kirigami

Popup {

    id:summaryPopUp
    signal btnApplyClicked
    signal btnCancelClicked
   
    width:650
    height:480
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    closePolicy:Popup.NoAutoClose
    
    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }
   
    contentItem:Item{
 
        RowLayout {
            id: headerRow
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 10

            Kirigami.Icon {
                id:dialogIcon
                Layout.preferredWidth: Kirigami.Units.iconSizes.huge
                Layout.preferredHeight: Kirigami.Units.iconSizes.huge
                source:"dialog-warning"

            }

            Text{
                id:titleSummary 
                text:i18nd("lliurex-flavours-selector","Changes to be applied to the system")
                font.pointSize: 16
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }
        }

        ColumnLayout{
            id:summaryLayout
            anchors.top:headerRow.bottom
            anchors.left:parent.left
            anchors.right:parent.right
            anchors.bottom:btnBox.top
            anchors.topMargin:20
            anchors.bottomMargin:20
            anchors.leftMargin:10
            spacing:8

            Text{
                id:installText
                text:i18nd("lliurex-flavours-selector","Flavours to install:")+"\n"+flavourStackBridge.flavoursToInstallList
                visible:mainStackBridge.enableInstallAction
                font.pointSize: 11
                Layout.fillWidth:true
                wrapMode: Text.WordWrap
            }

            Text{
                id:uninstallText
                text:i18nd("lliurex-flavours-selector","Flavours to remove:")+"\n"+flavourStackBridge.flavoursToRemoveList
                visible:mainStackBridge.enableRemoveAction
                font.pointSize: 11
                Layout.fillWidth:true
                wrapMode: Text.WordWrap
            }

            Text{
                id:additionalActions
                text:i18nd("lliurex-flavours-selector","Additional actions:")
                font.pointSize: 11
                visible:mainStackBridge.enableCartAction || mainStackBridge.enableRemoveAction?true:false
             }
            
            RowLayout{
                id:cartRow
                Layout.leftMargin:10
                visible:mainStackBridge.enableCartAction
                spacing:10

                PC.CheckBox {
                    id:configureCartCB
                    text:i18nd("lliurex-flavours-selector","Assign laptop to a cart (by default it will be assigned to cart 1):")
                    font.pointSize: 11
                    focusPolicy: Qt.NoFocus
                    Layout.alignment:Qt.AlignLeft
                    onToggled:{
                        mainStackBridge.onConfigureCartChecked(checked)
                    }
                }

                ComboBox {
                    id:cartsValues
                    currentIndex:0
                    model:14
                    delegate:ItemDelegate{
                        width:40
                        text:index+1
                    }
                    enabled:configureCartCB.checked?true:false
                    displayText:currentIndex+1
                    Layout.alignment:Qt.AlignLeft
                    Layout.preferredWidth:60
                    onActivated:{
                        mainStackBridge.updateCart(cartsValues.currentIndex)
                    }
                }

            }

            PC.CheckBox {
                id:autoRemoveCB
                text:i18nd("lliurex-flavours-selector","Remove other installed packages that are no longer neeed")
                visible:mainStackBridge.enableRemoveAction
                font.pointSize: 11
                focusPolicy: Qt.NoFocus
                Layout.leftMargin:10
                onToggled:{
                    mainStackBridge.onAutoRemoveChecked(checked)
                }
            }
            Item{
                Layout.fillHeight:true
            }
           
             
        }
        RowLayout{
            id:btnBox
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.bottomMargin:10
            spacing:10

            PC.Button {
                id:applyBtn
                visible:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:i18nd("lliurex-flavours-selector","Accept")
                enabled:true
		        focusPolicy: Qt.NoFocus
                onClicked:{
                    configureCartCB.checked=false
                    cartsValues.currentIndex=0
                    autoRemoveCB.checked=false
                    btnApplyClicked()
                }
            }
            
            PC.Button {
                id:cancelBtn
                visible:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel"
                text:i18nd("lliurex-flavours-selector","Cancel")
                enabled:true
                focusPolicy: Qt.NoFocus
                onClicked:{
                    autoRemoveCB.checked=false
                    cartsValues.currentIndex=0
                    configureCartCB.checked=false
                    btnCancelClicked()
                }                
            }

        }
    }

}
