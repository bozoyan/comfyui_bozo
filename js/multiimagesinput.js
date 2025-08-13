import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Bozo_ImagesInput",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Bozo_ImagesInput") {
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
                // 确保在调用原函数前检查是否存在
                if (onConnectionsChange) {
                    return onConnectionsChange.apply(this, arguments);
                }
            };

            // 添加或更新输入时的处理函数
            nodeType.prototype.updateInputs = function() {
                // 不需要实时显示图片预览，只处理逻辑
                // 移除了对undefined value属性的访问
                return; // 什么都不做，避免错误
            };
        }
    }
});