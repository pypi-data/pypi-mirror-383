# 可视化概述

Hypergraph-DB 提供强大的交互式可视化功能，帮助您直观地探索和理解复杂的超图结构。

## 🎯 核心特性

### 交互式可视化
- **拖拽操作**: 移动顶点和超边以获得更好的布局
- **缩放和平移**: 探索大型超图的不同部分
- **悬停信息**: 查看顶点和超边的详细属性
- **选择高亮**: 点击元素查看相关连接

### Web 技术栈
- **D3.js**: 强大的数据可视化库
- **HTML5 Canvas**: 高性能渲染
- **响应式设计**: 适配不同屏幕尺寸
- **本地服务器**: 无需外部依赖

## 🚀 快速开始

### 基本可视化

```python
from hyperdb import HypergraphDB

# 创建示例超图
hg = HypergraphDB()

# 添加社交网络数据
hg.add_v("Alice", {"age": 30, "职业": "工程师"})
hg.add_v("Bob", {"age": 25, "职业": "设计师"})
hg.add_v("Charlie", {"age": 35, "职业": "产品经理"})

# 添加关系
hg.add_e(("Alice", "Bob"), {"关系": "朋友", "亲密度": 0.8})
hg.add_e(("Alice", "Bob", "Charlie"), {"关系": "项目团队", "项目": "移动应用"})

# 启动可视化
hg.draw()
```

### 自定义端口和设置

```python
# 指定端口
hg.draw(port=9000)

# 不自动打开浏览器
hg.draw(open_browser=False)
print("请手动访问 http://localhost:8080")
```

## 📊 可视化元素

### 顶点表示
- **圆形节点**: 表示超图中的顶点
- **颜色编码**: 根据属性类型自动着色
- **大小变化**: 反映顶点的重要性（度数）
- **标签显示**: 显示顶点的名称或标识符

### 超边表示
- **连接线**: 显示顶点之间的关系
- **超边包络**: 用于多顶点超边的可视化
- **权重表示**: 线条粗细反映关系强度
- **类型区分**: 不同类型的关系使用不同样式

### 布局算法
- **力导向布局**: 自动排列顶点以减少重叠
- **层次布局**: 适用于有向或分层的超图
- **手动调整**: 拖拽顶点到期望位置

## 🎨 可视化样式

### 默认主题
```javascript
// 顶点样式
vertex: {
    radius: 8,
    fill: "#6366f1",
    stroke: "#4f46e5",
    strokeWidth: 2
}

// 超边样式
edge: {
    stroke: "#9ca3af",
    strokeWidth: 1.5,
    opacity: 0.7
}
```

### 自定义颜色方案
可视化支持基于数据属性的动态着色：

- **类别着色**: 根据顶点或超边的类型
- **数值着色**: 基于连续数值的渐变色
- **自定义调色板**: 为特定应用定制颜色

## 🔍 交互功能

### 鼠标操作
| 操作 | 功能 |
|------|------|
| 左键点击 | 选择顶点或超边 |
| 拖拽 | 移动顶点位置 |
| 滚轮 | 缩放视图 |
| 右键拖拽 | 平移视图 |
| 悬停 | 显示详细信息 |

### 键盘快捷键
| 按键 | 功能 |
|------|------|
| `R` | 重置视图到原始位置 |
| `F` | 适应视图到所有元素 |
| `+/-` | 缩放视图 |
| `Ctrl+A` | 选择所有元素 |
| `Delete` | 删除选中元素（如果启用编辑） |

## 📱 响应式设计

### 桌面端
- **全屏显示**: 充分利用大屏幕空间
- **侧边栏**: 显示详细的属性面板
- **工具栏**: 提供快速操作按钮

### 移动端
- **触摸友好**: 支持触摸手势操作
- **自适应布局**: 调整界面以适合小屏幕
- **简化控件**: 优化移动设备的用户体验

## 🎯 使用场景

### 学术研究
```python
# 研究合作网络可视化
academic_hg = HypergraphDB()

# 添加研究人员和论文合作关系
academic_hg.add_v("张教授", {"领域": "AI", "机构": "清华"})
academic_hg.add_v("李博士", {"领域": "ML", "机构": "北大"})

# 合作论文作为超边
academic_hg.add_e(("张教授", "李博士"), {
    "论文": "深度学习综述", 
    "年份": 2024,
    "期刊": "Nature AI"
})

academic_hg.draw()
```

### 社交网络分析
```python
# 群体社交关系
social_hg = HypergraphDB()

# 朋友群体
social_hg.add_e(("Alice", "Bob", "Charlie"), {
    "群体": "大学同学",
    "活动": "定期聚会"
})

social_hg.draw()
```

### 生物网络
```python
# 蛋白质相互作用网络
bio_hg = HypergraphDB()

# 蛋白质复合体
bio_hg.add_e(("ProteinA", "ProteinB", "ProteinC"), {
    "复合体": "转录因子",
    "功能": "基因调控"
})

bio_hg.draw()
```

## 🔧 高级配置

### 自定义 HTML 模板
您可以修改 `hyperdb/templates/hypergraph_viewer.html` 来：

- 添加自定义 CSS 样式
- 集成额外的 JavaScript 库
- 修改布局和界面元素
- 添加自定义分析工具

### 数据导出
可视化支持多种数据导出格式：

```python
# 导出当前视图（计划中的功能）
hg.export_view("network.png", format="png")
hg.export_view("network.svg", format="svg")
hg.export_data("network.json", format="json")
```

## 📈 性能优化

### 大型数据集处理
对于包含大量顶点和超边的超图：

1. **数据采样**: 只可视化数据的子集
2. **层次显示**: 逐级展开详细信息
3. **按需加载**: 根据用户交互动态加载数据
4. **性能监控**: 监控渲染性能并优化

### 渲染优化
```python
# 对于大型超图，考虑数据过滤
large_hg = HypergraphDB()
# ... 添加大量数据 ...

# 只可视化高度数顶点
important_vertices = [v for v in large_hg.all_v 
                     if large_hg.degree_v(v) > 5]

# 创建子图进行可视化
sub_hg = HypergraphDB()
for v in important_vertices:
    sub_hg.add_v(v, large_hg.v(v))
    for e in large_hg.nbr_e_of_v(v):
        sub_hg.add_e(e, large_hg.e(e))

sub_hg.draw()
```

## 下一步

- **[基础操作](basic-operations.zh.md)**: 学习可视化的基本交互
- **[界面指南](interface-guide.zh.md)**: 了解用户界面的各个部分
- **[高级定制](advanced-customization.zh.md)**: 个性化您的可视化体验

通过这些强大的可视化功能，您可以直观地理解和分析复杂的超图结构！🎨
