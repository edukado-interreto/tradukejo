<script setup lang="ts">
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"

import TranslationRow from "./TranslationRow.vue"
import DeletedString from "./DeletedString.vue"

const props = defineProps<{ strings: TrString[] }>()

const AddString = defineAsyncComponent(() => import("./AddString.vue"))
const LoadMoreStrings = defineAsyncComponent(() => import("./LoadMoreStrings.vue"))

const store = useStore()
const canLoadMore = computed(() => store.canLoadMore)

const { editMode } = useTranslation()
</script>

<template>
  <AddString v-if="editMode" />

  <Transition v-for="string in strings" :key="string.id" name="fade" mode="out-in">
    <TranslationRow v-if="!string.deleted" :string="string" />
    <DeletedString v-else :string="string" />
  </Transition>

  <LoadMoreStrings v-if="canLoadMore" />
</template>

<style scoped>
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scaleY(0);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: scaleY(1);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s;
}
</style>
