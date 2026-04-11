---
theme: seriph
background: https://cover.sli.dev
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  ## Slidev Presentation
  Presentation for Intelligent Algorithm project.
drawings:
  persist: false
transition: slide-left
title: 智能算法项目汇报
---

# 智能算法项目汇报

Intelligent Algorithm Project Presentation

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    按空格键查看下一页 <carbon:arrow-right class="inline"/>
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <button @click="$slidev.nav.openInEditor()" title="在编辑器中打开" class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon:edit />
  </button>
</div>

---
transition: fade-out
---

# 项目概览

介绍我们项目的核心功能和主要架构

- 📝 **智能文档处理** - 高效的文档解析与内容抽取
- 🤖 **AI模型赋能** - 集成先进的大语言模型技术
- ⚡️ **高性能架构** - FastAPI + Vue3 的现代化技术栈
- 🛠️ **一键部署** - 方便快捷的依赖管理与应用打包

<br>
<br>

<style>
h1 {
  background-color: #2B90B6;
  background-image: linear-gradient(45deg, #4EC5D4 10%, #146b8c 20%);
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>
