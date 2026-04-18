<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">智能文档系统</h1>
      <p class="login-subtitle">基于大语言模型的文档理解与多源数据融合</p>

      <n-tabs v-model:value="activeTab" type="segment" animated>
        <n-tab-pane name="login" tab="登录">
          <n-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="auth-form">
            <n-form-item path="email" label="邮箱">
              <n-input v-model:value="loginForm.email" placeholder="请输入邮箱" />
            </n-form-item>
            <n-form-item path="password" label="密码">
              <n-input v-model:value="loginForm.password" type="password" show-password-on="click" placeholder="请输入密码" @keyup.enter="handleLogin" />
            </n-form-item>
            <n-button type="primary" block strong :loading="loading" @click="handleLogin">登录</n-button>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="register" tab="注册">
          <n-form ref="registerFormRef" :model="registerForm" :rules="registerRules" class="auth-form">
            <n-form-item path="username" label="用户名">
              <n-input v-model:value="registerForm.username" placeholder="请输入用户名" />
            </n-form-item>
            <n-form-item path="email" label="邮箱">
              <n-input v-model:value="registerForm.email" placeholder="请输入邮箱" />
            </n-form-item>
            <n-form-item path="password" label="密码">
              <n-input v-model:value="registerForm.password" type="password" show-password-on="click" placeholder="请输入密码（至少6位）" @keyup.enter="handleRegister" />
            </n-form-item>
            <n-button type="primary" block strong :loading="loading" @click="handleRegister">注册</n-button>
          </n-form>
        </n-tab-pane>
      </n-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const loading = ref(false)
const activeTab = ref('login')

const loginForm = ref({ email: '', password: '' })
const registerForm = ref({ username: '', email: '', password: '' })

const loginRules = {
  email: { required: true, message: '请输入邮箱', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
}
const registerRules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  email: { required: true, message: '请输入邮箱', trigger: 'blur' },
  password: { required: true, min: 6, message: '密码至少6位', trigger: 'blur' },
}

const loginFormRef = ref(null)
const registerFormRef = ref(null)

const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()
  } catch { return }
  loading.value = true
  try {
    await authStore.login(loginForm.value.email, loginForm.value.password)
    message.success('登录成功')
    router.push('/')
  } catch (e) {
    message.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  try {
    await registerFormRef.value?.validate()
  } catch { return }
  loading.value = true
  try {
    await authStore.register(registerForm.value.email, registerForm.value.username, registerForm.value.password)
    message.success('注册成功')
    router.push('/')
  } catch (e) {
    message.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
}
.login-card {
  width: 420px;
  padding: 2.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(12px);
}
.login-title {
  text-align: center;
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}
.login-subtitle {
  text-align: center;
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: 2rem;
}
.auth-form {
  margin-top: 1.5rem;
}
</style>
