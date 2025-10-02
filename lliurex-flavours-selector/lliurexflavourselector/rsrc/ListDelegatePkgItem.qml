import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as PC


PC.ItemDelegate{
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

	    height:isVisible?80:0
	    enabled:true
	      
	    Rectangle{
	    	height:isVisible?80:0
	    	width:parent.width
	    	color:{
	    		if (type=="parent"){
	    			"#add8e6"
	    		}else{
	    			"transparent"
	    		}

	    	}
	    	visible:isVisible
	    	border.color:"transparent"

			states: State {
                name: "expanded"
                when: isExpanded
                PropertyChanges {
                    target: menuItem
                    visible: true
                }
            }

            transitions:[
                Transition {
                    from: ""
                    to: "expanded"
                    reversible: true
                    SequentialAnimation {
                        PropertyAnimation { property: "visible"; duration: 5 }
                    }
                }
            ]
	    	Item{
				id: menuItem
				height:isVisible?80:0
				width:parent.width-25

				Image{
                	id:menuOptionIcon
                	source:{
                    	if (isExpanded){
                        	"/usr/share/icons/breeze/actions/22/go-down.svg"
                    	}else{
                        	"/usr/share/icons/breeze/actions/22/go-next.svg"
                    	}
                	}
                	visible:{
                		if (type=="parent"){
                			true
                		}else{
                			false
                		}
                	}
                	anchors.left:parent.left
                	anchors.verticalCenter:parent.verticalCenter
                	anchors.leftMargin:10
               		MouseArea{
                    	function expand(isExpanded,pkg) {
                        	for(var i = 0; i < listPkg.count; ++i) {
                            	var item=flavourStackBridge.getModelData(i)
                            	console.log(item["pkg"])
                            	if (item["pkg"]===pkg){
                                	flavourStackBridge.onExpandedParent([pkg,"isExpanded",isExpanded])
                            	}else{
                            		console.log(item["flavourParent"])
                            		if (item["flavourParent"]===pkg){
                            			console.log("MATCH")
                            			flavourStackBridge.onExpandedParent([item["pkg"],"isVisible",isExpanded])
                            		}
                            	}
                            	
                       		}
                    	}	 
                    	anchors.fill:parent
                    	
                    	onClicked:{
                    		console.log("EXPANDED: "+isExpanded)
                        	if (type == "parent") {
                           		if (isExpanded == false) {
                                	expand(true,pkg)
                                	isExpanded=true
                            	}else{
                                	expand(false,pkg)
                                	isExpanded=false
                            	}
                            	

                        	}
                    	}
                	}
                }
				PC.CheckBox {
					id:packageCheck
					visible:{
						if (type=="child"){
							true
						}else{
							false
						}
					}
					checked:isChecked
					onToggled:{
						flavourStackBridge.onCheckedFlavour([pkg,checked])
					}
					anchors.left:parent.left
					anchors.leftMargin:{
						if (type=="parent"){
							10
						}else{
							30
						}
					}
					anchors.verticalCenter:parent.verticalCenter
					enabled:flavourStackBridge.enableFlavourList
				}

				Image {
					id:packageIcon
					visible:{
						if (type=="child"){
							true
						}else{
							false
						}
					}
					source:"image://iconProvider/"+banner
					sourceSize.width:64
					sourceSize.height:64
					anchors.left:packageCheck.right
					anchors.verticalCenter:parent.verticalCenter
					anchors.leftMargin:10
					cache:false
				} 

				Text{
					id: pkgName
					text: name
					width: {
						if ((showSpinner) || (resultImg.visible)){
							parent.width-resultImg.width-150
						}else{
							parent.width-150
						}
					}
					elide:Text.ElideMiddle
					clip: true
					font.family: "Quattrocento Sans Bold"
					font.pointSize: 10
					anchors.leftMargin:10
					font.bold:{
						if (type=="parent"){
							true
						}else{
							false
						}
					}
					anchors.left:packageIcon.right
					anchors.verticalCenter:parent.verticalCenter
				} 

				Image {
					id: resultImg
					source:{
						if (resultProcess==0){
		                    "/usr/share/icons/breeze/status/24/data-success.svg"
						}else{
		                    "/usr/share/icons/breeze/status/24/data-error.svg"
						}
					}
					visible:{
						if (resultProcess!=-1){
							true
						}else{
							false
						}
					}
					sourceSize.width:32
					sourceSize.height:32
					anchors.leftMargin:10
					anchors.rightMargin:1.5
					anchors.right:parent.right
					anchors.verticalCenter:parent.verticalCenter
				}
				Rectangle{
					id:animationFrame
					color:"transparent"
					width:0.4*(animation.width)
					height:0.4*(animation.height)
					anchors.leftMargin:10
					anchors.right:parent.right
					anchors.verticalCenter:parent.verticalCenter
					visible:{
						if ((packageCheck.checked) && (showSpinner)){
							mainStackBridge.isProcessRunning
						}else{
						false
						}
					}

					AnimatedImage{
						id:animation
						source: "/usr/lib/python3.12/dist-packages/lliurexflavourselector/rsrc/loading.gif"
						transform: Scale {xScale:0.40;yScale:0.40}
						paused:!animationFrame.visible
					}
				}

			}

		}
}
