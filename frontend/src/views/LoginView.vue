<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'
import { login } from '../api/auth'
import { extractErrorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const auth = useAuthStore()

const loading = ref(false)
const formRef = ref()
const form = reactive({ username: '', password: '' })
const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const resp = await login(form.username, form.password)
    auth.setSession(resp.data.token, resp.data.user)
    message.success('登录成功')
    router.push((route.query.redirect as string) || '/dashboard')
  } catch (error) {
    message.error(extractErrorMessage(error))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <n-card class="auth-card" :bordered="false">
    <h2>登录</h2>
    <p class="auth-subtitle">LingTuDemo - 认证与 AI 用户名审核 Demo</p>
    <n-form ref="formRef" :model="form" :rules="rules" size="large">
      <n-form-item path="username" label="用户名">
        <n-input
          v-model:value="form.username"
          placeholder="请输入用户名"
          :input-props="{ autocomplete: 'username' }"
          @keyup.enter="handleSubmit"
        />
      </n-form-item>
      <n-form-item path="password" label="密码">
        <n-input
          v-model:value="form.password"
          type="password"
          show-password-on="click"
          placeholder="请输入密码"
          :input-props="{ autocomplete: 'current-password' }"
          @keyup.enter="handleSubmit"
        />
      </n-form-item>
      <n-button type="primary" block size="large" :loading="loading" @click="handleSubmit">
        登录
      </n-button>
      <p class="auth-subtitle" style="margin-top: 16px">
        还没有账号？<router-link to="/register">去注册</router-link>
      </p>
    </n-form>
  </n-card>
</template>
