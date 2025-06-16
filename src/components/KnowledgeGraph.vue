<template>
  <div class="knowledge-graph-container">
    <div class="graph-wrapper">
      <RelationGraph ref="relationGraph$" :options="options" :on-node-click="onNodeClick">
        <template #node="{node}">
          <div class="node-content">
            <div class="node-icon" :style="{'background-image': node.data?.icon ? `url(${node.data.icon})` : 'none'}"></div>
            <div class="node-text" :style="{color: node.color}">{{node.text}}</div>
          </div>
        </template>
        <template #graph-plug>
          <div class="search-panel">
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
              <el-radio-group v-model="checked_sex" size="small" @change="doFilter">
                <el-radio-button label="">全部</el-radio-button>
                <el-radio-button label="male">男性</el-radio-button>
                <el-radio-button label="female">女性</el-radio-button>
              </el-radio-group>
              <el-radio-group v-model="checked_isgoodman" size="small" @change="doFilter">
                <el-radio-button label="">全部</el-radio-button>
                <el-radio-button :label="true">正面</el-radio-button>
                <el-radio-button :label="false">负面</el-radio-button>
              </el-radio-group>
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
import { onMounted, ref, computed } from 'vue'
import RelationGraph, { RGJsonData, RGNode, RGUserEvent } from 'relation-graph/vue3'
import { ElRadioGroup, ElRadioButton, ElCheckboxGroup, ElCheckbox, ElSelect, ElOption } from 'element-plus'
import demoData from '../assets/demo.json'

const relationGraph$ = ref<RelationGraph>()
const searchText = ref('')
const checked_sex = ref('')
const checked_isgoodman = ref('')
const rel_checkList = ref(['师生', '上下级', '亲戚', '情人', '朋友', '夫妻', '勾结', '腐化', '举报']);
const all_rel_type = ref(['师生', '上下级', '亲戚', '情人', '朋友', '夫妻', '勾结', '腐化', '举报']);

const options = {
  defaultExpandHolderPosition: 'right',
  debug: true,
  showDebugPanel: true,
  defaultNodeBorderWidth: 0,
  defaultNodeColor: 'rgba(238, 178, 94, 1)',
  allowSwitchLineShape: true,
  allowSwitchJunctionPoint: true,
  defaultLineShape: 1,
  layouts: [
    {
      label: '自动布局',
      layoutName: 'force',
      layoutClassName: 'seeks-layout-force'
    }
  ],
  defaultJunctionPoint: 'border'
}

const searchOptions = computed(() => {
  const graphInstance = relationGraph$.value?.getInstance()
  if (!graphInstance) return []
  
  return graphInstance.getNodes().map(node => ({
    value: node.id,
    label: `${node.text} (${node.id})`
  }))
})

const onNodeClick = (node: RGNode, e: RGUserEvent) => {
  console.log('onNodeClick:', node.id)
  return true
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

  _all_nodes.forEach(thisNode => {
    let _isHideThisLine = false
    if (checked_sex.value !== '') {
      if (thisNode.data?.['sexType'] !== checked_sex.value) {
        _isHideThisLine = true
      }
    }
    if (checked_isgoodman.value !== '') {
      if (thisNode.data?.['isGoodMan'] !== checked_isgoodman.value) {
        _isHideThisLine = true
      }
    }
    thisNode.opacity = _isHideThisLine ? 0.1 : 1
  })

  _all_links.forEach(thisLink => {
    thisLink.relations.forEach(thisLine => {
      if (rel_checkList.value.indexOf(thisLine.data?.['type']) === -1) {
        if (!thisLine.isHide) {
          thisLine.isHide = true
          console.log('Hide line:', thisLine)
        }
      } else {
        if (thisLine.isHide) {
          thisLine.isHide = false
          console.log('Show line:', thisLine)
        }
      }
    })
  })

  graphInstance.dataUpdated()
}

onMounted(() => {
  relationGraph$.value?.setJsonData(demoData, () => {
    console.log('relationGraph ready!')
  })
})
</script>

<style scoped>
.knowledge-graph-container {
  width: 100%;
  height: 100%;
}

.graph-wrapper {
  border: #efefef solid 1px;
  height: calc(100vh - 100px);
  width: 100%;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  position: relative;
}

.node-icon {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-position: center center;
  background-size: cover;
  background-repeat: no-repeat;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.node-text {
  position: absolute;
  bottom: -25px;
  width: 100%;
  text-align: center;
  color: #2E74B5;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 5px;
  box-sizing: border-box;
}

.search-panel {
  position: absolute;
  z-index: 700;
  left: 20px;
  top: 20px;
  padding: 10px 20px;
  border: #efefef solid 1px;
  color: #555555;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
}

.search-section {
  margin-bottom: 10px;
}

.search-title {
  line-height: 20px;
  margin-bottom: 5px;
  font-weight: bold;
}

.filter-section {
  margin-bottom: 10px;
}

.filter-title {
  line-height: 20px;
  margin-bottom: 5px;
  font-weight: bold;
}

:deep(.el-radio-group) {
  margin-right: 20px;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
