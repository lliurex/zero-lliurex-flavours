import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Rectangle{
    visible: true
    color:"transparent"

    ColumnLayout{
        id: loadGrid
        anchors.centerIn: parent
        width: parent.width * 0.9
        spacing: 15

        ColumnLayout{
            Layout.alignment:Qt.AlignHCenter
            spacing:10

            AnimatedImage{
                source: "/usr/lib/python3.10/dist-packages/lliurexflavourselector/rsrc/loading.gif"
                Layout.preferredWidth: 32
                Layout.preferredHeight: 32
                Layout.alignment: Qt.AlignHCenter
                fillMode: Image.PreserveAspectFit
            }

            Text{
                id:loadtext
                text:i18nd("lliurex-flavours-selector","Loading information. Wait a moment...")
                font.pointSize: 10
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }

}
