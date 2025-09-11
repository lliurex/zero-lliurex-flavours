import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs


Rectangle{
    visible: true
    color:"transparent"

    GridLayout{
        id: loadGrid
        rows: 2
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Rectangle{
                color:"transparent"
                width:30
                height:30
                
                AnimatedImage{
                    source: "/usr/lib/python3.12/dist-packages/lliurexflavourselector/rsrc/loading.gif"
                    transform: Scale {xScale:0.45;yScale:0.45}
                }
            }
        }

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:loadtext
                text:i18nd("lliurex-flavours-selector","Loading information. Wait a moment...")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }

}
