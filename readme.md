# 知识图谱可视化工具

## 1. 概述

本工具基于 [seeksdream/relation-graph](https://github.com/seeksdream/relation-graph) 工具开发，本工具利用Neo4j 进行初步的数据预处理导出后的jsonl数据，使用 Vue 3 进行开发，能够支持知识图谱的关系筛选、节点筛选、导览、力学布局修改等功能。

## 2. 数据准备

### 2.1 Neo4j 配置

在使用本工具前，你需要确保 Neo4j 已经正确配置了 APOC（Awesome Procedures on Cypher）插件。APOC 插件为 Neo4j 提供了许多额外的功能，包括数据导入导出等。

### 2.2 数据导出

通过如下指令，从 Neo4j 中导出对应的数据：

```Cypher
CALL apoc.export.json.all("all_data.jsonl", {useTypes:true})
```

### 2.3 数据放置

将导出的 `all_data.jsonl` 文件置入项目的 `assets` 文件夹下。

## 3. 数据预处理

### 3.1 初步筛选

首先将数据格式进行简单的初筛，得到对应的 `data`。你可以选择跳过这一步，因为该方法仅提供了一版简单的初筛。

```bash
python utils/process_jsonl.py
```

### 3.2 格式转换

进一步将数据格式转换成对应的可视化组件支持的格式。

```bash
python utils/convert_data.py
```

## 4. 系统运行

### 4.1 使用 npm 运行

```bash
# 安装对应环境
npm install
# 运行知识图谱组件
npm run serve
```

### 4.2 使用 yarn 运行

```bash
# 安装对应环境
yarn install
# 运行知识图谱组件
yarn dev
```