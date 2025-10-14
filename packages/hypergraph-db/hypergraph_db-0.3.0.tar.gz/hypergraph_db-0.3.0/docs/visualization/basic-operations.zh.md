# 基础操作指南

本指南将带您了解 Hypergraph-DB 可视化界面的基础操作，让您能够有效地浏览和交互超图数据。

## 界面概览

### 主界面布局

可视化界面采用现代化的 Web 设计，主要包含以下区域：

```
┌─────────────────────────────────────────┐
│              标题栏                      │
├─────────────────────────────────────────┤
│  工具栏  │                             │
│         │         画布区域              │
│  控制面板 │                             │
│         │                             │
├─────────────────────────────────────────┤
│              状态栏                      │
└─────────────────────────────────────────┘
```

### 核心组件

#### 1. 画布区域 (Canvas)
- **功能**: 显示超图的可视化内容
- **特点**: 支持缩放、平移、交互
- **操作**: 鼠标拖拽、滚轮缩放

#### 2. 工具栏 (Toolbar)
- **缩放控制**: 放大/缩小/适应屏幕
- **视图选项**: 切换显示模式
- **导出功能**: 保存为图像或数据

#### 3. 控制面板 (Control Panel)
- **图形设置**: 调整节点、边的样式
- **布局选项**: 选择不同的布局算法
- **过滤器**: 隐藏/显示特定元素

#### 4. 状态栏 (Status Bar)
- **统计信息**: 显示超点、超边数量
- **性能指标**: 渲染时间、内存使用
- **当前状态**: 操作提示、错误信息

## 基础交互操作

### 导航操作

#### 🔍 缩放 (Zoom)
- **滚轮缩放**: 鼠标滚轮上下滚动
- **工具栏按钮**: 点击 `+` / `-` 按钮
- **快捷键**: `Ctrl + 滚轮` (更精细控制)
- **双击缩放**: 双击节点快速聚焦

```javascript
// 程序化缩放示例
visualization.zoomTo(1.5);  // 缩放到1.5倍
visualization.zoomFit();    // 适应屏幕
```

#### 🤚 平移 (Pan)
- **鼠标拖拽**: 按住空白区域拖动
- **键盘导航**: 方向键微调位置
- **触摸设备**: 单指拖动

```javascript
// 程序化平移示例
visualization.panTo(100, 100);  // 平移到坐标(100,100)
visualization.center();          // 居中显示
```

### 选择操作

#### 单选
- **点击节点**: 选择单个超点
- **点击边**: 选择单个超边
- **高亮显示**: 选中元素会突出显示

#### 多选
- **Ctrl + 点击**: 添加到选择集合
- **Shift + 点击**: 范围选择
- **框选**: 拖拽选择多个元素

#### 取消选择
- **点击空白**: 清除所有选择
- **Esc 键**: 快速清除选择
- **右键菜单**: 选择"取消选择"

### 查看操作

#### 🔍 详细信息查看
- **悬停提示**: 鼠标悬停显示基础信息
- **右键菜单**: 查看详细属性
- **信息面板**: 在侧边栏显示完整信息

```javascript
// 获取节点信息示例
const nodeInfo = visualization.getNodeInfo(nodeId);
console.log(nodeInfo);
```

#### 📊 统计信息
- **全局统计**: 总体超点、超边数量
- **选择统计**: 当前选择的元素信息
- **性能指标**: 渲染性能和资源使用

## 可视化元素

### 超点 (Hypervertices)

#### 视觉表示
- **形状**: 圆形或多边形节点
- **颜色**: 表示类别或属性
- **大小**: 反映重要性或度数
- **标签**: 显示节点名称或ID

#### 交互功能
- **单击**: 选择节点
- **双击**: 展开/折叠连接
- **右键**: 显示上下文菜单
- **拖拽**: 移动节点位置

### 超边 (Hyperedges)

#### 视觉表示
- **超边可视化**: 使用轮廓或区域表示
- **连接线**: 显示超点之间的关系
- **颜色编码**: 区分不同类型的超边
- **厚度**: 表示权重或重要性

#### 交互功能
- **点击**: 选择超边
- **高亮**: 显示相关联的超点
- **悬停**: 显示超边信息

## 布局算法

### 📍 力引导布局 (Force-Directed)
- **特点**: 动态平衡，自然分布
- **适用**: 中等规模超图
- **参数**: 引力、斥力、阻尼系数

```javascript
visualization.setLayout('force', {
    strength: 0.8,
    distance: 100,
    iterations: 300
});
```

### 🔄 圆形布局 (Circular)
- **特点**: 节点排列在圆周上
- **适用**: 显示层次关系
- **参数**: 半径、起始角度

```javascript
visualization.setLayout('circular', {
    radius: 200,
    startAngle: 0
});
```

### 📊 层次布局 (Hierarchical)
- **特点**: 分层显示
- **适用**: 树状或DAG结构
- **参数**: 层间距、节点间距

```javascript
visualization.setLayout('hierarchical', {
    direction: 'TB',  // 从上到下
    levelSeparation: 50,
    nodeSeparation: 30
});
```

### 🎯 手动布局 (Manual)
- **特点**: 用户自定义位置
- **适用**: 精确控制显示
- **操作**: 拖拽节点到指定位置

## 样式自定义

### 节点样式

#### 基础属性
```javascript
visualization.setNodeStyle({
    size: 10,          // 节点大小
    color: '#3498db',  // 节点颜色
    stroke: '#2c3e50', // 边框颜色
    strokeWidth: 2,    // 边框宽度
    opacity: 0.8       // 透明度
});
```

#### 条件样式
```javascript
visualization.setNodeStyle(node => {
    if (node.degree > 5) {
        return { size: 15, color: '#e74c3c' };
    }
    return { size: 10, color: '#3498db' };
});
```

### 边样式

#### 基础属性
```javascript
visualization.setEdgeStyle({
    width: 2,          // 边宽度
    color: '#95a5a6',  // 边颜色
    opacity: 0.6,      // 透明度
    curvature: 0.3     // 弯曲度
});
```

#### 动态样式
```javascript
visualization.setEdgeStyle(edge => {
    return {
        width: Math.log(edge.weight + 1) * 2,
        color: edge.type === 'strong' ? '#e74c3c' : '#95a5a6'
    };
});
```

## 过滤和搜索

### 🔍 元素过滤

#### 按属性过滤
```javascript
// 隐藏度数小于3的节点
visualization.filterNodes(node => node.degree >= 3);

// 只显示特定类型的超边
visualization.filterEdges(edge => edge.type === 'collaboration');
```

#### 按值范围过滤
```javascript
// 显示权重在指定范围内的边
visualization.filterEdges(edge => 
    edge.weight >= 0.5 && edge.weight <= 1.0
);
```

### 🔎 搜索功能

#### 文本搜索
```javascript
// 搜索节点标签
const results = visualization.searchNodes('research');

// 高亮搜索结果
visualization.highlightNodes(results);
```

#### 高级搜索
```javascript
// 复合条件搜索
const results = visualization.search({
    nodeLabel: { contains: 'lab' },
    degree: { min: 3, max: 10 },
    type: 'researcher'
});
```

## 导出功能

### 📷 图像导出

#### PNG 格式
```javascript
visualization.exportPNG({
    width: 1920,
    height: 1080,
    quality: 0.9,
    background: '#ffffff'
});
```

#### SVG 格式
```javascript
visualization.exportSVG({
    includeStyles: true,
    embedFonts: true
});
```

### 📊 数据导出

#### JSON 格式
```javascript
const data = visualization.exportData('json');
console.log(data);
```

#### CSV 格式
```javascript
visualization.exportData('csv', {
    nodes: true,
    edges: true,
    attributes: ['degree', 'type', 'weight']
});
```

## 性能优化

### 大规模数据处理

#### 级联显示 (LOD - Level of Detail)
```javascript
visualization.enableLOD({
    nodeThreshold: 1000,  // 超过1000个节点时简化显示
    edgeThreshold: 5000,  // 超过5000条边时简化显示
    simplificationLevel: 0.5
});
```

#### 虚拟化渲染
```javascript
visualization.enableVirtualization({
    viewportMargin: 100,  // 视口边距
    updateFrequency: 16   // 更新频率(ms)
});
```

### 渲染优化

#### 帧率控制
```javascript
visualization.setRenderOptions({
    targetFPS: 60,        // 目标帧率
    adaptiveQuality: true, // 自适应质量
    maxNodes: 10000       // 最大节点数
});
```

## 快捷键参考

### 导航快捷键
- `空格 + 拖拽`: 平移视图
- `Ctrl + 滚轮`: 精确缩放
- `Ctrl + 0`: 重置缩放
- `Ctrl + 1`: 适应屏幕

### 选择快捷键
- `Ctrl + A`: 全选
- `Ctrl + D`: 取消选择
- `Ctrl + I`: 反选
- `Delete`: 删除选中元素

### 视图快捷键
- `F`: 适应屏幕
- `H`: 切换隐藏/显示
- `L`: 切换标签显示
- `G`: 切换网格显示

## 故障排除

### 常见问题

#### 性能问题
- **症状**: 渲染缓慢、卡顿
- **解决**: 启用LOD、减少节点数量、关闭动画

#### 显示问题
- **症状**: 元素重叠、布局混乱
- **解决**: 重新应用布局、调整参数、手动调整

#### 交互问题
- **症状**: 点击无响应、选择错误
- **解决**: 检查元素层级、清除缓存、重新加载

### 调试技巧

#### 开发者工具
```javascript
// 启用调试模式
visualization.enableDebug(true);

// 查看性能统计
console.log(visualization.getPerformanceStats());

// 检查元素状态
console.log(visualization.getElementState(elementId));
```

#### 日志记录
```javascript
// 设置日志级别
visualization.setLogLevel('debug');

// 监听事件
visualization.on('error', (error) => {
    console.error('Visualization error:', error);
});
```

## 下一步

现在您已经掌握了基础操作，可以：

1. 📖 查看 [界面指南](interface-guide.zh.md) 了解详细功能
2. 🎨 学习 [高级定制](advanced-customization.zh.md) 技巧
3. 💡 探索 [实际示例](../examples/basic-usage.zh.md)
4. 🔧 了解 [API 参考](../api/index.zh.md)

开始您的超图可视化之旅吧！
