
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import Schedule from './Schedule.vue'
import Files from './Files.vue'

const route = useRoute()
const projectId = ref(Number(route.params.id))

const project = ref(null)
const tab = ref('schedule')

async function load() {
  const { data } = await api.get(`/api/projects/${projectId.value}`)
  project.value = data
}

onMounted(load)
watch(() => route.params.id, (id) => { projectId.value = Number(id); load() })
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold">{{ project?.name || 'Project' }}</h1>
        <p class="text-sm text-gray-500">
          Code: {{ project?.code || '-' }} • Type: {{ project?.client_type || '-' }} • Status: {{ project?.status || '-' }}
        </p>
        <p class="text-sm text-gray-500">
          Start: {{ project?.start_date || '-' }} • End: {{ project?.end_date || '-' }}
        </p>
      </div>
      <div class="flex gap-2">
        <button :class="tab==='overview' ? 'px-3 py-1 border rounded bg-black/5' : 'px-3 py-1 border rounded'" @click="tab='overview'">Overview</button>
        <button :class="tab==='comm' ? 'px-3 py-1 border rounded bg-black/5' : 'px-3 py-1 border rounded'" @click="tab='comm'">Communication</button>
        <button :class="tab==='files' ? 'px-3 py-1 border rounded bg-black/5' : 'px-3 py-1 border rounded'" @click="tab='files'">Files</button>
        <button :class="tab==='data' ? 'px-3 py-1 border rounded bg-black/5' : 'px-3 py-1 border rounded'" @click="tab='data'">Data</button>
        <button :class="tab==='schedule' ? 'px-3 py-1 border rounded bg-black/5' : 'px-3 py-1 border rounded'" @click="tab='schedule'">Schedule</button>
      </div>
    </div>

    <section v-if="tab==='schedule'">
      <Schedule :project-id="projectId" />
    </section>
    <section v-else-if="tab==='files'">
      <Files :project-id="projectId" />
    </section>
    <section v-else class="border rounded p-6 bg-white">
      <p>Coming soon.</p>
    </section>
  </div>
</template>
