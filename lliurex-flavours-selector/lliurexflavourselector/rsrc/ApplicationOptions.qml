import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami

GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:130
        Layout.minimumHeight:480
        Layout.preferredHeight:480
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:3 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:packagesOption
                optionText:i18nd("lliurex-flavours-selector","Home")
                optionIcon:"/usr/share/icons/breeze/places/22/user-home.svg"
                visible:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(0)
                      
                    }
                }
            }
            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("lliurex-flavours-selector","View details")
                optionIcon:"/usr/share/icons/breeze/apps/22/utilities-terminal.svg"
                visible:mainStackBridge.enableKonsole
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(1)
                    }
                }
            }
            
            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("lliurex-flavours-selector","Help")
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp()
                    }
                }
            }
        }
    }

    GridLayout{
        id: layoutGrid
        rows:3 
        flow: GridLayout.TopToBottom
        rowSpacing:0

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionsStack
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignHCenter

            FlavoursPanel{
                id:flavoursPanel
            }

            KonsolePanel{
                id:konsolePanel
            }
           
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:mainStackBridge.showStatusMessage[0]
            text:getFeedBackText(mainStackBridge.showStatusMessage[1])
            type:getMsgType()
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.rightMargin:10
            
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:10
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
                    font.family: "Quattrocento Sans Bold"
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
                    implicitHeight:mainStackBridge.runPkexec?7:25
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
                Layout.preferredHeight:40
                Layout.leftMargin:10
                Layout.rightMargin:10
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
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
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }
   
    function applyChanges(){
        delay(100, function() {
            if (mainStackBridge.endProcess){
                timer.stop()
                
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 
    
    function getFeedBackText(code){

        var msg="";
        switch (code){
            case -1:
            case -2:
                msg=i18nd("lliurex-flavours-selector","Installation process has ending with errors");
                break;
           case -4:
                msg=i18nd("lliurex-flavours-selector","Internet connection not detected")
                break;
            case -5:
            case -6:
                msg=i18nd("lliurex-flavours-selector","Uninstallation process has ending with errors");
                break;
            case -7:
                msg=i18nd("lliurex-flavours-selector","The process has ending with errors")
                break;
            case -8:
                msg=i18nd("lliurex-flavours-selector","The process has ending with errors due to unresolved incompatibilities between flavours")
                break;
            case 1:
                msg=i18nd("lliurex-flavours-selector","Installation process has ending successfully. It's necessary to restart the system");
                break;
           case 3:
                msg=i18nd("lliurex-flavours-selector","Checking internet connection. Wait a moment...")
                break;
            case 4:
                msg=i18nd("lliurex-flavours-selector","Preparing installation. Wait a moment...")
                break;
            case 5:
                msg=i18nd("lliurex-flavours-selector","Installing selected Flavours. Wait a moment...")
                break;
            case 6:
                msg=i18nd("lliurex-flavours-selector","Uninstalling selected Flavours. Wait a moment...")
                break;
            case 7:
                msg=i18nd("lliurex-flavours-selector","Uninstallation process has ending successfully. It's necessary to restart the system")
                break;
            case 8:
                msg=i18nd("lliurex-flavours-selector","A current installed flavour will be remove due to incompatibility with other selected flavours")
                break;
            case 9:
                msg=i18nd("lliurex-flavours-selector","The process has ending successfully. It's necessary to restart the system")
                break;
            case 10:
                msg=i18nd("lliurex-flavours-selector","Removing packages that are no longer neeed. Wait a moment...")
                break;
            case 11:
                msg=i18nd("lliurex-flavours-selector","Activating metapackages protection. Wait a moment...")
                break;
            default:
                break;
        }
        return msg;
    }

    function getMsgType(){

        switch(mainStackBridge.showStatusMessage[2]){
            case "Ok":
                return Kirigami.MessageType.Positive;
            case "Error":
                return Kirigami.MessageType.Error;
            case "Info":
                return Kirigami.MessageType.Information;
            case "Warning":
                return Kirigami.MessageType.Warning;
        }
    }

}

