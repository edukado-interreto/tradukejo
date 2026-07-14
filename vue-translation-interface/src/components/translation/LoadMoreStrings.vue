<script setup lang="ts">
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"

const store = useStore()
const { queryStringDir, queryStringQ, queryStringState, queryStringSort } = useTranslation()

const loading = ref(false)

const loadMore = async () => {
  loading.value = true
  try {
    await store.loadMore({
      dir: queryStringDir.value,
      q: queryStringQ.value,
      state: queryStringState.value,
      sort: queryStringSort.value,
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <LoadingSpinner v-if="loading" />
  <div v-else class="text-center">
    <button class="btn btn-primary btn-lg" @click="loadMore">
      {{ $t("load_more") }}
    </button>
  </div>
</template>
