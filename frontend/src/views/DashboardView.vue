<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NButton,
  NTag,
  NSpace,
  NSpin,
  NResult,
  NList,
  NListItem,
  NThing,
  useMessage,
} from 'naive-ui'
import { fetchResourceA, fetchResourceB, type ResourceInfo } from '../api/resources'
import { extractErrorMessage } from '../api/http'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

interface ResourceState {
  status: 'idle' | 'loading' | 'ok' | 'forbidden' | 'error'
  data?: ResourceInfo
  error?: string
}

const resourceA = ref<ResourceState>({ status: 'idle' })
const resourceB = ref<ResourceState>({ status: 'idle' })

const roleTagType = computed(() =>
  auth.user?.role === 'ADMIN' ? 'success' : ('info' as 'success' | 'info'),
)

async function loadResourceA() {
  resourceA.value = { status: 'loading' }
  try {
    const resp = await fetchResourceA()
    resourceA.value = { status: 'ok', data: resp.data }
  } catch (error) {
    resourceA.value = { status: 'error', error: extractErrorMessage(error) }
  }
}

async function loadResourceB() {
  resourceB.value = { status: 'loading' }
  try {
    const resp = await fetchResourceB()
    resourceB.value = { status: 'ok', data: resp.data }
  } catch (error) {
    const status = (error as { response?: { status?: number } }).response?.status
    if (status === 403) {
      resourceB.value = { status: 'forbidden' }
    } else {
      resourceB.value = { status: 'error', error: extractErrorMessage(error) }
    }
  }
}

function handleLogout() {
  auth.logout()
  message.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  loadResourceA()
  loadResourceB()
})
</script>

<template>
  <div style="max-width: 720px; margin: 5vh auto 40px; padding: 0 16px">
    <n-card :bordered="false" style="margin-bottom: 20px">
      <n-space justify="space-between" align="center">
        <n-space align="center" :size="12">
          <strong style="font-size: 18px">{{ auth.user?.username }}</strong>
          <n-tag :type="roleTagType" size="small">{{ auth.user?.role }}</n-tag>
        </n-space>
        <n-button quaternary type="error" @click="handleLogout">退出登录</n-button>
      </n-space>
    </n-card>

    <n-card title="Resource A" :bordered="false" style="margin-bottom: 20px">
      <template #header-extra>
        <n-tag type="success" size="small">✓ 所有登录用户可访问</n-tag>
      </template>
      <n-spin v-if="resourceA.status === 'loading'" size="small" />
      <n-result
        v-else-if="resourceA.status === 'error'"
        status="error"
        title="加载失败"
        :description="resourceA.error"
        size="small"
      />
      <n-list v-else bordered>
        <n-list-item>
          <n-thing :title="resourceA.data?.resource" :description="resourceA.data?.message" />
        </n-list-item>
      </n-list>
    </n-card>

    <n-card title="Resource B" :bordered="false">
      <template #header-extra>
        <n-tag :type="auth.isAdmin ? 'success' : 'warning'" size="small">
          {{ auth.isAdmin ? '✓ 管理员可访问' : '🔒 仅管理员可访问' }}
        </n-tag>
      </template>
      <n-spin v-if="resourceB.status === 'loading'" size="small" />
      <template v-else-if="resourceB.status === 'ok'">
        <n-list bordered>
          <n-list-item>
            <n-thing :title="resourceB.data?.resource" :description="resourceB.data?.message" />
          </n-list-item>
        </n-list>
      </template>
      <n-result
        v-else-if="resourceB.status === 'forbidden'"
        status="403"
        title="403"
        description="没有访问资源 B 的权限（仅 ADMIN 角色可访问）"
        size="small"
      />
      <n-result
        v-else-if="resourceB.status === 'error'"
        status="error"
        title="加载失败"
        :description="resourceB.error"
        size="small"
      />
    </n-card>
  </div>
</template>
