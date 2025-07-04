import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";


app.registerExtension({
  name: "Comfy.Bozo.PreviewText",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    // StylesCSVLoader 节点
    if (
      nodeData.name === "StylesCSVLoader" ||
      nodeData.title === "StylesCSVLoader" ||
      nodeData.display_name === "StylesCSVLoader"
    ) {
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
        // 只插入一次，并用 advanced: true 放到底部
        if (!this.widgets.some(w => w.name === "样式内容预览")) {
          const widget = ComfyWidgets.STRING(
            this,
            "样式内容预览",
            ["STRING", { multiline: true, advanced: true }],
            app
          );
          widget.widget.inputEl.readOnly = true;
          widget.widget.inputEl.style.color = "rgba(255,255,255,0.95)";
          widget.widget.inputEl.style.fontSize = "15px";
          widget.widget.inputEl.style.padding = "8px";
          widget.widget.inputEl.style.lineHeight = "1.5";
          widget.widget.inputEl.style.fontFamily = "monospace";
          widget.widget.inputEl.style.background = "rgba(0,0,0,0.15)";
          widget.widget.inputEl.style.border = "1px solid #444";
          widget.widget.inputEl.style.marginBottom = "8px";
          widget.value = "请选择样式...";
        }
        const stylesWidget = this.widgets.find(w => w.name === "styles");
        const stylesInfoWidget = this.widgets.find(w => w.name === "_styles_info");
        let stylesInfo = {};
        try {
          stylesInfo = stylesInfoWidget ? JSON.parse(stylesInfoWidget.value) : {};
        } catch {}
        if (stylesWidget) {
          stylesWidget.callback = (value) => {
            const info = stylesInfo[value] || ["", "", ""];
            const pos = info[0] || "";
            const remark = info[2] || "";
            const previewWidget = this.widgets.find(w => w.name === "样式内容预览");
            if (previewWidget) {
              previewWidget.value =
                "正向提示词：\n" +
                (pos || "无") +
                "\n\n备注：\n" +
                (remark || "无");
            }
            app.graph.setDirtyCanvas(true, false);
          };
          if (stylesWidget.value) {
            stylesWidget.callback(stylesWidget.value);
          }
        }
        // 隐藏 _styles_info 输入框
        setTimeout(() => {
          const nodeEl = this?.el || this?.canvas?.getNodeDOM(this);
          if (nodeEl) {
            nodeEl.querySelectorAll('div.widget').forEach(div => {
              if (
                div.textContent &&
                div.textContent.includes('_styles_info')
              ) {
                div.style.display = 'none';
              }
            });
          }
        }, 100);
        return r;
      };
      // 执行后刷新内容
      const onExecuted = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (message) {
        onExecuted?.apply(this, arguments);
        const pos = message?.outputs?.[0] ?? "";
        const remark = message?.outputs?.[2] ?? "";
        const widget = this.widgets.find((w) => w.name === "样式内容预览");
        if (widget) {
          widget.value =
            "正向提示词：\n" +
            (pos || "无") +
            "\n\n备注：\n" +
            (remark || "无");
        }
        requestAnimationFrame(() => {
          const sz = this.computeSize();
          if (sz[0] < this.size[0]) sz[0] = this.size[0];
          if (sz[1] < this.size[1]) sz[1] = this.size[1];
          this.onResize?.(sz);
          app.graph.setDirtyCanvas(true, false);
        });
      };
    }
    // Bozo_preview_text 节点（增强显示及时性）
    if (nodeData.name === "Bozo_preview_text") {
      // Add custom widget
      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

        // Add a text widget for preview
        const widget = ComfyWidgets.STRING(this, "display_text", ["STRING", { multiline: true }], app);
        widget.widget.inputEl.readOnly = true;
        widget.widget.inputEl.style.color = "rgba(255, 255, 255, 0.9)";  // 90% white
        widget.widget.inputEl.style.fontSize = "16px";
        widget.widget.inputEl.style.padding = "8px";
        widget.widget.inputEl.style.lineHeight = "1.4";
        widget.widget.inputEl.style.fontFamily = "monospace";

        return r;
      };

      // Handle node execution
      const onExecuted = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (message) {
        onExecuted?.apply(this, arguments);
        const text = message.text;
        
        if (Array.isArray(text)) {
          // Find the display widget
          const widget = this.widgets.find((w) => w.name === "display_text");
          if (widget) {
            widget.value = text.join("\n");
          }
        }

        // Resize node
        requestAnimationFrame(() => {
          const sz = this.computeSize();
          if (sz[0] < this.size[0]) sz[0] = this.size[0];
          if (sz[1] < this.size[1]) sz[1] = this.size[1];
          this.onResize?.(sz);
          app.graph.setDirtyCanvas(true, false);
        });
      };
    }
    
  },
});