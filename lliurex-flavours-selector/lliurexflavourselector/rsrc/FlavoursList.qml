import QtQuick
import QtQuick.Controls
import QtQml.Models 2.8
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick.Layouts


Rectangle{
    id: optionsGrid
    property alias flavoursModel:filterModel.model
    property alias listCount:listPkg.count
    Layout.fillWidth:true
    Layout.fillHeight:true
    color:"transparent"


    ColumnLayout{
        id:mainGrid
        anchors.fill:parent
        spacing:10

        RowLayout{
            id: btnRow
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignLeft
            spacing:10
            enabled:true

            PC.Button{
                id:expandBtn
                display:AbstractButton.IconOnly
                icon.name:"view-list-tree"
                visible:true
                enabled:flavourStackBridge.enableFlavourList
                Layout.rightMargin:5
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-flavours-selector","Click to expand the list of flavours")
                onClicked:flavourStackBridge.manageExpansionList("expand")

            }
            
            PC.Button{
                id:retryBtn
                display:AbstractButton.IconOnly
                icon.name:"view-list-details"
                visible:true
                enabled:flavourStackBridge.enableFlavourList
                Layout.rightMargin:mainGrid.width-(expandBtn.width+statusFilterBtn.width+pkgSearchEntry.width+60)
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-flavours-selector","Click to collapse the list of flavours")
                onClicked:flavourStackBridge.manageExpansionList("collpase")
            }

            PC.Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter"
                visible:true
                enabled:flavourStackBridge.totalErrorInProcess!==0
                        || (flavourStackBridge.enableFlavourList
                            && !flavourStackBridge.isAllInstalled.allInstalled
                            && !flavourStackBridge.isAllInstalled.allAvailable)
                
                ToolTip.delay: 1000
                ToolTip.timeout: 3000
                ToolTip.visible: hovered
                ToolTip.text:i18nd("lliurex-flavours-selector","Click to filter flavour by status")
                Layout.alignment:Qt.AlignRight
                onClicked:optionsMenu.open();
               
                PC.Menu{
                    id:optionsMenu
                    y: statusFilterBtn.height
                    x:-(optionsMenu.width-statusFilterBtn.width/2)

                    PC.MenuItem{
                        icon.name:"installed"
                        text:i18nd("lliurex-flavours-selector","Show installed Flavours")
                        enabled:flavourStackBridge.filterStatusValue!="installed"?true:false
                        onClicked:flavourStackBridge.manageStatusFilter("installed")
                    }

                    PC.MenuItem{
                        icon.name:"noninstalled"
                        text:i18nd("lliurex-flavours-selector","Show uninstalled Flavours")
                        enabled:flavourStackBridge.filterStatusValue!="available"?true:false
                        onClicked:flavourStackBridge.manageStatusFilter("available")
                    }
                    PC.MenuItem{
                        icon.name:"emblem-error"
                        text:i18nd("lliurex-flavours-selector","Show Flavours with error")
                        enabled:flavourStackBridge.filterStatusValue!="error"
                                && flavourStackBridge.totalErrorInProcess>0
                        onClicked:flavourStackBridge.manageStatusFilter("error")
                    }
                    PC.MenuItem{
                        icon.name:"kt-remove-filters"
                        text:i18nd("lliurex-flavours-selector","Remove filter")
                        enabled:flavourStackBridge.filterStatusValue!="all"?true:false
                        onClicked:flavourStackBridge.manageStatusFilter("all")
                    }
                }
            }
                
            PC.TextField{
                id:pkgSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                visible:true
                enabled:flavourStackBridge.enableFlavourList
                placeholderText:i18nd("lliurex-flavours-selector","Search...")
                onTextChanged:{
                    filterModel.update()
                }
            }
        }

        Rectangle {
            id:pkgTable
            visible: true
            color:"white"
            Layout.fillHeight:true
            Layout.fillWidth:true
       
            border.color: "#d3d3d3"

            PC.ScrollView{
                anchors.fill:parent
       
                ListView{
                    id: listPkg

                    Timer {
                        id: searchTimer
                        interval: 150
                        repeat: false
                        onTriggered: filterModel.update()
                    }

                    model:FilterDelegateModel{
                        id:filterModel
                        model:flavoursModel
                        role:"name"
                        search:pkgSearchEntry.text.trim()
                        statusFilter:flavourStackBridge.filterStatusValue
                        externalTimer: searchTimer
                        
                        delegate: ListDelegatePkgItem{
                            width:pkgTable.width
                            pkgId:model.pkgId
                            pkg:model.pkg
                            isChecked:model.isChecked
                            name:model.name
                            banner:model.banner
                            status:model.status
                            isVisible:model.isVisible
                            resultProcess:model.resultProcess
                            showSpinner:model.showSpinner
                            isManaged:model.isManaged
                            isExpanded:model.isExpanded
                            type:model.type
                            flavourParent:model.flavourParent
                            showAction:model.showAction
                        }
                    }

                    currentIndex:-1
                    enabled:true
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightFollowsCurrentItem:true
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listPkg.count==0?true:false
                        text: (pkgSearchEntry.text !== "" || 
                              flavourStackBridge.filterStatusValue !== "all") 
                              ? i18nd("lliurex-flavours-selector", "Flavours not found") 
                              : i18nd("lliurex-flavours-selector", "Flavours not available")
                        icon.name:"zero-lliurex-flavours"
 
                    }

                 } 
            }
        }
            
    }

}
