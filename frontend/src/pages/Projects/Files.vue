
<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import api from '../../api'
import { File as IFile, FileText, FileSpreadsheet, FileImage, FileArchive, FileAudio, FileVideo, FileCode, Folder as IFolder, FolderOpen, ChevronRight, ChevronDown, History, Download, Upload, Trash2, Edit, RotateCcw } from 'lucide-vue-next'

const props = defineProps({ projectId: { type: Number, required: true } })

const folders = ref([])            // [{id,name,path,parent_id}]
const expanded = ref(new Set())    // set of path
const currentFolder = ref('')      // '' = root
const files = ref([])
const inRecycle = ref(false)
const crumbs = computed(()=>{
  if(inRecycle.value) return [{label:'Recycle Bin', path:null}]
  const parts = (currentFolder.value||'').split('/').filter(Boolean)
  const acc=[]; let p=''
  acc.push({label:'Root', path:''})
  for(const part of parts){ p = p ? p + '/' + part : part; acc.push({label:part, path:p}) }
  return acc
})              // [{id,name,revision_no,size_bytes,content_type,folder}]
const newFolderName = ref('')
const renameFolderId = ref(null)
const renameText = ref('')

const replacingFileId = ref(null)
const showVersionsFor = ref(null)
const versions = ref([])
const editingFileId = ref(null)
const editingFileName = ref('')
const showPermForFolderId = ref(null)
const permRows = ref([])
const showMoveFor = ref(null)
const moveTargetPath = ref('')
const uploadInput = ref(null)

function isExpanded(path){ return expanded.value.has(path) }
function toggleExpand(path){ if(expanded.value.has(path)) expanded.value.delete(path); else expanded.value.add(path) }

async function loadFolders(){
  const { data } = await api.get(`/api/files/projects/${props.projectId}/folders`)
  folders.value = data || []
}

async function loadFiles(){
  if (inRecycle.value){
    const { data } = await api.get(`/api/files/projects/${props.projectId}/items-deleted`)
    files.value = data || []
    return
  }
  const params = {}
  if (currentFolder.value) params.folder = currentFolder.value
  const { data } = await api.get(`/api/files/projects/${props.projectId}/items`, { params })
  files.value = data || []
}

onMounted(async () => { await loadFolders(); await loadFiles() })
watch(() => props.projectId, async () => { await loadFolders(); await loadFiles() })

const tree = computed(() => {
  // Build a simple flat tree for rendering
  const byParent = new Map()
  for(const f of folders.value){
    const key = f.parent_id ?? null
    if(!byParent.has(key)) byParent.set(key, [])
    byParent.get(key).push(f)
  }
  for(const arr of byParent.values()) arr.sort((a,b)=> a.name.localeCompare(b.name))
  const out = []
  function dfs(pid, depth){
    const arr = byParent.get(pid ?? null) || []
    for(const f of arr){
      out.push({...f, __depth: depth})
      dfs(f.id, depth+1)
    }
  }
  dfs(null, 0)
  return out
})

async function createFolder(parent_id = null){
  const name = (newFolderName.value || '').trim()
  if(!name) return
  const fd = new FormData()
  fd.append('name', name)
  if (parent_id !== null && parent_id !== undefined) fd.append('parent_id', String(parent_id))
  await api.post(`/api/files/projects/${props.projectId}/folders`, fd)
  newFolderName.value = ''
  await loadFolders(); await loadFiles()
}

function selectFolder(path){ inRecycle.value=false; currentFolder.value = path || ''; loadFiles() }

// Rename / move folder (from UI context for now rename inline on left)
function startRename(f){ renameFolderId.value = f.id; renameText.value = f.name; nextTick(()=>{ const el = document.getElementById('rename-folder-'+f.id); if(el) el.focus() }) }
async function saveRename(f){
  if(renameFolderId.value !== f.id) return
  const name = (renameText.value || '').trim()
  renameFolderId.value = null
  if(!name || name === f.name) return
  (()=>{ const fd=new FormData(); fd.append('name', name); return api.patch(`/api/files/folders/${f.id}`, fd) })()
  await loadFolders()
  await loadFiles()
}

// DnD folder move
const draggingFolderId = ref(null)
function onFolderDragStart(f){ draggingFolderId.value = f.id }
async function onFolderDrop(target){
  if(draggingFolderId.value == null) return
  if(target && target.id === draggingFolderId.value) { draggingFolderId.value = null; return }
  const parent_id = target ? target.id : null
  (()=>{ const fd=new FormData(); if(parent_id!==null&&parent_id!==undefined) fd.append('parent_id', String(parent_id)); return api.patch(`/api/files/folders/${draggingFolderId.value}`, fd) })()
  draggingFolderId.value = null
  await loadFolders()
  await loadFiles()
}

// DnD files: move to folder
async function onDropFilesToFolder(ev, folder){
  ev.preventDefault()
  // Handle native files
  if (ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files.length){
    await uploadFiles(ev.dataTransfer.files, folder?.path || '')
    return
  }
  // Handle app-internal drag (moving files)
  const payload = ev.dataTransfer.getData('text/x-file-id')
  if(payload){
    const id = Number(payload)
    await api.patch(`/api/files/items/${id}`, { folder: folder?.path || null })
    await loadFiles()
  }
}

function onDragOver(ev){ ev.preventDefault() }

// Drag from file list

function iconForFile(name, type){
  const ext = (name.split('.').pop() || '').toLowerCase()
  if(['png','jpg','jpeg','gif','bmp','svg','webp','tiff'].includes(ext)) return 'image'
  if(['pdf'].includes(ext)) return 'text'
  if(['doc','docx','rtf','odt','txt','md'].includes(ext)) return 'text'
  if(['xls','xlsx','csv','ods'].includes(ext)) return 'sheet'
  if(['zip','rar','7z','gz','tar'].includes(ext)) return 'archive'
  if(['mp3','wav','ogg','m4a','flac'].includes(ext)) return 'audio'
  if(['mp4','mov','avi','mkv','webm'].includes(ext)) return 'video'
  if(['js','ts','json','xml','yml','yaml','html','css','scss','py','rb','go','java','cs','cpp','c','php','sql'].includes(ext)) return 'code'
  return 'file'
}

async function downloadFile(file, version = null){
  const url = `/api/files/items/${file.id}/download` + (version? `?version=${version}` : '')
  const res = await api.get(url, { responseType: 'blob' })
  const blob = res.data
  const a = document.createElement('a')
  const href = URL.createObjectURL(blob)
  a.href = href
  const rev = version ? `.rev${version}` : ''
  a.download = file.name
  document.body.appendChild(a); a.click(); a.remove()
  URL.revokeObjectURL(href)
}

function onFileDragStart(file, ev){
  ev.dataTransfer.setData('text/x-file-id', String(file.id))
}

async function uploadFiles(fileList, folderPath){
  for(const f of fileList){
    const form = new FormData()
    form.append('file', f)
    if(folderPath) form.append('folder', folderPath)
    await api.post(`/api/files/projects/${props.projectId}/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
  }
  await loadFiles()
}

function triggerUpload(){ replacingFileId.value = null; uploadInput.value?.click() }
function triggerReplace(file){ replacingFileId.value = file.id; uploadInput.value?.click() }

async function onChooseUpload(e){
  const fl = e.target.files

  if(!fl || !fl.length) {
    return
  }
  if(replacingFileId.value){
    const form = new FormData()
    form.append('file', fl[0])
    form.append('replace_file_id', String(replacingFileId.value))
    await api.post(`/api/files/projects/${props.projectId}/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
    replacingFileId.value = null
    uploadInput.value.value = ''
    await loadFiles()
  }else{
    await uploadFiles(fl, currentFolder.value || '')
    uploadInput.value.value = ''
  }
}

async function openVersions(file){
  showVersionsFor.value = file
  const { data } = await api.get(`/api/files/items/${file.id}/versions`)
  versions.value = data || []
}
async function restoreVersion(file, rev){


function startRename(file){
  editingFileId.value = file.id
  editingFileName.value = file.name
  nextTick(()=>{ const el = document.getElementById('edit-file-name-'+file.id); if(el) el.focus() })
}
async function saveRename(file){
  if (editingFileId.value !== file.id) return
  const name = (editingFileName.value||'').trim()
  editingFileId.value = null
  if(!name || name === file.name) return
  const fd = new FormData(); fd.append('name', name)
  await api.patch(`/api/files/items/${file.id}`, fd)
  await loadFiles()
}

async function trashFile(file){
  await api.post(`/api/files/items/${file.id}/trash`)
  await loadFiles()
}
async function restoreDeleted(file){
  await api.post(`/api/files/items/${file.id}/restore-deleted`)
  await loadFiles()
}

async function openPerm(){
  const f = folders.value.find(x=>x.path===currentFolder.value)
  if(!f){ return }
  showPermForFolderId.value = f.id
  const { data } = await api.get(`/api/files/folders/${f.id}/permissions`)
  permRows.value = data || []
}
async function setPerm(row){
  const fd = new FormData(); fd.append('user_id', String(row.user_id)); fd.append('can_read', row.can_read ? '1':'0'); fd.append('can_write', row.can_write ? '1':'0')
  await api.post(`/api/files/folders/${showPermForFolderId.value}/permissions`, fd)
}

function openMove(item){ showMoveFor.value = item; moveTargetPath.value = currentFolder.value || '' }
async function confirmMove(){
  const item = showMoveFor.value
  if(!item) return
  if(item.folder_path !== undefined){
    // file
    const fd = new FormData(); if(moveTargetPath.value) fd.append('folder', moveTargetPath.value); else fd.append('folder','')
    await api.patch(`/api/files/items/${item.id}`, fd)
  } else {
    // folders moved by drag already; optional future support
  }
  showMoveFor.value = null
  await loadFolders(); await loadFiles()
}
  await api.post(`/api/files/items/${file.id}/restore-deleted`)
  await loadFiles()
}

</script>

<template>
  <div class="grid grid-cols-12 gap-5">
    <!-- Sidebar -->
    <aside class="col-span-3">
      <div class="border rounded-lg bg-white shadow-sm">
        <div class="px-3 py-2 border-b flex items-center justify-between">
          <h3 class="font-semibold">Folders</h3>
          <button class="text-xs text-gray-600 hover:text-black flex items-center gap-1" @click="inRecycle=true; currentFolder=''; loadFiles()">
            <Trash2 class="inline w-4 h-4" /> <span>Bin</span>
          </button>
        </div>
        <div class="p-3">
          <div class="flex gap-2 mb-2">
            <input v-model="newFolderName" placeholder="New folder name" class="border rounded px-2 py-1 flex-1" />
            <button class="px-3 py-1 rounded bg-black text-white hover:bg-gray-800" @click="createFolder(null)">Add</button>
          </div>
          <div class="text-xs text-gray-500 mb-2">Drag folders to move. Drop files on a folder to move.</div>
          <ul @dragover.prevent @drop="onFolderDrop(null)">
            <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center mb-1"
                @click="inRecycle=true; currentFolder=''; loadFiles()">
              <Trash2 class="inline w-4 h-4 mr-2" /><span>Recycle Bin</span>
            </li>
            <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
                :class="{'font-semibold': currentFolder=='' && !inRecycle}" @click="selectFolder('')">
              <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
            </li>
            <li v-for="f in tree" :key="f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
                :style="{ paddingLeft: (f.__depth*14) + 'px' }"
                draggable="true" @dragstart="onFolderDragStart(f)"
                @dragover.prevent @drop="onFolderDrop(f)"
                @click="selectFolder(f.path)"
                :class="{'font-semibold': currentFolder===f.path && !inRecycle}">
              <component :is="isExpanded(f.path) ? ChevronDown : ChevronRight" class="inline w-4 h-4 mr-1" />
              <component :is="isExpanded(f.path) ? FolderOpen : IFolder" class="inline w-4 h-4 mr-2" />
              <template v-if="renameFolderId===f.id">
                <input :id="'rename-folder-'+f.id" v-model="renameText" @keyup.enter="saveRename(f)" @blur="saveRename(f)" class="border rounded px-1 py-0.5 text-sm flex-1" />
              
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
              <template v-else>
                <span class="truncate" @dblclick.stop="startRename(f)">{{ f.name }}</span>
              
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
            </li>
          </ul>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <section class="col-span-9">
      <div class="border rounded-lg bg-white shadow-sm">
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <div class="flex items-center gap-2 text-sm">
            <template v-if="inRecycle">
              <Trash2 class="inline w-4 h-4" /> <span class="font-medium">Recycle Bin</span>
            
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
            <template v-else>
              <nav class="flex items-center gap-1">
                <template v-for="(c,i) in crumbs" :key="i">
                  <template v-if="i>0"><span class="text-gray-400">/</span>
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
                  <a href="#" @click.prevent="selectFolder(c.path)" class="hover:underline">{{ c.label }}</a>
                
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
              </nav>
            
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
          </div>
          <div class="flex gap-2">
            <button class="px-3 py-1.5 rounded border hover:bg-gray-50" @click="openPerm" v-if="!inRecycle">Permissions</button>
            <input type="file" ref="uploadInput" class="hidden" @change="onChooseUpload" />
            <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800 disabled:opacity-50" @click="triggerUpload" :disabled="inRecycle">
              <Upload class="inline w-4 h-4 mr-1" /> Upload
            </button>
          </div>
        </div>

        <div class="overflow-hidden">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left p-2 w-8"></th>
                <th class="text-left p-2">Name</th>
                <th class="text-left p-2 w-24">Revision</th>
                <th class="text-left p-2 w-32">Size</th>
                <th class="text-left p-2 w-64">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in files" :key="f.id" class="border-t hover:bg-gray-50" draggable="true" @dragstart="(e)=>onFileDragStart(f, e)">
                <td class="p-2 w-8">
                  <component :is="{image: FileImage, text: FileText, sheet: FileSpreadsheet, archive: FileArchive, audio: FileAudio, video: FileVideo, code: FileCode, file: IFile}[iconForFile(f.name, f.content_type)]" class="inline w-4 h-4" />
                </td>
                <td class="p-2">
                  <template v-if="editingFileId===f.id">
                    <input :id="'edit-file-name-'+f.id" v-model="editingFileName" @keyup.enter="saveRename(f)" @blur="saveRename(f)" class="border rounded px-2 py-1 w-full" />
                  
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
                  <template v-else>
                    <span @dblclick="startRename(f)" class="truncate inline-block max-w-[480px] align-middle">{{ f.name }}</span>
                  
  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
                </td>
                <td class="p-2">Rev {{ f.revision_no }}</td>
                <td class="p-2">{{ (f.size_bytes||0).toLocaleString() }} B</td>
                <td class="p-2">
                  <div class="flex items-center gap-2">
                    <button class="border rounded px-2 py-1" @click="triggerReplace(f)" v-if="!inRecycle"><Upload class="inline w-4 h-4 mr-1" />Replace</button>
                    <button class="border rounded px-2 py-1" @click="openVersions(f)"><History class="inline w-4 h-4 mr-1" />Versions</button>
                    <button class="border rounded px-2 py-1" @click="downloadFile(f)"><Download class="inline w-4 h-4 mr-1" />Download</button>
                    <button class="border rounded px-2 py-1 text-red-600" @click="trashFile(f)" v-if="!inRecycle"><Trash2 class="inline w-4 h-4 mr-1" />Delete</button>
                    <button class="border rounded px-2 py-1" @click="restoreDeleted(f)" v-else><RotateCcw class="inline w-4 h-4 mr-1" />Restore</button>
                    <button class="border rounded px-2 py-1" @click="openMove(f)" v-if="!inRecycle">Move&nbsp;to…</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!files.length">
                <td colspan="5" class="p-10 text-center text-gray-500">No files yet</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="px-4 py-3 text-xs text-gray-500 border-t bg-gray-50">Tip: drag a file row and drop it on a folder on the left to move it.</div>
      </div>
    </section>
  </div>

  <!-- Versions modal -->
  <div v-if="showVersionsFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showVersionsFor=null">
    <div class="bg-white rounded shadow p-4 w-[600px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Versions — {{ showVersionsFor?.name }}</h3>
        <button class="text-xl" @click="showVersionsFor=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">Revision</th><th class="text-left p-2">Uploaded</th><th class="text-left p-2">Size</th><th class="text-left p-2">Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="v in versions" :key="v.revision_no" class="border-t">
            <td class="p-2">Rev {{ v.revision_no }}</td>
            <td class="p-2">{{ v.uploaded_at }}</td>
            <td class="p-2">{{ (v.size_bytes||0).toLocaleString() }} B</td>
            <td class="p-2">
              <button class="border rounded px-2 py-1 mr-2" @click="downloadFile(showVersionsFor, v.revision_no)">Download</button>
              <button class="border rounded px-2 py-1" @click="restoreVersion(showVersionsFor, v.revision_no)">Restore</button>
            </td>
          </tr>
          <tr v-if="!versions.length"><td colspan="4" class="p-6 text-center text-gray-500">No versions</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Permissions modal -->
  <div v-if="showPermForFolderId" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showPermForFolderId=null">
    <div class="bg-white rounded shadow p-4 w-[640px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Folder permissions</h3>
        <button class="text-xl" @click="showPermForFolderId=null">×</button>
      </div>
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr><th class="text-left p-2">User</th><th class="text-left p-2">Email</th><th class="text-left p-2 w-24">Read</th><th class="text-left p-2 w-24">Write</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in permRows" :key="r.user_id" class="border-t">
            <td class="p-2">{{ r.name }}</td>
            <td class="p-2">{{ r.email }}</td>
            <td class="p-2"><input type="checkbox" v-model="r.can_read" @change="setPerm(r)" /></td>
            <td class="p-2"><input type="checkbox" v-model="r.can_write" @change="setPerm(r)" /></td>
          </tr>
        </tbody>
      </table>
      <div class="text-xs text-gray-500 mt-3">Note: when any permissions are defined for this project, access is granted only if a user has permission on the folder or one of its ancestors. Admins bypass.</div>
    </div>
  </div>

  <!-- Move to modal -->
  <div v-if="showMoveFor" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showMoveFor=null">
    <div class="bg-white rounded shadow p-4 w-[520px] max-h-[70vh] overflow-auto">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold">Move to…</h3>
        <button class="text-xl" @click="showMoveFor=null">×</button>
      </div>
      <div class="mb-3 text-sm text-gray-600">Choose destination folder:</div>
      <ul class="border rounded p-2 max-h-[40vh] overflow-auto">
        <li class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :class="{'font-semibold': moveTargetPath==''}" @click="moveTargetPath=''">
          <IFolder class="inline w-4 h-4 mr-2" /> <span>Root</span>
        </li>
        <li v-for="f in tree" :key="'mv-'+f.id" class="px-2 py-1 rounded hover:bg-black/5 cursor-pointer flex items-center"
            :style="{ paddingLeft: (f.__depth*14) + 'px' }"
            @click="moveTargetPath=f.path">
          <component :is="ChevronRight" class="inline w-4 h-4 mr-1 opacity-0" />
          <component :is="IFolder" class="inline w-4 h-4 mr-2" />
          <span class="truncate">{{ f.name }}</span>
        </li>
      </ul>
      <div class="mt-3 flex justify-end gap-2">
        <button class="px-3 py-1.5 rounded border" @click="showMoveFor=null">Cancel</button>
        <button class="px-3 py-1.5 rounded bg-black text-white hover:bg-gray-800" @click="confirmMove">Move here</button>
      </div>
    </div>
  </div>

</template>
