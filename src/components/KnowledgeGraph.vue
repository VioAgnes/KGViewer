<template>
  <div class="knowledge-graph-container">
    <div class="graph-wrapper">
      <RelationGraph 
        ref="relationGraph$" 
        :options="options" 
        :on-node-click="onNodeClick" 
        :on-line-click="onLineClick"
        @node-expand="onNodeExpand"
        @node-collapse="onNodeCollapse"
      >
        <template #graph-plug>
          <div class="menu-toggle" @click="toggleMenu">
            <el-icon :size="20" :color="showMenu ? '#ffffff' : '#ffffff'">
              <component :is="showMenu ? 'ArrowRight' : 'ArrowLeft'" />
            </el-icon>
          </div>
          <!-- 控制面板 -->
          <div class="control-panel" :class="{ 'menu-hidden': !showMenu }">
            <!-- 布局切换 -->
            <div class="panel-section layout-section">
              <div class="section-title">布局切换</div>
              <div class="layout-buttons">
                <el-button 
                  v-for="layout in layouts"
                  :key="layout.layoutName"
                  size="small" 
                  :type="currentLayout === layout.layoutName ? 'primary' : 'default'" 
                  @click="switchLayout(layout.layoutName)"
                >
                  {{layout.label}}
                </el-button>
              </div>
            </div>

            <!-- 节点搜索 -->
            <div class="panel-section search-section">
              <div class="section-title">节点搜索</div>
              <div class="search-area">
                <el-select
                  v-model="searchText"
                  size="small"
                  filterable
                  remote
                  reserve-keyword
                  placeholder="输入节点名称或ID搜索"
                  @change="handleNodeSearch"
                  class="search-select"
                >
                  <el-option
                    v-for="item in searchOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
                <el-checkbox
                  v-model="onlyRelated"
                  class="only-related-checkbox"
                  @change="() => { if (searchText) handleNodeSearch(searchText) }"
                >仅相关</el-checkbox>
              </div>
              <!-- 新增：快速定位标签 -->
              <div class="quick-tags" style="margin-top: 10px; display: flex; gap: 10px;">
                <el-tag
                  size="small"
                  style="cursor: pointer;"
                  @click="searchByNodeText('认知域')"
                >认知域</el-tag>
                <el-tag
                  size="small"
                  style="cursor: pointer;"
                  @click="searchByNodeText('美国主流智库')"
                >美国主流智库</el-tag>
                <el-tag
                  size="small"
                  style="cursor: pointer;"
                  @click="searchByNodeText('俄罗斯')"
                >俄罗斯</el-tag>
                <el-tag
                  size="small"
                  style="cursor: pointer;"
                  @click="searchByNodeText('印度')"
                >印度</el-tag>
              </div>
            </div>

            <!-- 节点筛选 -->
            <div class="panel-section filter-section">
              <div class="section-title">节点筛选</div>
              <el-checkbox-group v-model="node_checkList" @change="doFilter" class="filter-group">
                <el-checkbox v-for="item in all_node_labels" :key="item" :label="item" />
              </el-checkbox-group>
            </div>

            <!-- 关系筛选 -->
            <div class="panel-section filter-section">
              <div class="section-title">关系筛选</div>
              <el-checkbox-group v-model="rel_checkList" @change="doFilter" class="filter-group">
                <el-checkbox v-for="item in all_rel_type" :key="item" :label="item" />
              </el-checkbox-group>
            </div>
          </div>
        </template>
      </RelationGraph>
    </div>
    
    <!-- 右侧详情面板 -->
    <div class="node-detail-panel" :class="{ 'panel-show': showNodeDetail }" :style="panelStyle">
      <div class="panel-header">
        <div class="header-title">{{ isPanelForNode ? '节点详情' : '关系详情' }}</div>
        <el-icon class="close-icon" @click="closeNodeDetail">
          <Close />
        </el-icon>
      </div>
      <!-- 节点详情内容 -->
      <div v-if="selectedNode && isPanelForNode" class="panel-content">
        <div class="detail-item">
          <span class="item-label">节点名称:</span>
          <span class="item-value">{{ selectedNode.text }}</span>
        </div>
        <div v-if="selectedNode.data?.labels" class="detail-item">
          <span class="item-label">节点类型:</span>
          <span class="item-value">
            <el-tag v-for="label in selectedNode.data.labels" 
                   :key="label" 
                   size="small">
              {{ label }}
            </el-tag>
          </span>
        </div>
        <div v-if="selectedNode.data?.description" class="detail-item">
          <span class="item-label">描述:</span>
          <span class="item-value">{{ selectedNode.data.description }}</span>
        </div>
      </div>
      
      <!-- 关系详情内容 -->
      <div v-if="selectedRelation && !isPanelForNode" class="panel-content">
        <div class="detail-item">
          <span class="item-label">关系类型:</span>
          <span class="item-value">{{ selectedRelation.data?.type }}</span>
        </div>
        <div class="detail-item">
          <span class="item-label">源节点:</span>
          <span class="item-value">{{ selectedRelation.sourceNodeText }}</span>
        </div>
        <div class="detail-item">
          <span class="item-label">目标节点:</span>
          <span class="item-value">{{ selectedRelation.targetNodeText }}</span>
        </div>
        <div v-if="selectedRelation.data?.description" class="detail-item">
          <span class="item-label">描述:</span>
          <span class="item-value">{{ selectedRelation.data.description }}</span>
        </div>
      </div>
      
      <div v-if="!selectedNode && !selectedRelation" class="empty-content">
        请点击节点或关系查看详细信息
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, onBeforeUnmount, watch } from 'vue'
import RelationGraph, { 
  RGJsonData, 
  RGNode, 
  RGUserEvent, 
  RGLineShape, 
  RGJunctionPoint,
  RelationGraphComponent,
  RGNodeShape,
  RGLine,
  RGLink
} from 'relation-graph/vue3'
import { ElRadioGroup, ElRadioButton, ElCheckboxGroup, ElCheckbox, ElSelect, ElOption, ElIcon } from 'element-plus'
import { ArrowLeft, ArrowRight, Close } from '@element-plus/icons-vue'
import demoData from '../assets/converted_data.json'

// 类型定义
interface TooltipPosition {
  x: number
  y: number
}

interface ExtendedLayout {
  label: string
  layoutName: string
  from: string
  layoutClassName: string
  defaultExpandHolderPosition: string
  defaultJunctionPoint: string
  nodeSize: number
  // 可选属性
  levelDistance?: number
  horizontalGap?: number
  verticalGap?: number
  distance?: number
  radius?: number
  angleInterval?: number
  multiTreeGap?: number
  multiTreeDirection?: 'vertical' | 'horizontal'
  allowMultipleRoot?: boolean
  fromMultipleRoots?: boolean
  rootIds?: string[]
  // 力导向布局特有属性
  nodeStrength?: number
  edgeStrength?: number
  collideStrength?: number
  alphaDecay?: number
  velocityDecay?: number
  linkDistance?: number
  gravity?: number
  preventOverlap?: boolean
  clustering?: boolean
}

interface ExtendedRGLink extends RGLink {
  data?: {
    type?: string
    description?: string
    source?: string
    target?: string
  }
  sourceNodeText?: string
  targetNodeText?: string
  color?: string
  fromText?: string
  toText?: string
}

// 响应式状态
const relationGraph$ = ref<RelationGraphComponent>()
const searchText = ref('')
const rel_checkList = ref<string[]>([])
const all_rel_type = ref<string[]>([])
const all_node_labels = ref<string[]>([])
const node_checkList = ref<string[]>([])

// 新增：可见数据，初始化为 demoData 的深拷贝
const visibleData = ref(JSON.parse(JSON.stringify(demoData)))


const searchOptions = computed(() => {
  return demoData.nodes.map((node: any) => ({
    value: node.id,
    label: `${node.text} (${node.id})`
  }))
})

// 布局配置
const layouts: ExtendedLayout[] = [
  {
    label: '中心布局',
    layoutName: 'center',
    from: 'left',
    layoutClassName: 'seeks-layout-center',
    defaultExpandHolderPosition: 'hide',
    defaultJunctionPoint: 'border',
    distance: 220,
    nodeSize: 90,
    levelDistance: 180,
  },
  {
    label: '树形布局',
    layoutName: 'tree',
    from: 'left',
    layoutClassName: 'seeks-layout-center',
    defaultExpandHolderPosition: 'hide',
    defaultJunctionPoint: 'border',
    levelDistance: 150,
    nodeSize: 100,
    horizontalGap: 150,
    verticalGap: 100,
    multiTreeGap: 200,
    multiTreeDirection: 'vertical',
    allowMultipleRoot: true,
    fromMultipleRoots: true
  },
  {
    label: '环形布局',
    layoutName: 'circle',
    from: 'left',
    layoutClassName: 'seeks-layout-center',
    defaultExpandHolderPosition: 'hide',
    defaultJunctionPoint: 'border',
    radius: 500,
    nodeSize: 100,
    angleInterval: 30,
  },
  {
    label: '力导向布局',
    layoutName: 'force',
    from: 'left',
    layoutClassName: 'seeks-layout-center',
    defaultExpandHolderPosition: 'hide',
    defaultJunctionPoint: 'border',
    nodeStrength: -1500,
    edgeStrength: 0.8,
    nodeSize: 120,
    collideStrength: 1,
    alphaDecay: 0.05,
    velocityDecay: 0.2,
    linkDistance: 200,
    gravity: 0.1,
    preventOverlap: true,
    clustering: true,
  }
]

// 图表配置
const options = {
  defaultExpandHolderPosition: 'right' as const,
  showExpandHolder: true,
  debug: false,
  showDebugPanel: false,
  defaultNodeBorderWidth: 0,
  defaultNodeColor: 'transparent',
  defaultNodeShape: 0 as RGNodeShape,
  allowSwitchLineShape: true,
  allowSwitchJunctionPoint: true,
  defaultLineShape: 1 as RGLineShape,
  moveToCenterWhenRefresh: true,
  zoomToFitWhenRefresh: true,
  useAnimationWhenRefresh: true,
  defaultFocusRootNode: false,
  allowShowZoomMenu: true,
  placeSingleNode: true,
  placeOtherGroup: true,
  layouts,
  defaultJunctionPoint: 'border' as RGJunctionPoint
}

// 状态控制
const currentLayout = ref('center')
const showMenu = ref(true)

// 添加节点详情相关的响应式状态
const showNodeDetail = ref(false)
const selectedNode = ref<RGNode | null>(null)
const isPanelForNode = ref(true)

// 添加关系详情相关的响应式状态
const selectedRelation = ref<ExtendedRGLink | null>(null)

// 添加面板样式计算属性
const panelStyle = computed(() => {
  if (!showNodeDetail.value) return {}
  
  const backgroundColor = isPanelForNode.value 
    ? selectedNode.value?.color || '#ffffff'
    : selectedRelation.value?.color || '#666666'
    
  return {
    backgroundColor: `${backgroundColor}15`, // 降低透明度到15%
    borderLeft: `4px solid ${backgroundColor}`,
    boxShadow: `inset 0 0 30px ${backgroundColor}10` // 添加内阴影效果
  }
})

// 新增：仅相关勾选框
const onlyRelated = ref(true)
let lastSearchedId: string | null = null // 记录上次搜索的节点id

// 事件处理函数
const onNodeClick = (node: RGNode, e: RGUserEvent) => {
  console.log('onNodeClick:', node.id)
  hideAllPanel()
  
  // 设置选中节点
  selectedNode.value = {
    ...node,
    data: {
      ...node.data,
      // 确保所有可能的属性都被正确处理
      labels: node.data?.labels || [],
      sexType: node.data?.sexType || '',
      isGoodMan: node.data?.isGoodMan,
      description: node.data?.description || '',
      properties: node.data?.properties || {}
    }
  }
  isPanelForNode.value = true
  showNodeDetail.value = true
  
  return true
}


const handleNodeSearch = async (nodeId: string) => {
  lastSearchedId = nodeId
  if (!onlyRelated.value) {
    // 未勾选，仅相关，恢复全量数据
    visibleData.value = JSON.parse(JSON.stringify(demoData))
    relationGraph$.value?.setJsonData(visibleData.value, async () => {
      const graphInstance = relationGraph$.value?.getInstance()
      if (!graphInstance) return
      graphInstance.options.useAnimationWhenRefresh = false
      await graphInstance.zoomToFit()
      graphInstance.options.useAnimationWhenRefresh = true
      graphInstance.focusNodeById(nodeId)
    })
    return
  }
  // 勾选，仅相关，筛选相关节点和关系
  const subGraph = getRelatedSubGraph(nodeId, 100)
  visibleData.value = subGraph
  relationGraph$.value?.setJsonData(visibleData.value, async () => {
    const graphInstance = relationGraph$.value?.getInstance()
    if (!graphInstance) return
    graphInstance.options.useAnimationWhenRefresh = false
    await graphInstance.zoomToFit()
    graphInstance.options.useAnimationWhenRefresh = true
    graphInstance.focusNodeById(nodeId)
  })
}

// 新增：根据节点文本查找节点ID并执行搜索
const searchByNodeText = (nodeText: string) => {
  const node = demoData.nodes.find((n: any) => n.text === nodeText)
  if (node) {
    searchText.value = node.id
    handleNodeSearch(node.id)
  }
}

// 新增：获取相关子图（BFS，最多100个节点）
function getRelatedSubGraph(rootId: string, maxNodes = 100) {
  const nodesMap = new Map(demoData.nodes.map((n: any) => [n.id, n]))
  const links = demoData.lines
  const visited = new Set<string>()
  const queue: string[] = [rootId]
  const resultNodes: any[] = []
  let idx = 0
  while (queue.length && resultNodes.length < maxNodes) {
    const nid = queue.shift()!
    if (visited.has(nid)) continue
    visited.add(nid)
    const node = nodesMap.get(nid)
    if (node) {
      resultNodes.push(node)
      // 找到与该节点直接相连的节点
      links.forEach((l: any) => {
        if (l.from === nid && !visited.has(l.to)) queue.push(l.to)
        if (l.to === nid && !visited.has(l.from)) queue.push(l.from)
      })
    }
    idx++
    if (idx > maxNodes * 2) break // 防止死循环
  }
  // 只保留相关节点id
  const nodeIds = new Set(resultNodes.map(n => n.id))
  // 只保留相关的关系
  const resultLinks = links.filter((l: any) => nodeIds.has(l.from) && nodeIds.has(l.to))
  // 返回子图数据
  return {
    nodes: resultNodes,
    lines: resultLinks,
    rootId: rootId
  }
}

const doFilter = () => {
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return

  const _all_nodes = graphInstance.getNodes()
  const _all_links = graphInstance.getLinks()

  // 节点标签过滤
  _all_nodes.forEach(thisNode => {
    let _isHideThisNode = false
    if (node_checkList.value.length > 0) {
      const nodeLabels = thisNode.data?.labels || []
      _isHideThisNode = !nodeLabels.some(label => node_checkList.value.includes(label))
    }
    thisNode.opacity = _isHideThisNode ? 0.1 : 1
  })

  // 关系过滤
  _all_links.forEach(thisLink => {
    thisLink.relations.forEach(thisLine => {
      const shouldHide = rel_checkList.value.indexOf(thisLine.data?.['type']) === -1
      thisLine.isHide = shouldHide
    })
  })

  graphInstance.dataUpdated()
}

const hideAllPanel = () => {
}

const switchLayout = async (layoutName: string) => {
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return
  
  currentLayout.value = layoutName
  const targetLayout = {...layouts.find(layout => layout.layoutName === layoutName)} as ExtendedLayout
  if (targetLayout) {
    graphInstance.options.useAnimationWhenRefresh = false
    
    // 如果是树形布局，先找出所有根节点
    if (layoutName === 'tree') {
      const nodes = graphInstance.getNodes()
      const links = graphInstance.getLinks()
      
      // 找出所有没有入边的节点作为根节点
      const rootNodes = nodes.filter(node => {
        const nodeId = node.id
        return !links.some(link => {
          const relations = link.relations || []
          return relations.some(relation => {
            const target = relation.data?.target
            return target === nodeId
          })
        })
      })
      
      // 如果找到了根节点，设置为布局的起始点
      if (rootNodes.length > 0) {
        targetLayout.rootIds = rootNodes.map(node => node.id)
      }
    }
    
    await graphInstance.switchLayout(targetLayout, false, true)
    await graphInstance.zoomToFit()
    graphInstance.options.useAnimationWhenRefresh = true
  }
}

const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

const onNodeExpand = async (node: RGNode, $event: RGUserEvent) => {
  console.log('onNodeExpand:', node);
  const graphInstance = relationGraph$.value!.getInstance();
  // 展开节点时只展开当前节点，保持子节点的收缩状态
  node.expanded = true;
  if (node.lot?.childs) {
    node.lot.childs.forEach(child => {
      child.expanded = false;
    });
  }
  await graphInstance.doLayout();
};

const onNodeCollapse = async (node: RGNode, $event: RGUserEvent) => {
  console.log('onNodeCollapse:', node);
  const graphInstance = relationGraph$.value!.getInstance();
  // 收缩节点时，同时收缩其所有子节点
  const collapseNode = (node: RGNode) => {
    node.expanded = false;
    if (node.lot?.childs) {
      node.lot.childs.forEach(child => collapseNode(child));
    }
  };
  collapseNode(node);
  await graphInstance.doLayout();
};

// 关系点击事件处理
const onLineClick = (line: RGLine, link: RGLink, e: RGUserEvent) => {
  hideAllPanel()
  
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return true
  
  // 获取关系数据
  const relationData = link.relations[0]?.data
  
  // 扩展关系对象
  const extendedLine: ExtendedRGLink = {
    ...link,
    sourceNodeText: relationData?.fromText || '未知节点',
    targetNodeText: relationData?.toText || '未知节点',
    data: relationData,
    color: line.color || '#666666'
  }
  
  selectedRelation.value = extendedLine
  isPanelForNode.value = false
  showNodeDetail.value = true
  
  return true
}

// 修改关闭面板函数
const closeNodeDetail = () => {
  showNodeDetail.value = false
  selectedNode.value = null
  selectedRelation.value = null
  isPanelForNode.value = true
}

// 生命周期钩子
onMounted(() => {
  // 初始化关系类型
  const relTypeSet = new Set<string>()
  demoData.lines.forEach((line: any) => {
    if (line.text) {
      relTypeSet.add(line.text)
    }
  })
  all_rel_type.value = Array.from(relTypeSet)
  rel_checkList.value = Array.from(relTypeSet)

  // 初始化节点标签
  const labelSet = new Set<string>()
  demoData.nodes.forEach((node: any) => {
    if (node.data && Array.isArray(node.data.labels)) {
      node.data.labels.forEach((label: string) => {
        labelSet.add(label)
      })
    }
  })
  all_node_labels.value = Array.from(labelSet)
  node_checkList.value = Array.from(labelSet)

  // 初始化图谱
  relationGraph$.value?.setJsonData(visibleData.value, () => {
    console.log('relationGraph ready!')
  })
})

onBeforeUnmount(() => {
  hideAllPanel()
})
</script>

<style scoped>
.knowledge-graph-container {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #f8fafc;
  overflow: hidden;
}

.graph-wrapper {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  height: calc(100vh - 100px);
  width: 100%;
  position: relative;
  background-color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  position: relative;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 24px 0 rgba(0, 0, 0, 0.12), 0 2px 8px 0 rgba(0,0,0,0.06);
  background: radial-gradient(circle at 50% 40%, rgba(255,255,255,0.45) 0%, rgba(0,0,0,0.02) 80%, transparent 100%), var(--node-color, #4ea1e6);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
}

.node-content:hover,
.node-content.node-hover {
  transform: scale(1.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.node-text {
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  padding: 0 8px;
  word-break: break-all;
  line-height: 1.3;
  max-width: 80px;
  max-height: 80px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.menu-toggle {
  position: absolute;
  left: 16px;
  top: 24px;
  z-index: 800;
  width: 36px;
  height: 36px;
  background-color: #2563eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid #fff;
}

.menu-toggle:hover {
  background-color: #1d4ed8;
  transform: scale(1.05);
}

.control-panel {
  position: fixed;
  z-index: 700;
  left: 0;
  top: 50%;
  transform: translateY(-50%) translateX(0);
  padding: 24px 20px 24px 16px;
  border-radius: 0 12px 12px 0;
  background-color: rgba(255, 255, 255, 0.98);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.10);
  min-width: 320px;
  max-width: 380px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  backdrop-filter: blur(12px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 80vh;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.menu-hidden {
  transform: translateX(-100%) translateY(-50%);
  opacity: 0;
  pointer-events: none;
}

.panel-section {
  margin-bottom: 24px;
  padding: 16px 8px 16px 0;
  border-radius: 8px;
  background-color: rgba(248, 250, 252, 0.5);
  transition: all 0.3s ease;
  max-height: 180px;
  overflow: auto;
}

.panel-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.layout-buttons {
  display: flex;
  flex-direction: row;
  gap: 12px;
  width: 100%;
  justify-content: space-between;
}

.layout-buttons .el-button {
  flex: 1 1 0;
  min-width: 0;
  height: 36px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin: 0;
}

.search-area {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.search-select {
  flex: 1;
  min-width: 0;
}

.only-related-checkbox {
  white-space: nowrap;
  margin: 0;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 4px;
  max-height: 110px;
  overflow-y: auto;
  background: transparent;
}

:deep(.el-checkbox) {
  margin-right: 0;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.5);
}

:deep(.el-checkbox:hover) {
  background-color: rgba(255, 255, 255, 0.8);
}

:deep(.el-checkbox__label) {
  font-size: 12px;
  color: #475569;
  font-weight: 500;
  line-height: 1.2;
}

:deep(.el-button) {
  font-weight: 500;
  letter-spacing: 0.3px;
}

:deep(.el-select) {
  width: 100%;
}

.node-detail-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 360px;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.98);
  border-left: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(100%);
  z-index: 1000;
  backdrop-filter: blur(12px);
}

.panel-show {
  transform: translateX(0);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  background-color: rgba(255, 255, 255, 0.9);
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: 0.3px;
}

.close-icon {
  cursor: pointer;
  padding: 6px;
  color: #64748b;
  transition: all 0.3s ease;
  border-radius: 6px;
}

.close-icon:hover {
  color: #1e293b;
  background-color: rgba(0, 0, 0, 0.05);
  transform: scale(1.1);
}

.panel-content {
  padding: 24px;
  overflow-y: auto;
  height: calc(100% - 70px);
}

.empty-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: calc(100% - 70px);
  color: #94a3b8;
  font-size: 14px;
  background-color: rgba(248, 250, 252, 0.5);
  border-radius: 12px;
  margin: 24px;
  padding: 24px;
  text-align: center;
  line-height: 1.6;
}

.detail-item {
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.detail-item:hover {
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.item-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.item-value {
  display: block;
  font-size: 14px;
  color: #1e293b;
  word-break: break-all;
  line-height: 1.6;
}


:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  min-width: 44px;
  text-align: center;
  padding: 4px 12px;
  height: auto;
  line-height: 1.5;
  border: 1px solid rgba(226, 232, 240, 0.8);
  background-color: rgba(226, 232, 240, 0.5);
  transition: all 0.3s ease;
}

:deep(.el-tag:hover) {
  background-color: rgba(226, 232, 240, 0.8);
  transform: translateY(-1px);
}

.panel-section.layout-section {
  max-height: none;
  overflow: visible;
  padding-bottom: 12px;
}

.panel-section.search-section {
  max-height: 90px;
  min-height: 70px;
  overflow: visible;
}

.panel-section.filter-section {
  max-height: 180px;
  min-height: 80px;
  overflow: visible;
  padding: 12px 8px 8px 0;
}
</style>

