import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QMLTermWidget


Rectangle{
    color:"transparent"
    Text{ 
        text:{
            if (mainStackBridge.launchedProcess=="uninstall"){  
                i18nd("lliurex-flavours-selector","Uninstallation process details")
            }else{
                i18nd("lliurex-flavours-selector","Installation process details")
            }
        }
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    RowLayout{
        id:terminalLayout
        anchors.left:parent.left
        width:parent.width-10
        height:parent.height-25
        
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.topMargin:40
            QMLTermWidget {
                id: terminal
                anchors.fill: parent
                font.family: "Monospace"
                font.pointSize: 9
                colorScheme: "cool-retro-term"
                session: QMLTermSession{
                    id: mainsession
                    initialWorkingDirectory: "$HOME"
                }
                Component.onCompleted: {
                    mainsession.startShellProgram();
                    mainsession.sendText('setterm -cursor off;stty -echo;PS1="";history -c;clear;\n');
                }

            }

            QMLTermScrollbar {
                terminal: terminal
                width: 20
                Rectangle {
                    opacity: 0.8
                    anchors.margins: 5
                    radius: width * 0.5
                    anchors.fill: parent
                }
            }
        
        }
    }
    
    function runCommand(command){
        mainsession.sendText('\n')
        mainsession.sendText(command)

    } 

} 
