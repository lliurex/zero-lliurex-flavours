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
	    	if (type=="parent"){
	    		if (isVisible){
	    			30
	    		}else{
	    			0
	    		}
	    	}else{
	    		if (isExpanded){
	    			if (isVisible){
	    				50
	    			}else{
	    				0
	    			}
	    		}else{
	    			0
	    		}
	    	}
	    }
	    enabled:true
	      
	    Rectangle{
	    	id:containerParent
	    	height:{
	    		if (type=="parent"){
	    			if (isVisible){
	    				28
	    			}else{
	    				0
	    			}
	    		}else{
	    			if (isExpanded){
	    				if (isVisible){
	    					48
	    				}else{
	    					0
	    				}
	    			}else{
	    				0
	    			}
	    		}
	    	}
	    	width:parent.width-20
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
	    	visible:{
	    		if (type=="parent"){
	    			isVisible
	    		}else{
	    			if (isExpanded){
	    				isVisible
	    			}else{
	    				false
	    			}
	    		}
	    	}
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
		    		if (type=="parent"){
		    			if (isVisible){
		    				28
		    			}else{
		    				0
		    			}
		    		}else{
		    			if (isExpanded){
		    				if (isVisible){
		    					48
		    				}else{
		    					0
		    				}
		    			}else{
		    				0
		    			}
		    		}
				}

				width:containerParent.width-25
				Rectangle{
					id:expandedContainer
					width:26
					height:26
					visible:{
	                	if (type==="parent"){
	                		true
	                	}else{
	                		false
	                	}
	                }
					anchors.verticalCenter:menuItem.verticalCenter
					anchors.left:menuItem.left
					anchors.leftMargin:10
					border.color:"transparent"
					radius:5.0
					color:"transparent"
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
	                	anchors.centerIn:expandedContainer
	                	enabled:true
	               		MouseArea{
	                    	function expand(isExpanded,pkg) {
	                        	for(var i = 0; i < flavourStackBridge.totalElements; ++i) {
	                            	var item=flavourStackBridge.getModelData(i)
	                              	if (item["pkg"]===pkg){
	                                	flavourStackBridge.onExpandedParent([pkg,"isExpanded",isExpanded])
	                            	}else{
	                            		if (item["flavourParent"]===pkg){
	                            			flavourStackBridge.onExpandedParent([item["pkg"],"isExpanded",isExpanded])
	                            		}
	                            	}
	                            	
	                       		}
	                    	}	 
	                    	anchors.fill:parent
	                    	hoverEnabled:true
	                    	
	                    	onEntered:{
	                    		expandedContainer.border.color="#308cc6"
	                    		expandedContainer.color="#d5eaf2"
	                    	}
	                    	onExited:{
	                    		expandedContainer.border.color="transparent"
	                    		expandedContainer.color="#add8e6"
	                    	}
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
					anchors.left:expandedContainer.right
					anchors.leftMargin:10
					anchors.verticalCenter:menuItem.verticalCenter
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
                	anchors.verticalCenter:menuItem.verticalCenter
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
					source:banner
					sourceSize.width:{
						if (type=="child"){
							54
						}else{
							22
						}
					}
					sourceSize.height:{
						if (type=="child"){
							36
						}else{
							22
						}
					}
					anchors.left:actionIcon.right
					anchors.verticalCenter:menuItem.verticalCenter
					anchors.leftMargin:10
					cache:false
				} 

				Text{
					id: pkgName
					text: name
					width: {
						if ((showSpinner) || (resultImg.visible)){
							menuItem.width-(resultImg.width+actionIcon.width+175)
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
							expandedContainer.right
						}
					}
					anchors.verticalCenter:menuItem.verticalCenter
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
					anchors.right:menuItem.right
					anchors.verticalCenter:menuItem.verticalCenter
				}
				Rectangle{
					id:animationFrame
					color:"transparent"
					width:0.4*(animation.width)
					height:0.4*(animation.height)
					anchors.leftMargin:10
					anchors.right:menuItem.right
					anchors.rightMargin:1
					anchors.verticalCenter:menuItem.verticalCenter
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
