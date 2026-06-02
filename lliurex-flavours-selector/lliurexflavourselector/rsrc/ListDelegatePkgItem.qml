import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami

PC.ItemDelegate {
    id: listPkgItem

    property string pkgId
    property string pkg
    property bool isChecked
    property string name
    property string banner
    property string status
    property bool isVisible
    property int resultProcess
    property bool showSpinner
    property bool isManaged
    property bool isExpanded
    property string type
    property string flavourParent
    property int showAction

    height: !isVisible ? 0 : (type === "parent" ? 30 : (isExpanded ? 50 : 0))
    enabled: true

    Rectangle {
        id: containerParent
        height: !isVisible ? 0 : (type === "parent" ? 28 : (isExpanded ? 48 : 0))
        width: parent.width - 20
        visible: type === "parent" ? isVisible : (isExpanded && isVisible)
        border.color: "transparent"

        color: {
            if (type === "parent") {
                return "#add8e6"
            }
            switch(showAction) {
                case 1:  return "#f0d6bf"
                case 2:  return "#c7e2d2"
                default: return "transparent"
            }
        }

        states: State {
            name: "expanded"
            when: isExpanded
            PropertyChanges {
                target: menuItem
                visible: true
            }
        }

        transitions: Transition {
            from: ""
            to: "expanded"
            reversible: true
            SequentialAnimation {
                PropertyAnimation { property: "visible"; duration: 5 }
            }
        }

        Item {
            id: menuItem
            height: containerParent.height
            width: containerParent.width - 25

            Rectangle {
                id: expandedContainer
                width: 24
                height: 24
                visible: type === "parent"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 10
                border.color: "transparent"
                radius: 5.0
                color: "transparent"

                Kirigami.Icon {
                    id: expandParentIcon
                    source: isExpanded ? "go-down" : "go-next"
                    width: Kirigami.Units.iconSizes.smallMedium
                    height: Kirigami.Units.iconSizes.smallMedium
                    visible: type === "parent"
                    anchors.centerIn: parent

                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: (type === "parent") && mouseAreaExpand.hovered
                    ToolTip.text: isExpanded ? i18nd("lliurex-flavours-selector", "Click to hide flavours") : i18nd("lliurex-flavours-selector", "Click to show flavours")
                }

                MouseArea {
                    id: mouseAreaExpand
                    anchors.fill: parent
                    hoverEnabled: true
                    property bool hovered: false

                    onEntered: {
                        hovered = true
                        expandedContainer.border.color = "#308cc6"
                        expandedContainer.color = "#d5eaf2"
                    }
                    onExited: {
                        hovered = false
                        expandedContainer.border.color = "transparent"
                        expandedContainer.color = "transparent"
                    }
                    onClicked: {
                        if (type === "parent") {
                            flavourStackBridge.onExpandedParent({"pkg":pkg, "isExpanded":!isExpanded})
                        }
                    }
                }
            }

            PC.CheckBox {
                id: packageCheck
                visible: type === "child"
                checked: isChecked
                enabled: isManaged && flavourStackBridge.enableFlavourList
                         ?true
                         :false
                anchors.left: expandedContainer.right
                anchors.leftMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                onToggled: {
                    flavourStackBridge.onCheckedFlavour({"pkg":pkg, "isChecked":checked})
                }
            }

            Kirigami.Icon {
                id: actionIcon
                visible: showAction !== -1
                anchors.left: packageCheck.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 5
                width: Kirigami.Units.iconSizes.medium
                height: Kirigami.Units.iconSizes.medium
                source: {
                    switch(showAction) {
                        case 0:  return "data-success"
                        case 1:  return "edit-delete"
                        case 2:  return "edit-download"
                        default: return "package-available"
                    }
                }
            }

            Image {
                id: packageIcon
                visible: type === "child"
                source: banner
                cache: false
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 10
                sourceSize.width: type === "child" ? 54 : 22
                sourceSize.height: type === "child" ? 36 : 22
                anchors.left: type === "child" ? (showAction !== -1 ? actionIcon.right : packageCheck.right) : expandedContainer.right
            }

            Text {
                id: pkgName
                text: name
                elide: Text.ElideMiddle
                clip: true
                font.pointSize: 10
                font.bold: type === "parent"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: type === "child" ? packageIcon.right : expandedContainer.right
                anchors.leftMargin: 10

                width: {
                    let reservedSpace = (type === "child") ? 175 : 75
                    if (showSpinner || resultImg.visible) {
                        return menuItem.width - (32 + 32 + reservedSpace) 
                    }
                    return menuItem.width - reservedSpace
                }
            }

            Kirigami.Icon {
                id: resultImg
                visible: resultProcess !== -1
                width: Kirigami.Units.iconSizes.medium
                height: Kirigami.Units.iconSizes.medium
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                source: resultProcess === 0 ? "data-success" : "data-error"
            }

            Rectangle {
                id: animationFrame
                color: "transparent"
                width: 24
                height: 24
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                visible: showSpinner && mainStackBridge.isProcessRunning

                AnimatedImage {
                    id: animation
                    source: "file:///usr/lib/python3.12/dist-packages/lliurexflavourselector/rsrc/loading.gif"
                    anchors.fill: parent
                    paused: !animationFrame.visible
                }
            }
        }
    }
}
