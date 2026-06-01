import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC
import org.kde.kirigami 2.16 as Kirigami

RowLayout{
    id: optionsGrid
    spacing:10

    Rectangle{
        width:130
        Layout.fillHeight:true
        border.color: palette.mid

        ColumnLayout{
            id: menuGrid
            anchors.fill:parent
            spacing:0

            MenuOptionBtn {
                id:packagesOption
                optionText:i18nd("lliurex-flavours-selector","Home")
                optionIcon:"user-home"
                visible:true
                onMenuOptionClicked:mainStackBridge.manageTransitions(0)
            }
            
            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("lliurex-flavours-selector","View details")
                optionIcon:"utilities-terminal"
                visible:mainStackBridge.enableKonsole
                onMenuOptionClicked: mainStackBridge.manageTransitions(1)
            }
            
            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("lliurex-flavours-selector","Help")
                optionIcon:"help-contents"
                onMenuOptionClicked:mainStackBridge.openHelp()
            }

            Item {
                Layout.fillHeight:true
            }
        }
    }

    ColumnLayout{
        id: layoutGrid
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin:5
        Layout.rightMargin:15
        spacing:10

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionsStack
            Layout.fillHeight:true
            Layout.fillWidth:true

            FlavoursPanel{
                id:flavoursPanel
            }

            KonsolePanel{
                id:konsolePanel
            }
           
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:mainStackBridge.showStatusMessage.show
            text:getFeedBackText(mainStackBridge.showStatusMessage.msgCode)
            type:getMsgType()
            Layout.fillWidth:true
            
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:5
            Layout.bottomMargin:15
            Layout.fillWidth:true

            ColumnLayout{
                id:feedbackColumn
                spacing:10
                Layout.alignment:Qt.AlignHCenter
                visible:true
                Text{
                    id:feedBackText
                    text:getFeedBackText(mainStackBridge.feedbackCode)
                    visible:true
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                    Layout.alignment:Qt.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                
                ProgressBar{
                    id:feedBackBar
                    indeterminate:true
                    visible:mainStackBridge.isProgressBarVisible
                    implicitWidth:200
                    implicitHeight:25
                    Layout.alignment:Qt.AlignHCenter
                }
                
            }
               
            PC.Button {
                id:installBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:i18nd("lliurex-flavours-selector","Apply")
                enabled:mainStackBridge.enableApplyBtn?true:false
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
                Layout.leftMargin:10
                onClicked:{
                    summary.open()
                }
            }
        }
    }

    Summary{
        id:summary
        Connections{
            target:summary
            function onBtnApplyClicked(){
                summary.close()
                konsolePanel.runCommand('history -c\n')
                applyChanges()
                mainStackBridge.launchChangeProcess()
            }
            function onBtnCancelClicked(){
                summary.close()
            } 

        }     
    }

    Timer{
        id:timer
        interval:100
        repeat:true
        onTriggered:{
            if (mainStackBridge.endProcess){
                timer.stop()
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }  
            }
        }
    }

    function applyChanges(){
        timer.restart()
    }
    
    function getFeedBackText(code){

        switch (code){
            case -1:
            case -2:
                return i18nd("lliurex-flavours-selector","Installation process has ending with errors");
           case -4:
                return i18nd("lliurex-flavours-selector","Internet connection not detected")
            case -5:
            case -6:
                return i18nd("lliurex-flavours-selector","Uninstallation process has ending with errors");
            case -7:
                return i18nd("lliurex-flavours-selector","The process has ending with errors")
            case -8:
                return i18nd("lliurex-flavours-selector","The process has ending with errors due to unresolved incompatibilities between flavours")
            case 1:
                return i18nd("lliurex-flavours-selector","Installation process has ending successfully. It's necessary to restart the system");
           case 3:
                return i18nd("lliurex-flavours-selector","Checking internet connection. Wait a moment...")
            case 4:
                return i18nd("lliurex-flavours-selector","Preparing installation. Wait a moment...")
            case 5:
                return i18nd("lliurex-flavours-selector","Installing selected Flavours. Wait a moment...")
            case 6:
                return i18nd("lliurex-flavours-selector","Uninstalling selected Flavours. Wait a moment...")
            case 7:
                return i18nd("lliurex-flavours-selector","Uninstallation process has ending successfully. It's necessary to restart the system")
            case 8:
                return i18nd("lliurex-flavours-selector","A current installed flavour will be remove due to incompatibility with other selected flavours")
            case 9:
                return i18nd("lliurex-flavours-selector","The process has ending successfully. It's necessary to restart the system")
            case 10:
                return i18nd("lliurex-flavours-selector","Removing packages that are no longer neeed. Wait a moment...")
            case 11:
                return i18nd("lliurex-flavours-selector","Activating metapackages protection. Wait a moment...")
            case 12:
                return i18nd("lliurex-flavours-selector","Assigning the laptop to cart %1. Wait a moment...", mainStackBridge.selectedCart)
            default:
                return ""
        }
    }

    function getMsgType(){

        switch(mainStackBridge.showStatusMessage.type){
            case 0:
                return Kirigami.MessageType.Positive;
            case 1:
                return Kirigami.MessageType.Error;
            case 2:
                return Kirigami.MessageType.Warning;
            case 3:
            default:
                return Kirigami.MessageType.Information;
         }
    }

}

