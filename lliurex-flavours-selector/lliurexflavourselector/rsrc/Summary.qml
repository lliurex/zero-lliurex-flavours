import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC

Popup {

    id:summaryPopUp
    signal btnApplyClicked
    signal btnCancelClicked
   
    width:650
    height:450
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
   
    contentItem:Rectangle{
        id:container
        width:650
        height:450
        color:"transparent"
        Image{
            id:dialogIcon
            source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"

        }
        Text{
            id:titleSummary 
            text:i18nd("lliurex-flavours-selector","Changes to be applied to the system")
            font.pointSize: 16
            anchors.left:dialogIcon.right
            anchors.verticalCenter:dialogIcon.verticalCenter
            anchors.leftMargin:10
        }
        GridLayout{
            id:summaryLayout
            rows:5
            flow: GridLayout.TopToBottom
            rowSpacing:0
            anchors.left:parent.left
            anchors.topMargin:80
            enabled:true

            Text{
                id:installText
                text:i18nd("lliurex-flavours-selector","Flavours to install:")+"\n"+flavourStackBridge.flavoursToInstallList
                visible:mainStackBridge.enableInstallAction
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 11
                Layout.leftMargin:10
                Layout.topMargin:80
                Layout.preferredWidth:480
                wrapMode: Text.WordWrap
            }

            Text{
                id:uninstallText
                text:i18nd("lliurex-flavours-selector","Flavours to remove:")+"\n"+flavourStackBridge.flavoursToRemoveList
                visible:mainStackBridge.enableRemoveAction
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 11
                Layout.leftMargin:10
                Layout.topMargin:mainStackBridge.enableInstallAction?10:80
                Layout.preferredWidth:480
                wrapMode: Text.WordWrap
            }

            Text{
                id:additionalActions
                text:i18nd("lliurex-flavours-selector","Additional actions:")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 11
                visible:{
                    if (mainStackBridge.enableCartAction || mainStackBridge.enableRemoveAction){
                        true
                    }else{
                        false
                    }
                }
                Layout.leftMargin:10
            }
            
            RowLayout{
                id:cartRow
                Layout.alignment:Qt.AlignLeft
                Layout.leftMargin:15
                Layout.bottomMargin:10
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
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
                Layout.leftMargin:15
                onToggled:{
                    mainStackBridge.onAutoRemoveChecked(checked)
                }
            }
           
             
        }
        RowLayout{
            id:btnBox
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.topMargin:10
            anchors.bottomMargin:10
            anchors.rightMargin:10
            spacing:10

            PC.Button {
                id:applyBtn
                visible:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:i18nd("lliurex-flavours-selector","Accept")
                Layout.preferredHeight:40
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
                Layout.preferredHeight: 40
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
