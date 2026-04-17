<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { darkTheme, zhCN, dateZhCN } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#002EA6',
    primaryColorHover: '#1a4fd0',
    primaryColorPressed: '#001d6e',
    primaryColorSuppl: '#FFE76F',
    bodyColor: '#0a0f1e',
    cardColor: 'rgba(13, 21, 41, 0.85)',
    modalColor: '#0d1529',
    popoverColor: '#0d1529',
    tableColor: 'rgba(13, 21, 41, 0.85)',
    inputColor: 'rgba(255, 255, 255, 0.06)',
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  Button: {
    textColorPrimary: '#FFE76F',
    colorPrimary: '#002EA6',
    colorHoverPrimary: '#1a4fd0',
    colorPressedPrimary: '#001d6e',
    borderPrimary: '#002EA6',
    borderHoverPrimary: '#1a4fd0',
  },
  Tag: {
    colorInfo: 'rgba(0, 46, 166, 0.2)',
    textColorInfo: '#5b8def',
  },
}
</script>
