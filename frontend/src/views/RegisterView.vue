<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { NForm, NFormItem, NInput, NButton, NAlert, NSpin, useMessage } from 'naive-ui'
import { register } from '../api/auth'
import { extractErrorMessage } from '../api/http'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const moderating = ref(false)
const formRef = ref()
const form = reactive({ username: '', password: '', confirmPassword: '' })

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度需在 3-20 个字符之间', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string) => !/\s/.test(value || ''),
      message: '用户名不能包含空白字符',
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 64, message: '密码长度需在 8-64 个字符之间', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string) => value === form.password,
      message: '两次输入的密码不一致',
      trigger: 'blur',
    },
  ],
}

const rejectReason = ref('')
const rejected = computed(() => rejectReason.value !== '')

async function handleSubmit() {
  rejectReason.value = ''
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  loading.value = true
  // 提交后进入 LLM 审核阶段（注册接口同步等待审核结果）
  moderating.value = true
  try {
    await register(form.username, form.password, form.confirmPassword)
    message.success('注册成功，AI 审核通过！请登录')
    router.push('/login')
  } catch (error) {
    const msg = extractErrorMessage(error)
    rejectReason.value = msg
    message.error(msg)
  } finally {
    loading.value = false
    moderating.value = false
  }
}
</script>

<template>
  <n-card class="auth-card" :bordered="false">
    <h2>注册</h2>
    <p class="auth-subtitle">用户名将由 AI 实时审核</p>
    <n-alert
      v-if="rejected"
      type="error"
      closable
      title="用户名未通过审核"
      style="margin-bottom: 16px"
      @close="rejectReason = ''"
    >
      {{ rejectReason }}
    </n-alert>
    <n-form ref="formRef" :model="form" :rules="rules" size="large">
      <n-form-item path="username" label="用户名">
        <n-input v-model:value="form.username" placeholder="3-20 个字符，不含空格" />
      </n-form-item>
      <n-form-item path="password" label="密码">
        <n-input
          v-model:value="form.password"
          type="password"
          show-password-on="click"
          placeholder="至少 8 位"
        />
      </n-form-item>
      <n-form-item path="confirmPassword" label="确认密码">
        <n-input
          v-model:value="form.confirmPassword"
          type="password"
          show-password-on="click"
          placeholder="再次输入密码"
          @keyup.enter="handleSubmit"
        />
      </n-form-item>

      <div v-if="moderating" style="text-align: center; margin-bottom: 12px">
        <n-spin size="small" />
        <p style="color: #18a058; font-size: 13px; margin: 6px 0 0">🤖 AI 正在审核用户名…</p>
      </div>

      <n-button
        type="primary"
        block
        size="large"
        :loading="loading"
        :disabled="loading"
        @click="handleSubmit"
      >
        注册
      </n-button>
      <p class="auth-subtitle" style="margin-top: 16px">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
    </n-form>
  </n-card>
</template>
