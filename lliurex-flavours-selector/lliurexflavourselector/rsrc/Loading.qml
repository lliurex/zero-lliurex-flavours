import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle{
    visible: true
    color:"transparent"

    ColumnLayout{
        id: loadRoot
        anchors.centerIn: parent
        width: parent.width * 0.9
        spacing: 15

        ColumnLayout{
            Layout.alignment:Qt.AlignHCenter
            spacing:10

           Image{
                id:spinnerImage
                source: "/usr/lib/python3.12/dist-packages/lliurexflavourselector/rsrc/loading.png"
                Layout.preferredWidth: 24
                Layout.preferredHeight: 24
                Layout.alignment: Qt.AlignHCenter
                fillMode: Image.PreserveAspectFit
                smooth:false
                antialiasing:false

                rotation:0
            }
            
            Timer{
                id:rotationTimer
                running:(spinnerImage!==null && loadRoot!==null) && spinnerImage.visible && loadRoot.visible
                repeat:true
                interval:100

                onTriggered:{

                    if (spinnerImage && typeof spinnerImage.rotation!="undefined"){
                        var nextRotation= spinnerImage.rotation-30

                            if (nextRotation<0){
                                nextRotation=330
                            }
                            spinnerImage.rotation=nextRotation
                     }else{
                        stop()
                     }   

                }
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
