import org.kde.plasma.core 2.1 as PlasmaCore
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "Lliurex Flavours Selector"
    color:"#eff0f1"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
    minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
    
    Component.onCompleted: {
        x:(Screen.width-width)/2
        y:(Screen.height-height)/2
    }
    
    onClosing:(close)=> {
        close.accepted=closing;

        if (!closing) {
            mainStackBridge.closeApplication();
            closeTimer.start();
        }
        
    }

    Timer {
        id: closeTimer
        interval: 100
        repeat: true
        onTriggered: {
            if (mainStackBridge.closeGui) {
                stop();
                mainWindow.closing = true;
                mainWindow.close();
            }
        }
    }

    
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        Layout.minimumWidth:800
        Layout.minimumHeight:600

        Rectangle{
            color: "#07227d"
            Layout.fillWidth:true
            Layout.preferredHeight: 120
            Image{
                id:banner
                source: "/usr/lib/python3.12/dist-packages/lliurexflavourselector/rsrc/flavourselector-banner.png"
                anchors.centerIn: parent
                fillMode: Image.PreserveAspectFit  
            }
        }

        StackView {
            id: mainView
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight:475

            property int currentView:mainStackBridge.currentStack

            initialItem:loadingView

            onCurrentViewChanged:{
                switch(currentView){
                    case 0:
                        mainView.replace(loadingView)
                        break;
                    case 1:
                        mainView.replace(errorView)
                        break;
                    case 2:
                        mainView.replace(applicationOptionView)
                        break
                }
            }

            replaceEnter: Transition {
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: 60
                }
            }
            
            replaceExit: Transition {
                NumberAnimation { 
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: 60
                }
            }
        }
         
        Component{
           id:loadingView
           Loading{
               id:loading
           }

        }

        Component{
            id:applicationOptionView
            ApplicationOptions{
                id:applicationOptions
            }
        }
    }
}

