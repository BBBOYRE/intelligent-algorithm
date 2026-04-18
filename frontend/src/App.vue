<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { zhCN, dateZhCN } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#3370ff',
    primaryColorHover: '#5b8def',
    primaryColorPressed: '#245bdb',
    primaryColorSuppl: '#3370ff',
    bodyColor: '#ffffff',
    cardColor: '#ffffff',
    modalColor: '#ffffff',
    popoverColor: '#ffffff',
    tableColor: '#ffffff',
    inputColor: '#f2f3f5',
    borderColor: '#e5e6eb',
    textColorBase: '#1f2329',
    textColor1: '#1f2329',
    textColor2: '#646a73',
    textColor3: '#8f959e',
  },
  Button: {
    textColorPrimary: '#ffffff',
    colorPrimary: '#3370ff',
    colorHoverPrimary: '#5b8def',
    colorPressedPrimary: '#245bdb',
    borderPrimary: '#3370ff',
    borderHoverPrimary: '#5b8def',
  },
  Tag: {
    colorInfo: 'rgba(51, 112, 255, 0.08)',
    textColorInfo: '#3370ff',
  },
}
</script>
