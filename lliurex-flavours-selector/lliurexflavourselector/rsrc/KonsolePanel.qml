import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QMLTermWidget


Rectangle{
    color:"transparent"
    Layout.fillWidth:true
    Layout.fillHeight:true

    ColumnLayout{
        id:terminalLayout
        spacing: 25
        anchors.rightMargin:5
        anchors.fill:parent
        anchors.bottomMargin:10
    
        Text{ 
            text:mainStackBridge.launchedProcess=="uninstall"
                ?i18nd("lliurex-flavours-selector","Uninstallation process details")
                :i18nd("lliurex-flavours-selector","Installation process details")
            font.pointSize: 16
        }
        
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
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
