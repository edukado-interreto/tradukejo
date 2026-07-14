<script setup lang="ts">
import { useTranslation } from "@/composables/useTranslation"

type NodeData = {
  children: Record<string, NodeData>
  strings: { count: number; words: number }
  strings_in_children: { count: number; words: number }
}

type Props = {
  node: NodeData
  nodeName?: string
  first?: boolean
  parentPath?: string
}

const props = withDefaults(defineProps<Props>(), { nodeName: "", parentPath: "" })

const { translateLink, queryStringDir } = useTranslation()

const open = ref(props.first)

const name = computed(() => (props.first ? "navigation.all" : props.nodeName))

const path = computed(() => {
  return props.first || props.parentPath === ""
    ? props.nodeName
    : `${props.parentPath}/${props.nodeName}`
})

const hasChildren = computed(() => Object.keys(props.node.children).length > 0)

const active = computed(() => {
  return queryStringDir.value === path.value || (props.first && !queryStringDir.value)
})

const folderOpen = computed(() => (open.value && hasChildren.value) || active.value)

const title = computed(() => (hasChildren.value ? "navigation.count_children" : "navigation.count"))

const titleParams = computed(() => ({
  strings: props.node.strings.count,
  strings2: props.node.strings_in_children.count,
  words: props.node.strings.words,
  words2: props.node.strings_in_children.words,
}))

const toggle = () => {
  open.value = !open.value
}

watch(active, (isNowActive) => {
  if (isNowActive) open.value = true
})

onMounted(() => {
  if (props.first || active.value || queryStringDir.value.startsWith(`${path.value}/`)) {
    open.value = true
  }
})
</script>

<template>
  <li :class="{ first }">
    <span v-if="hasChildren" @click="toggle" :class="{ open }">
      <i class="fas fa-angle-right" />
    </span>

    <span class="folder" :class="{ 'has-children': hasChildren, closed: !folderOpen }">
      <i :class="['fas', folderOpen ? 'fa-folder-open mr-1' : 'fa-folder mr-1']" />
    </span>

    <RouterLink
      :to="translateLink({ dir: path })"
      :class="{ active }"
      :title="$t(title, titleParams)"
    >
      {{ first ? $t(name) : name }}
      ({{ node.strings.count + node.strings_in_children.count }})
    </RouterLink>

    <Transition name="slide">
      <ul v-if="hasChildren && open">
        <DirectoryNode
          v-for="(child, childName) in node.children"
          :key="childName"
          :node="child"
          :node-name="String(childName)"
          :parent-path="path"
        />
      </ul>
    </Transition>
  </li>
</template>

<style lang="scss" scoped>
ul {
  padding-left: 9px;
  margin: 1px 0 1px 4px;
  list-style-type: none;
  border-left: 1px solid #999;
}

a {
  padding-left: 2px;
  &.active {
    font-weight: bold;
    background: #007bff;
    color: white;
    padding: 2px 4px;
    margin: 1px 0;
    border-radius: 6px;
    font-size: 0.9rem;
    &:hover {
      background: #0056b3;
      text-decoration: none;
    }
  }
}

li.first > a::before {
  display: none;
}

.fa-angle-right {
  margin-right: 4px;
  position: relative;
  top: 1px;
  transition: transform 0.2s;
  cursor: pointer;
}

.open .fa-angle-right {
  transform: rotate(90deg);
}

.folder {
  margin-left: 14px;
  &.closed {
    margin-right: 2px;
  }
  &.has-children {
    margin-left: 2px;
  }
}
</style>
