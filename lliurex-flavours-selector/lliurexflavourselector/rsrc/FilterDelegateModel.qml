import QtQuick
import QtQml.Models

DelegateModel {
    id: filterModel
    property var externalTimer: null
    property string role
    property string search
    property string statusFilter
    property var visibleElements: []

    onRoleChanged: if (externalTimer) externalTimer.restart()
    onSearchChanged: if (externalTimer) externalTimer.restart()
    onStatusFilterChanged: if (externalTimer) externalTimer.restart()

    groups: [
        DelegateModelGroup {
            id: allItems
            name: "all"
            includeByDefault: true
            onCountChanged: if (externalTimer) externalTimer.restart()
        },
        DelegateModelGroup {
            id: visibleItems
            name: "visible"
        }
    ]

    filterOnGroup: "visible"

    function update() {
        visibleElements = [];
        let total = allItems.count;
        if (total === 0 || !role) return;

        allItems.setGroups(0, total, ["all"]);

        let searchLower = search.toLowerCase();
        let visibleIndices = [];
        let parentMap = {};
        let childrenToProcess = [];

        for (let i = 0; i < total; i++) {
            let item = allItems.get(i).model;
            if (!item) continue;

            if (item["type"] === "parent") {
                let visibleParent = item[role].toString().toLowerCase().includes(searchLower);
                parentMap[item["pkg"]] = {
                    index: i,
                    visibleParent: visibleParent,
                    matchStatusParent: (statusFilter === "all"),
                    hasVisibleChild: false
                };
            } else if (item["type"] === "child") {
                childrenToProcess.push({ index: i, item: item });
            }
        }

        let totalChildren = childrenToProcess.length;
        for (let i = 0; i < totalChildren; i++) {
            let childData = childrenToProcess[i];
            let itemChild = childData.item;
            let indexChild = childData.index;

            let parentData = parentMap[itemChild["flavourParent"]];
            if (!parentData) continue;

            let matchStatus = true;
            if (statusFilter !== "all") {
                switch (statusFilter) {
                    case "available":
                        matchStatus = (itemChild["status"] !== "installed");
                        break;
                    case "installed":
                        matchStatus = (itemChild["status"] !== "available");
                        break;
                    case "error":
                        matchStatus = (itemChild["resultProcess"] === 1 || itemChild["resultProcess"] === "1");
                        break;
                }
            }

            if (matchStatus) {
                parentData.matchStatusParent = true;

                let visibleChild = itemChild[role].toString().toLowerCase().includes(searchLower);
                if (visibleChild || parentData.visibleParent) {
                    if (itemChild["isVisible"] !== false && itemChild["isVisible"] !== "false") {
                        parentData.hasVisibleChild = true;
                        visibleIndices.push(indexChild);
                    }
                }
            }
        }

        let parentKeys = Object.keys(parentMap);
        for (let i = 0; i < parentKeys.length; i++) {
            let parentData = parentMap[parentKeys[i]];
            if (parentData.matchStatusParent && (parentData.visibleParent || parentData.hasVisibleChild)) {
                visibleIndices.push(parentData.index);
            }
        }

        visibleIndices.sort((a, b) => a - b);
        for (let i = 0; i < visibleIndices.length; i++) {
            allItems.setGroups(visibleIndices[i], 1, ["all", "visible"]);
        }

        visibleElements = visibleIndices;
    }

    Component.onCompleted: if (externalTimer) externalTimer.restart()
}
