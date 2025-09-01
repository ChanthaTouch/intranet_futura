
<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import api from '../../api'

const props = defineProps({ projectId: { type: Number, required: true } })

const items = ref([])
const form = ref({ title: '', planned_start: '', planned_end: '' })
const loading = ref(false)

// inline title editing (single active editor)
const editingId = ref(null)
const editingVal = ref('')

function startEdit(item) {
  editingId.value = item.id
  editingVal.value = item.title
  nextTick(() => {
    const el = document.getElementById('edit-title-' + item.id)
    if (el) el.focus()
  })
}
async function saveEdit(item) {
  if (editingId.value !== item.id) return
  const newTitle = editingVal.value.trim()
  editingId.value = null
  if (!newTitle || newTitle === item.title) return
  await patchItem(item.id, { title: newTitle })
}

// ------- data load -------
async function load(retry = 0) {
  loading.value = true
  try {
    const { data } = await api.get(`/api/schedule/projects/${props.projectId}/items`, { params: { _ts: Date.now() } })
    const arr = Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : [])
    items.value = arr.filter(Boolean).map(it => ({
      ...it,
      id: Number(it.id),
      parent_id: (it.parent_id === undefined || it.parent_id === null) ? null : Number(it.parent_id),
      sort_index: Number(it.sort_index ?? 0)
    }))
  } catch (err) {
    console.error('Failed to load schedule items', err)
    if (retry < 2) setTimeout(() => load(retry + 1), 250)
  } finally {
    loading.value = false
  }
}

async function addItem() {
  if (!form.value.title?.trim()) return
  await api.post(`/api/schedule/projects/${props.projectId}/items`, {
    title: form.value.title.trim(),
    planned_start: form.value.planned_start || null,
    planned_end: form.value.planned_end || null,
  })
  form.value = { title: '', planned_start: '', planned_end: '' }
  await load()
}


async function deleteItem(id) {
  if (!confirm('Delete this task and all of its sub-items?')) return
  await api.delete(`/api/schedule/items/${id}`)
  await load()
}


// ---- move helpers ----
function siblingsOf(item) {
  const pid = item.parent_id ?? null
  const list = childrenOf(pid).slice()
  list.sort((a,b)=> (a.sort_index||0)-(b.sort_index||0) || a.id-b.id)
  return list
}

async function reorderWithinParent(parentId, orderedIds) {
  await api.post('/api/schedule/items/reorder', {
    contract_id: props.projectId,
    parent_id: parentId ?? null,
    item_ids_in_order: orderedIds
  })
  await load()
}

async function moveUp(item) {
  const sibs = siblingsOf(item)
  const idx = sibs.findIndex(x => x.id === item.id)
  if (idx <= 0) return
  const order = sibs.map(x=>x.id)
  ;[order[idx-1], order[idx]] = [order[idx], order[idx-1]]
  await reorderWithinParent(item.parent_id ?? null, order)
}

async function moveDown(item) {
  const sibs = siblingsOf(item)
  const idx = sibs.findIndex(x => x.id === item.id)
  if (idx === -1 || idx >= sibs.length-1) return
  const order = sibs.map(x=>x.id)
  ;[order[idx], order[idx+1]] = [order[idx+1], order[idx]]
  await reorderWithinParent(item.parent_id ?? null, order)
}

function indexInRows(id) {
  return rows.value.findIndex(r => r.id === id)
}

async function indent(item) {
  const idx = indexInRows(item.id)
  if (idx <= 0) return
  const prev = rows.value[idx-1]
  if (!prev) return
  await patchItem(item.id, { parent_id: prev.id })
}

async function outdent(item) {
  const parent = items.value.find(x => x.id === (item.parent_id ?? null))
  if (!parent) return
  await patchItem(item.id, { parent_id: parent.parent_id ?? null })
}

// existing patchItem
async function patchItem(id, patch) {


  await api.patch(`/api/schedule/items/${id}`, patch)
  await load()
}

function daysBetween(a, b) {
  if (!a || !b) return ''
  const A = new Date(a), B = new Date(b)
  const ms = (B - A) / (1000*60*60*24)
  return Math.max(0, Math.round(ms) + 1)
}

// ---- left list drag/drop + tree flattening -----
const dragId = ref(null)
function onDragStart(id) { dragId.value = id }

function isDescendant(potentialParentId, nodeId) {
  // walk up from potentialParentId to root; if we hit nodeId, then invalid
  let current = potentialParentId
  const lookup = new Map(items.value.map(it => [it.id, it]))
  while (current != null) {
    if (current === nodeId) return true
    const n = lookup.get(current)
    current = n ? n.parent_id : null
  }
  return false
}

async function onDropNewParent(newParentId) {
  if (dragId.value == null) return
  if (dragId.value === newParentId) { dragId.value = null; return }
  if (newParentId != null && isDescendant(newParentId, dragId.value)) { dragId.value = null; return }
  await patchItem(dragId.value, { parent_id: newParentId ?? null })
  dragId.value = null
}

const byParent = computed(() => {
  const m = new Map()
  for (const it of items.value) {
    const key = it.parent_id ?? null
    if (!m.has(key)) m.set(key, [])
    m.get(key).push(it)
  }
  for (const arr of m.values()) {
    arr.sort((a,b)=> (a.sort_index||0)-(b.sort_index||0) || a.id-b.id)
  }
  return m
})

function childrenOf(pid) {
  return byParent.value.get(pid ?? null) || []
}

const rows = computed(() => {
  const out = []
  const visited = new Set()
  function dfs(pid, depth) {
    const arr = childrenOf(pid)
    for (const it of arr) {
      if (visited.has(it.id)) continue
      visited.add(it.id)
      out.push({ ...it, __indent: depth })
      dfs(it.id, depth+1)
    }
  }
  dfs(null, 0)
  // include any orphans to avoid items disappearing
  for (const it of items.value) {
    if (!visited.has(it.id)) out.push({ ...it, __indent: 0 })
  }
  return out
})
// ----------------------------

// ----- Gantt helpers -----
const pxPerDay = 8
const gScrollLeft = ref(0)
const ganttHeaderRef = ref(null)
function onGanttScroll(e){ gScrollLeft.value = e.target.scrollLeft }
const rowHeight = 40

function parseDate(s) { return s ? new Date(s + 'T00:00:00') : null }
function fmt(d) {
  if (!d) return null
  const y = d.getFullYear()
  const m = String(d.getMonth()+1).padStart(2,'0')
  const da = String(d.getDate()).padStart(2,'0')
  return `${y}-${m}-${da}`
}

const minDate = computed(() => {
  const ds = rows.value.map(r => parseDate(r.planned_start)).filter(Boolean)
  if (!ds.length) return new Date(Date.now())
  const d = new Date(Math.min(...ds.map(d=>d.getTime())))
  d.setDate(d.getDate()-3) // small pad
  return d
})
const maxDate = computed(() => {
  const ds = rows.value.map(r => parseDate(r.planned_end)).filter(Boolean)
  if (!ds.length) { const t = new Date(Date.now()); t.setDate(t.getDate()+30); return t }
  const d = new Date(Math.max(...ds.map(d=>d.getTime())))
  d.setDate(d.getDate()+3)
  return d
})

function diffDays(a,b) {
  const dt = Math.round((b.getTime()-a.getTime())/(1000*60*60*24))
  return dt
}

const timelineDays = computed(() => Math.max(1, diffDays(minDate.value, maxDate.value)))
const timelineWidth = computed(() => timelineDays.value * pxPerDay)

function xForDate(d) { return diffDays(minDate.value, d) * pxPerDay }
function dateForX(x) {
  const days = Math.round(x / pxPerDay)
  const d = new Date(minDate.value.getTime())
  d.setDate(d.getDate() + days)
  return d
}

// weekly ticks
const weekTicks = computed(() => {
  const arr = []
  const d = new Date(minDate.value.getTime())
  let idx = 0
  while (d <= maxDate.value) {
    arr.push({ when: new Date(d.getTime()), label: 'W' + (idx+1) })
    d.setDate(d.getDate()+7); idx++
  }
  return arr
})

// drag/resize bars
const dragState = ref(null) // { id, mode: 'drag'|'resize-l'|'resize-r', startX, origStart, origEnd }

function onBarMouseDown(e, row) {
  const s = parseDate(row.planned_start)
  const en = parseDate(row.planned_end)
  if (!s || !en) return

  const left = xForDate(s)
  const right = xForDate(en) + pxPerDay // inclusive
  const x = e.offsetX

  let mode = 'drag'
  const edge = 6
  if (Math.abs(x - 0) < edge || Math.abs(x - left) < edge) mode = 'resize-l'
  else if (Math.abs(x - (right - left)) < edge) mode = 'resize-r'

  dragState.value = {
    id: row.id,
    mode,
    startX: e.clientX,
    origStart: s,
    origEnd: en,
  }
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp, { once: true })
}

async function onMouseUp() {
  if (!dragState.value) return
  const ds = dragState.value
  window.removeEventListener('mousemove', onMouseMove)
  const row = rows.value.find(r => r.id === ds.id)
  if (row) {
    // persist
    await patchItem(row.id, { planned_start: row.planned_start, planned_end: row.planned_end })
  }
  dragState.value = null
}

function onMouseMove(e) {
  const ds = dragState.value
  if (!ds) return
  const dx = e.clientX - ds.startX
  const deltaDays = Math.round(dx / pxPerDay)
  const row = rows.value.find(r => r.id === ds.id)
  if (!row) return

  if (ds.mode === 'drag') {
    const ns = new Date(ds.origStart.getTime()); ns.setDate(ns.getDate() + deltaDays)
    const ne = new Date(ds.origEnd.getTime()); ne.setDate(ne.getDate() + deltaDays)
    row.planned_start = fmt(ns); row.planned_end = fmt(ne)
  } else if (ds.mode === 'resize-l') {
    const ns = new Date(ds.origStart.getTime()); ns.setDate(ns.getDate() + deltaDays)
    if (ns <= ds.origEnd) row.planned_start = fmt(ns)
  } else if (ds.mode === 'resize-r') {
    const ne = new Date(ds.origEnd.getTime()); ne.setDate(ne.getDate() + deltaDays)
    if (ds.origStart <= ne) row.planned_end = fmt(ne)
  }
}
// ----------------------------

onMounted(load)
watch(() => props.projectId, () => load(), { immediate: true })
</script>

<template>
  <div class="space-y-3">
    <div class="grid grid-cols-12 gap-3 items-end">
      <div class="col-span-6">
        <label class="block text-sm font-medium mb-1">Title</label>
        <input v-model="form.title" class="w-full border rounded px-3 py-2" placeholder="Task name" />
      </div>
      <div class="col-span-2">
        <label class="block text-sm font-medium mb-1">Planned start</label>
        <input v-model="form.planned_start" type="date" class="border rounded px-3 py-2 w-full" />
      </div>
      <div class="col-span-2">
        <label class="block text-sm font-medium mb-1">Planned end</label>
        <input v-model="form.planned_end" type="date" class="border rounded px-3 py-2 w-full" />
      </div>
      <div class="col-span-2 flex">
        <button class="px-4 py-2 rounded border self-end w-full" @click="addItem">Add</button>
      </div>
    </div>

    <div class="grid grid-cols-12 gap-3">
      <!-- Left draggable tree -->
      <div class="col-span-3 border rounded p-3 h-[460px] overflow-auto"
           @dragover.prevent
           @drop="onDropNewParent(null)">
        <p class="text-sm text-gray-500 mb-2">Drag onto another to make a sub-item. Double-click to rename. Drop here to move to root.</p>
        <ul>
          <li v-for="r in rows" :key="'L-'+r.id"
              class="px-2 py-1 rounded hover:bg-black/5 cursor-move"
              draggable="true"
              @dragstart="onDragStart(r.id)"
              @dragover.prevent
              @drop="onDropNewParent(r.id)"
              :style="{ paddingLeft: (r.__indent*16) + 'px' }"
          >
            <template v-if="editingId === r.id">
              <input :id="'edit-title-'+r.id" v-model="editingVal" @keyup.enter="saveEdit(r)" @blur="saveEdit(r)" class="border rounded px-2 py-1 w-full" />
            </template>
            <template v-else>
              <span @dblclick="startEdit(r)">{{ r.title }}</span>
            </template>
          </li>
        </ul>
      </div>

      <!-- Right area: table + gantt -->
      <div class="col-span-9 border rounded overflow-hidden">
        <!-- Gantt header -->
        <div class="flex">
          <div class="w-[6%] border-b px-2 py-2 text-xs font-medium bg-gray-50">Move</div><div class="w-[20%] border-b px-2 py-2 text-xs font-medium bg-gray-50">Task</div>
          <div class="w-[12%] border-b px-2 py-2 text-xs font-medium bg-gray-50">Start</div>
          <div class="w-[12%] border-b px-2 py-2 text-xs font-medium bg-gray-50">End</div>
          <div class="w-[6%] border-b px-2 py-2 text-xs font-medium bg-gray-50">Days</div>
          <div class="flex-1 border-b bg-gray-50 overflow-x-auto" ref="ganttHeaderRef" @scroll="onGanttScroll">
            <div class="relative h-10" :style="{ width: timelineWidth + 'px' }">
              <template v-for="(w, idx) in weekTicks" :key="'T'+idx">
                <div class="absolute top-0 bottom-0 border-l" :style="{ left: xForDate(w.when)+'px' }"></div>
                <div class="absolute text-[10px] -translate-x-1/2 top-1" :style="{ left: xForDate(w.when)+'px' }">{{ w.label }}</div>
              </template>
            </div>
          </div>
        </div>

        <!-- Rows -->
        <div class="max-h-[420px] overflow-auto">
          <template v-for="(r, idx) in rows" :key="'R-'+r.id">
            <div class="flex items-stretch border-t" :style="{ height: rowHeight + 'px' }">
              <div class="w-[12%] px-2 flex items-center gap-1">
              <button class="text-xs px-1" @click.stop="moveUp(r)" title="Move up">↑</button>
              <button class="text-xs px-1" @click.stop="moveDown(r)" title="Move down">↓</button>
              <button class="text-xs px-1" @click.stop="indent(r)" title="Indent (make sub-item)">→</button>
              <button class="text-xs px-1" @click.stop="outdent(r)" title="Outdent">←</button>
            </div>
            <div class="w-[20%] px-2 flex items-center" :style="{ paddingLeft: (r.__indent*16) + 'px' }">
                <template v-if="editingId === r.id">
                  <input :id="'edit-title-'+r.id" v-model="editingVal" @keyup.enter="saveEdit(r)" @blur="saveEdit(r)" class="border rounded px-2 py-1 w-full" />
                </template>
                <template v-else>
                  <span @dblclick="startEdit(r)" class="whitespace-nowrap overflow-hidden text-ellipsis">{{ r.title }}</span>
                </template>
              </div>
              <div class="w-[12%] px-2 flex items-center">
                <input type="date" :value="r.planned_start || ''" @change="e=>patchItem(r.id,{planned_start:e.target.value||null})" class="border rounded px-2 py-1 w-full text-sm" />
              </div>
              <div class="w-[12%] px-2 flex items-center">
                <input type="date" :value="r.planned_end || ''" @change="e=>patchItem(r.id,{planned_end:e.target.value||null})" class="border rounded px-2 py-1 w-full text-sm" />
              </div>
              <div class="w-[6%] px-2 flex items-center justify-between"><span>{{ daysBetween(r.planned_start, r.planned_end) }}</span><button class="ml-2 text-red-600" title="Delete" @click.stop="deleteItem(r.id)">🗑</button></div>
              <div class="flex-1 relative overflow-hidden">
                <div class="relative" :style="{ width: timelineWidth + 'px', height: '100%', transform: 'translateX(-'+gScrollLeft+'px)'}">
                  <!-- background weekly grid -->
                  <template v-for="(w, idx) in weekTicks" :key="'G'+idx">
                    <div class="absolute top-0 bottom-0 border-l" :style="{ left: xForDate(w.when)+'px' }"></div>
                  </template>
                  <!-- bar -->
                  <template v-if="r.planned_start && r.planned_end">
                    <div class="absolute top-2 bottom-2 rounded cursor-ew-resize bg-blue-500/60 hover:bg-blue-600/70"
                         :style="{ left: xForDate(new Date(r.planned_start))+'px', width: (xForDate(new Date(r.planned_end)) - xForDate(new Date(r.planned_start)) + pxPerDay) + 'px' }"
                         @mousedown.prevent="(e)=>onBarMouseDown(e, r)">
                      <div class="absolute left-0 top-0 bottom-0 w-2 cursor-w-resize"></div>
                      <div class="absolute right-0 top-0 bottom-0 w-2 cursor-e-resize"></div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </template>

          <div v-if="!rows.length" class="p-6 text-center text-gray-500">
            {{ loading ? 'Loading…' : 'No tasks yet' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
