
<template>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h2 class="text-2xl font-bold">Task Card</h2>
      <div class="flex flex-wrap gap-2 items-center">
        <input v-model="newTitle" class="input" placeholder="Task title" />
        <input v-model="newDeadline" type="date" class="input" />
        <input v-model="newColor" type="color" class="input w-12 p-1" />
        <button class="btn btn-primary" @click="createTask" :disabled="creating || !newTitle.trim()">Add</button>
      </div>
    </div>

    <div class="grid md:grid-cols-3 gap-4">
      <div v-for="col in columns" :key="col.key" class="card p-3"
           @dragover.prevent @drop="onDrop(col.key)">
        <div class="font-semibold mb-2">{{ col.label }}</div>
        <div class="space-y-2 min-h-[120px]">
          <div v-for="t in tasksBy(col.key)" :key="t.id"
               class="rounded-lg p-3 shadow-sm border bg-white cursor-move"
               :style="{ borderColor: t.color || '#e5e7eb', background: t.color ? t.color+'22' : '#fff' }"
               draggable="true"
               @dragstart="dragStart(t)">
            <div class="flex items-start justify-between">
              <div class="font-medium">{{ t.title }}</div>
              <input type="color" v-model="t.color" @change="save(t)" class="w-6 h-6 border-0 bg-transparent"/>
            </div>
            <div class="text-xs text-gray-600 whitespace-pre-wrap mt-1">{{ t.description }}</div>
            <div class="text-xs text-gray-500 mt-1">Due: {{ t.deadline || '—' }}</div>
            <div class="flex gap-2 mt-2">
              <button class="text-xs underline" @click="edit(t)">Edit</button>
              <button class="text-xs underline text-red-600" @click="removeTask(t)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <dialog ref="dlg" class="modal">
      <form method="dialog" class="modal-box">
        <h3 class="font-bold mb-2">Edit Task</h3>
        <input v-model="editing.title" class="input w-full mb-2" placeholder="Title"/>
        <textarea v-model="editing.description" class="input w-full mb-2" rows="4" placeholder="Description"></textarea>
        <div class="flex gap-2">
          <input v-model="editing.deadline" type="date" class="input" />
          <select v-model="editing.status" class="input">
            <option value="todo">To Do</option>
            <option value="doing">Doing</option>
            <option value="done">Done</option>
          </select>
        </div>
        <div class="mt-3 flex justify-end gap-2">
          <button class="btn" @click="$refs.dlg.close()">Cancel</button>
          <button class="btn btn-primary" @click.prevent="save(editing)">Save</button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const tasks = ref([])
const creating = ref(false)
const drag = ref(null)
const columns = [
  { key: 'todo', label: 'To Do' },
  { key: 'doing', label: 'Doing' },
  { key: 'done', label: 'Done' },
]

const newTitle = ref('')
const newDeadline = ref('')
const newColor = ref('#2563eb')

const editing = ref({})
const dlg = ref(null)

function tasksBy(s){ 
  return tasks.value.filter(t=> (t.status || 'todo') === s)
                    .sort((a,b)=> (a.order_index||0)-(b.order_index||0) || a.id-b.id)
}
function dragStart(t){ drag.value = t }
function onDrop(status){
  if (!drag.value) return
  const t = drag.value
  t.status = status
  const last = tasksBy(status).slice(-1)[0]
  t.order_index = (last?.order_index || 0) + 1
  save(t)
  drag.value = null
}
function edit(t){ editing.value = JSON.parse(JSON.stringify(t)); dlg.value.showModal() }

async function load(){
  try{
    const { data } = await api.get('/api/tasks/my')
    tasks.value = Array.isArray(data) ? data : []
  }catch(e){
    console.error('Load tasks failed', e?.response?.data || e?.message)
    tasks.value = []
  }
}

async function createTask(){
  if(!newTitle.value.trim()) return
  creating.value = true
  try{
    const { data } = await api.post('/api/tasks', {
      title: newTitle.value, 
      deadline: newDeadline.value || null, 
      color: newColor.value, 
      status: 'todo'
    })
    if (data && data.id){
      tasks.value.push({ ...data, order_index: data.order_index ?? tasksBy('todo').length })
    }
    await load()
    newTitle.value=''; newDeadline.value=''
  }catch(e){
    alert('Create task failed: ' + (e?.response?.data?.detail || e.message))
  }finally{
    creating.value = false
  }
}

async function save(t){
  try{
    const payload = { 
      title: t.title, description: t.description || null, status: t.status || 'todo',
      color: t.color || null, order_index: t.order_index || 0, deadline: t.deadline || null
    }
    await api.put(`/api/tasks/${t.id}`, payload)
    await load()
    try{ dlg.value.close() }catch{}
  }catch(e){
    alert('Save failed: ' + (e?.response?.data?.detail || e.message))
  }
}

async function removeTask(t){
  if(!confirm('Delete this task?')) return
  try{
    await api.delete(`/api/tasks/${t.id}`)
    tasks.value = tasks.value.filter(x=>x.id !== t.id)
  }catch(e){
    alert('Delete failed: ' + (e?.response?.data?.detail || e.message))
  }
}

onMounted(load)
</script>

<style scoped>
.card{background:#fff;border:1px solid #e5e7eb;border-radius:14px}
.input{border:1px solid #e5e7eb;border-radius:10px;padding:.45rem .6rem;background:#fff}
.btn{border:1px solid #e5e7eb;border-radius:10px;padding:.5rem .9rem;background:#fff}
.btn-primary{background:#2563eb;color:#fff;border-color:transparent}
.modal::backdrop{background:rgba(0,0,0,.25)}
</style>
