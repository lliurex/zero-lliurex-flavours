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
	    property int showAction

	    height:{
	    	if (isVisible){
	    		if (type==="child"){
	    			85
	    		}else{
	    			45
	    		}
	    	}else{
	    		0	
	    	}
	    }
	    enabled:true
	      
	    Rectangle{
	    	height:{
	    		if (isVisible){
	    			if (type==="child"){
	    				80
	    			}else{
	    				40
	    			}
	    		}else{
	    			0	
	    		}
	    	}
	    	width:parent.width
	    	color:{
	    		if (type=="parent"){
	    			"#add8e6"
	    		}else{
	    			switch(showAction){
	    				case 0:
	    				case -1:
	    					"transparent"
	    					break
	    				case 1:
	    					"#f0d6bf"
	    					break
	    				case 2:
	    					"#c7e2d2"
	    					break
	    			}
	    			
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
				height:{
					if (isVisible){
						if (type==="child"){
							80
						}else{
							40
						}
					}else{
						0	
					}
				}

				width:parent.width-25

				Image{
                	id:expandParentIcon
                	source:{
                    	if (isExpanded){
                        	"/usr/share/icons/breeze/actions/24/go-down.svg"
                    	}else{
                        	"/usr/share/icons/breeze/actions/24/go-next.svg"
                    	}
                	}
                	visible:{
                		if (type==="parent"){
                			true
                		}else{
                			false
                		}
                	}
                	anchors.left:parent.left
                	anchors.verticalCenter:parent.verticalCenter
                	anchors.leftMargin:10
                	enabled: {
                		if ((flavourStackBridge.filterStatusValue=="all") && (pkgSearchEntry.text.trim()=="")){
                			true
                		}else{
                			false
                		}
                	}
               		MouseArea{
                    	function expand(isExpanded,pkg) {
                        	for(var i = 0; i < listPkg.count; ++i) {
                            	var item=flavourStackBridge.getModelData(i)
                              	if (item["pkg"]===pkg){
                                	flavourStackBridge.onExpandedParent([pkg,"isExpanded",isExpanded])
                            	}else{
                            		if (item["flavourParent"]===pkg){
                            			flavourStackBridge.onExpandedParent([item["pkg"],"isVisible",isExpanded])
                            		}
                            	}
                            	
                       		}
                    	}	 
                    	anchors.fill:parent
                    	
                    	onClicked:{
                        	if (type === "parent") {
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
						if (type==="child"){
							true
						}else{
							false
						}
					}
					checked:isChecked
					onToggled:{
						flavourStackBridge.onCheckedFlavour([pkg,checked])
					}
					anchors.left:expandParentIcon.right
					anchors.leftMargin:10
					anchors.verticalCenter:parent.verticalCenter
					enabled:isManaged
				}

				Image {
					id:actionIcon
					source:{
						switch(showAction){
							case 0:
								"/usr/share/icons/breeze/status/24/data-success.svg"
								break
							case 1:
								"/usr/share/icons/breeze/actions/24/edit-delete.svg"
								break;
							case 2:
								"/usr/share/icons/breeze/actions/24/edit-download.svg"
								break
							default:
								"/usr/share/icons/breeze/emblems/16/package-available.svg"
								break;
						}
	               	}
					visible:{
						if (showAction!=-1){
							true
						}else{
							false
						}
					}
					anchors.left:packageCheck.right
                	anchors.verticalCenter:parent.verticalCenter
                	anchors.leftMargin:10
                	sourceSize.width:32
					sourceSize.height:32
				}

				Image {
					id:packageIcon
					visible:{
						if (type==="child"){
							true
						}else{
							false
						}
					}
					source:"image://iconProvider/"+banner
					sourceSize.width:{
						if (type=="child"){
							64
						}else{
							22
						}
					}
					sourceSize.height:{
						if (type=="child"){
							64
						}else{
							22
						}
					}
					anchors.left:actionIcon.right
					anchors.verticalCenter:parent.verticalCenter
					anchors.leftMargin:10
					cache:false
				} 

				Text{
					id: pkgName
					text: name
					width: {
						if ((showSpinner) || (resultImg.visible)){
							parent.width-(resultImg.width+actionIcon.width+175)
						}else{
							if (type==="child"){
								parent.width-175
							}else{
								parent.width-75
							}
						}
					}
					elide:Text.ElideMiddle
					clip: true
					font.family: "Quattrocento Sans Bold"
					font.pointSize: 10
					anchors.leftMargin:10
					font.bold:{
						if (type==="parent"){
							true
						}else{
							false
						}
					}
					anchors.left:{
						if (type=="child"){
							packageIcon.right
						}else{
							expandParentIcon.right
						}
					}
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
					anchors.rightMargin:1
					anchors.verticalCenter:parent.verticalCenter
					visible:{
						if (showSpinner){
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
