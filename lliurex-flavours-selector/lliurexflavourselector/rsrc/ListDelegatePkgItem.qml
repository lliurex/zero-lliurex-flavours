import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as PC


PC.ItemDelegate{
	    id: listPkgItem
	    property string pkg
	    property bool isChecked
	    property string name
	    property string banner
	    property string status
	    property bool isVisible
	    property int resultProcess
	    property bool showSpinner
	    property bool isManaged

	    height:85
	    enabled:true
	      
	    Item{
		id: menuItem
		height:visible?80:0
		width:parent.width-25
		
		MouseArea {
			id: mouseAreaOption
			anchors.fill: parent
			hoverEnabled:true
			propagateComposedEvents:true
			
			onEntered: {
				listPkg.currentIndex=filterModel.visibleElements.indexOf(index)
			}
		} 

		PC.CheckBox {
			id:packageCheck
			checked:isChecked
			onToggled:{
				flavourStackBridge.onCheckedFlavour([pkg,checked])
			}
			anchors.left:parent.left
			anchors.leftMargin:10
			anchors.verticalCenter:parent.verticalCenter
			visible:isManaged
			enabled:flavourStackBridge.enableFlavourList
		}

		Image {
			id:packageIcon
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
