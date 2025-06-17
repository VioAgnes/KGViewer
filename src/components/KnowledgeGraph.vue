<template>
  <div class="knowledge-graph-container">
    <div class="graph-wrapper" @mouseleave="onMouseLeave">
      <RelationGraph ref="relationGraph$" :options="options" :on-node-click="onNodeClick" :on-node-hover="onNodeHover" :on-node-mouseleave="onNodeMouseLeave">
        <template #node="{node}">
          <div class="node-content">
            <div class="node-text" :style="{color: node.color}">{{node.text}}</div>
          </div>
        </template>
        <template #graph-plug>
          <div v-show="showNodeTooltip" class="node-tooltip" :style="{left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px'}">
            <div class="tooltip-title">{{currentNode?.text}}</div>
            <div class="tooltip-content">
              <div v-if="currentNode?.data?.sexType" class="tooltip-item">
                <span class="label">性别:</span>
                <span class="value">{{currentNode.data.sexType === 'male' ? '男' : '女'}}</span>
              </div>
              <div v-if="currentNode?.data?.isGoodMan !== undefined" class="tooltip-item">
                <span class="label">性质:</span>
                <span class="value">{{currentNode.data.isGoodMan ? '正面' : '负面'}}</span>
              </div>
              <div v-if="currentNode?.data?.description" class="tooltip-item">
                <span class="label">描述:</span>
                <span class="value">{{currentNode.data.description}}</span>
              </div>
            </div>
          </div>
          <div class="menu-toggle" @click="toggleMenu">
            <el-icon :size="20" :color="showMenu ? '#409EFF' : '#909399'">
              <component :is="showMenu ? 'ArrowRight' : 'ArrowLeft'" />
            </el-icon>
          </div>
          <div class="search-panel" :class="{ 'menu-hidden': !showMenu }">
            <div class="layout-section">
              <div class="layout-title">布局切换:</div>
              <el-button v-if="!playing" type="success" size="small" @click="play">自动切换布局</el-button>
              <el-button v-else type="danger" size="small" @click="stop">停止切换</el-button>
            </div>
            <div class="search-section">
              <div class="search-title">节点搜索:</div>
              <el-select
                v-model="searchText"
                size="small"
                filterable
                remote
                reserve-keyword
                placeholder="输入节点名称或ID搜索"
                @change="handleNodeSearch"
                style="width: 200px"
              >
                <el-option
                  v-for="item in searchOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </div>
            <div class="filter-section">
              <div class="filter-title">节点筛选:</div>
              <el-checkbox-group v-model="node_checkList" @change="doFilter">
                <el-checkbox v-for="item in all_node_labels" :key="item" :label="item" />
              </el-checkbox-group>
            </div>
            <div class="filter-section">
              <div class="filter-title">关系筛选:</div>
              <el-checkbox-group v-model="rel_checkList" @change="doFilter">
                <el-checkbox v-for="item in all_rel_type" :key="item" :label="item" />
              </el-checkbox-group>
            </div>
          </div>
        </template>
      </RelationGraph>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, onBeforeUnmount } from 'vue'
import RelationGraph, { 
  RGJsonData, 
  RGNode, 
  RGUserEvent, 
  RGLineShape, 
  RGJunctionPoint,
  RelationGraphComponent 
} from 'relation-graph/vue3'
import { ElRadioGroup, ElRadioButton, ElCheckboxGroup, ElCheckbox, ElSelect, ElOption, ElIcon } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import demoData from '../assets/converted_data.json'

// 类型定义
interface TooltipPosition {
  x: number
  y: number
}

// 响应式状态
const relationGraph$ = ref<RelationGraphComponent>()
const searchText = ref('')
const checked_sex = ref('')
const checked_isgoodman = ref('')
const rel_checkList = ref<string[]>([])
const all_rel_type = ref<string[]>([])
const all_node_labels = ref<string[]>([])
const node_checkList = ref<string[]>([])

// 悬浮提示相关状态
const showNodeTooltip = ref(false)
const currentNode = ref<RGNode | null>(null)
const tooltipPosition = ref<TooltipPosition>({ x: 0, y: 0 })

// 图表配置
const options = {
  defaultExpandHolderPosition: 'right' as const,
  showExpandHolder: true,
  debug: false,
  showDebugPanel: false,
  defaultNodeBorderWidth: 0,
  defaultNodeColor: 'rgba(238, 178, 94, 1)',
  allowSwitchLineShape: true,
  allowSwitchJunctionPoint: true,
  defaultLineShape: 1 as RGLineShape,
  layouts: [
    {
      label: '中心布局',
      layoutName: 'center',
      from: 'left',
      layoutClassName: 'seeks-layout-center',
      defaultExpandHolderPosition: 'hide',
      defaultJunctionPoint: 'border'
    },
    {
      label: '树形布局',
      layoutName: 'tree',
      from: 'left',
      layoutClassName: 'seeks-layout-center',
      defaultExpandHolderPosition: 'hide',
      defaultJunctionPoint: 'border'
    },
    {
      label: '环形布局',
      layoutName: 'circle',
      from: 'left',
      layoutClassName: 'seeks-layout-center',
      defaultExpandHolderPosition: 'hide',
      defaultJunctionPoint: 'border'
    },
    {
      label: '力导向布局',
      layoutName: 'force',
      from: 'left',
      layoutClassName: 'seeks-layout-center',
      defaultExpandHolderPosition: 'hide',
      defaultJunctionPoint: 'border'
    }
  ],
  defaultJunctionPoint: 'border' as RGJunctionPoint
}

// 添加布局切换相关状态
const playing = ref(false)
const currentLayoutIndex = ref(0)

// 添加菜单显示状态控制
const showMenu = ref(true)

// 计算属性
const searchOptions = computed(() => {
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return []
  
  return graphInstance.getNodes().map(node => ({
    value: node.id,
    label: `${node.text} (${node.id})`
  }))
})

// 事件处理函数
const onNodeClick = (node: RGNode, e: RGUserEvent) => {
  console.log('onNodeClick:', node.id)
  hideAllPanel()
  return true
}

const onNodeHover = (node: RGNode, e: RGUserEvent) => {
  if (!node) return
  
  showNodeTooltip.value = true
  currentNode.value = node
  
  const graphInstance = relationGraph$.value?.getInstance()
  if (graphInstance) {
    const rect = graphInstance.getBoundingClientRect()
    const mouseEvent = e as MouseEvent
    tooltipPosition.value = {
      x: mouseEvent.clientX - rect.left + 15,
      y: mouseEvent.clientY - rect.top + 15
    }
  }
}

const onNodeMouseLeave = () => {
  showNodeTooltip.value = false
}

const onMouseLeave = () => {
  showNodeTooltip.value = false
}

const handleNodeSearch = async (nodeId: string) => {
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return
  
  await graphInstance.focusNodeById(nodeId)
  await graphInstance.zoomToFit()
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
  showNodeTooltip.value = false
}

// 添加布局切换相关方法
const play = () => {
  playing.value = true
  switchLayout(0)
}

const stop = () => {
  playing.value = false
}

const switchLayout = async (layoutOptionsIndex: number) => {
  if (!playing.value) return
  if (layoutOptionsIndex > options.layouts.length - 1) layoutOptionsIndex = 0
  
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return
  
  await graphInstance.switchLayout(options.layouts[layoutOptionsIndex], false, true)
  await sleep(2000)
  await switchLayout(layoutOptionsIndex + 1)
}

const sleep = async (time: number) => {
  return new Promise<void>((resolve) => {
    setTimeout(() => {
      resolve()
    }, time)
  })
}

// 添加菜单切换方法
const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

// 生命周期钩子
onMounted(() => {
  // 动态生成关系类型
  const relTypeSet = new Set<string>()
  demoData.lines.forEach((line: any) => {
    if (line.text) {
      relTypeSet.add(line.text)
    }
  })
  all_rel_type.value = Array.from(relTypeSet)
  rel_checkList.value = Array.from(relTypeSet)

  // 动态生成所有节点标签
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

  relationGraph$.value?.setJsonData(demoData, () => {
    console.log('relationGraph ready!')
  })
})

onBeforeUnmount(() => {
  // 清理工作
  hideAllPanel()
})
</script>

<style scoped>
.knowledge-graph-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.graph-wrapper {
  border: #efefef solid 1px;
  height: calc(100vh - 100px);
  width: 100%;
  position: relative;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  position: relative;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.node-content:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.node-text {
  font-size: 14px;
  font-weight: bold;
  text-align: center;
  padding: 0 5px;
  word-break: break-all;
  line-height: 1.2;
  max-width: 70px;
  max-height: 70px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.node-tooltip {
  position: absolute;
  z-index: 9999;
  padding: 10px;
  border: #efefef solid 1px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-width: 200px;
  transition: opacity 0.3s ease;
}

.tooltip-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.tooltip-item .label {
  font-weight: bold;
  margin-right: 8px;
  color: #333;
}

.tooltip-item .value {
  flex: 1;
}

.menu-toggle {
  position: absolute;
  left: 20px;
  top: 60px;
  z-index: 800;
  width: 28px;
  height: 28px;
  background-color: #1e3a8a;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.menu-toggle:hover {
  background-color: #1e40af;
  transform: scale(1.05);
}

.menu-toggle .el-icon {
  color: #ffffff !important;
}

.search-panel {
  position: absolute;
  z-index: 700;
  left: 20px;
  top: 20px;
  padding: 15px 20px;
  border: #e5e7eb solid 1px;
  color: #374151;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.95);
  font-size: 13px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  transform: translateX(0);
  min-width: 240px;
}

.menu-hidden {
  transform: translateX(-100%);
  opacity: 0;
  pointer-events: none;
}

.layout-section,
.search-section,
.filter-section {
  margin-bottom: 15px;
}

.layout-title,
.search-title,
.filter-title {
  line-height: 20px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #1e3a8a;
}

:deep(.el-button) {
  font-weight: 500;
}

:deep(.el-radio-group) {
  margin-right: 20px;
  margin-bottom: 8px;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.el-select) {
  width: 100% !important;
}
</style>

