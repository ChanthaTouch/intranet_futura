<template>
  <div>
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold">E-Project Introduction</h2>
      <div class="flex gap-2">
        <button class="px-3 py-1 border rounded">Getting Started</button>
        <button class="px-3 py-1 border rounded">Manual</button>
        <button class="px-3 py-1 border rounded">Leaflet</button>
        <button class="px-3 py-1 border rounded">New in E-project</button>
        <button class="px-3 py-1 border rounded" @click="makeClientAccess" :disabled="!selectedId">Client Access</button>
        <button class="px-3 py-1 border rounded">Access Rights</button>
      </div>
    </div>
    <div class="bg-yellow-50 border rounded p-3 my-4 text-sm">
      If you cannot access the contract you are working on, please ask your project assistant to add you in Organisation &amp; Directory.
    </div>
    <div class="flex gap-2 items-end mb-4">
      <div>
        <label class="block text-sm">Office</label>
        <select v-model.number="office" @change="loadStats" class="border rounded p-2">
          <option v-for="o in offices" :key="o.id" :value="o.id">{{ o.name }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm">Select Contract</label>
        <select v-model.number="selectedId" class="border rounded p-2">
          <option :value='null'>—</option>
          <option v-for="c in allContracts" :key="c.id" :value="c.id">{{ c.code }} — {{ c.name }}</option>
        </select>
      </div>
      <button class="px-3 py-2 border rounded" @click="favSelected" :disabled="!selectedId">★ Favourite</button>
    </div>
    <div class="space-y-2">
      <Accordion title="My Favourite Contracts" :count="stats.favorites" @toggle="() => loadGroup('favorites')">
        <ContractList :items="lists.favorites"/>
      </Accordion>
      <Accordion title="Contracts · External Clients" :count="stats.external" @toggle="() => loadGroup('external')">
        <ContractList :items="lists.external"/>
      </Accordion>
      <Accordion title="Contracts · Internal Clients" :count="stats.internal" @toggle="() => loadGroup('internal')">
        <ContractList :items="lists.internal"/>
      </Accordion>
      <Accordion title="On Hold Contracts" :count="stats.on_hold" @toggle="() => loadGroup('on_hold')">
        <ContractList :items="lists.on_hold"/>
      </Accordion>
      <Accordion title="To be Liquidated Contracts" :count="stats.to_be_liquidated" @toggle="() => loadGroup('to_be_liquidated')">
        <ContractList :items="lists.to_be_liquidated"/>
      </Accordion>
      <Accordion title="Archived Contracts" :count="stats.archived" @toggle="() => loadGroup('archived')">
        <ContractList :items="lists.archived"/>
      </Accordion>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../../api'
const offices = ref([])
const office = ref()
const selectedId = ref(null)
const stats = reactive({favorites:0, external:0, internal:0, on_hold:0, to_be_liquidated:0, archived:0})
const lists = reactive({favorites:[], external:[], internal:[], on_hold:[], to_be_liquidated:[], archived:[]})
const allContracts = ref([])
async function loadOffices(){ const { data } = await api.get('/api/contracts/offices'); offices.value = data; office.value = data[0]?.id }
async function loadStats(){ const { data } = await api.get('/api/contracts/stats', { params: { office_id: office.value } }); Object.assign(stats, data); allContracts.value = []; for (const g of ['favorites','external','internal']) { const { data: list } = await api.get('/api/contracts/list', { params: { group: g, office_id: office.value } }); lists[g] = list; allContracts.value = [...new Map([...allContracts.value, ...list].map(x => [x.id, x])).values()] } }
async function loadGroup(g){ const { data } = await api.get('/api/contracts/list', { params: { group: g, office_id: office.value } }); lists[g] = data }
async function favSelected(){ await api.post(`/api/contracts/favorite/${selectedId.value}`); await loadStats() }
async function makeClientAccess(){ const { data } = await api.post(`/api/contracts/client-access/${selectedId.value}`); alert('Client link token: ' + data.token) }
onMounted(async () => { await loadOffices(); await loadStats() })
</script>
<script>
export default {
  components: {
    Accordion: {
      props: ['title','count'],
      emits: ['toggle'],
      data(){ return { open: false } },
      template: `<div class="border rounded">
        <button class="w-full flex justify-between items-center px-4 py-2 bg-teal-700 text-white rounded-t" @click="open=!open; $emit('toggle')">
          <span>{{ title }}</span><span class="text-xs bg-white/20 px-2 py-0.5 rounded">{{ count }}</span>
        </button>
        <div v-show="open" class="p-3"><slot/></div>
      </div>`
    },
    ContractList: {
      props:['items'],
      template:`<table class='w-full text-sm'><thead><tr class='text-left'><th class='p-2'>Code</th><th>Name</th><th>Status</th><th>Type</th></tr></thead><tbody><tr v-for='c in items' :key='c.id'><td class='p-2'>{{ c.code }}</td><td>{{ c.name }}</td><td>{{ c.status }}</td><td>{{ c.client_type }}</td></tr></tbody></table>`
    }
  }
}
</script>
