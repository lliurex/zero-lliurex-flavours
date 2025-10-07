import QtQuick
import QtQml.Models

DelegateModel {
	id:filterModel
	property string role
	property string search
	property string statusFilter
	onRoleChanged:Qt.callLater(update)
	onSearchChanged:Qt.callLater(update)
	onStatusFilterChanged:Qt.callLater(update)
	property var visibleElements:[]
	
	groups: [
		DelegateModelGroup{
			id:allItems
			name:"all"
			includeByDefault:true
			onCountChanged:Qt.callLater(update)
		},
		DelegateModelGroup{
			id:visibleItems
			name:"visible"
		}
	]

	filterOnGroup:"visible"

	function update(){
		visibleElements=[]
		if (allItems.count>0){
			allItems.setGroups(0,allItems.count,[ "all"]);
			for (let index = 0; index < allItems.count; index++) {
				let item = allItems.get(index).model;
				if (item["type"]=="parent"){
					let visibleParentChild=false
					let visibleParent=item[role].toLowerCase().includes(search.toLowerCase());
					let matchStatusParent=false
					for (let indexChild=0;indexChild<allItems.count;indexChild++){
						let itemChild=allItems.get(indexChild).model;
						let matchStatus=true
						if ((itemChild["type"]=="child") && (itemChild["flavourParent"]==item["pkg"])){
							let visible = itemChild[role].toLowerCase().includes(search.toLowerCase());
							if (visible){
								visibleParent=true
							}else{
								if (visibleParent){
									visible=true
								}
							}
							if (statusFilter!="all"){
		            			switch(statusFilter){
		            				case "available":
		            					if (itemChild["status"]=="installed"){
		            						matchStatus=false
				            			}else{
				            				matchStatusParent=true
				            			}
				            			break;
				            		case "installed":
				            			if (itemChild["status"]=="available"){
				            				matchStatus=false
				            			}else{
				            				matchStatusParent=true
				            			}
				            			break;
				            		case "error":
				            			if (itemChild["resultProcess"]!=1){
				            				matchStatus=false
				            			}else{
				            				matchStatusParent=true
				            			}
				            		break
				       			}

				    		}else{
				    			matchStatusParent=true
				    		}

				    		if (!visible) continue;
	            			if (!itemChild["isVisible"] || !matchStatus) continue;
	           				allItems.setGroups(indexChild, 1, [ "all", "visible" ]);
	           				visibleElements.push(indexChild);
						}
					}
					if (!visibleParent && !visibleParentChild) continue;
	            	if (!matchStatusParent) continue;
	            	allItems.setGroups(index, 1, [ "all", "visible" ]);
	            	visibleElements.push(index);

	            }
	        }
    	}

	}
	Component.onCompleted: Qt.callLater(update)

}
