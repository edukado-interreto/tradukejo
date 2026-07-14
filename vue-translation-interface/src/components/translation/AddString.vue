<script setup lang="ts">
import { useRouter } from "vue-router"
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"
import TranslateForm from "./translatingTo/TranslateForm.vue"

const router = useRouter()
const store = useStore()

const { queryStringDir, translateLink, fetchDirectoriesTree } = useTranslation()

const editing = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)

provide("stringId", "add")

const showForm = () => {
  editing.value = true
}

const hideForm = () => {
  editing.value = false
  error.value = null
}

const saveString = async (data: any) => {
  loading.value = true
  error.value = null

  try {
    const response = await store.addString(data)

    hideForm()
    await fetchDirectoriesTree()

    setTimeout(() => {
      if (response.path !== queryStringDir.value) {
        router.push(translateLink({ dir: response.path }))
      }
    }, 200)
  } catch (e: any) {
    console.error(e)
    error.value = e.message || "An error occurred"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Transition name="slide">
    <div v-if="editing" class="card">
      <div class="card-body">
        <h5 class="card-title">{{ $t("translate.add_string") }}</h5>
        <TranslateForm
          :path="queryStringDir"
          :error="error"
          :loading="loading"
          :new-string="true"
          @cancel="hideForm"
          @save-translation="saveString"
        />
      </div>
    </div>
  </Transition>

  <div v-if="!editing" class="text-center mb-4">
    <button class="btn btn-primary" @click="showForm">
      {{ $t("translate.add_string") }}
    </button>
  </div>
</template>

<style scoped>
.card {
  max-width: 800px;
  margin: 0 auto 1rem auto;
}

.card-body {
  padding-bottom: 0;
}

/* Ensure you have the slide transition defined in your global CSS or here */
.slide-enter-active,
.slide-leave-active {
  transition:
    transform 0.3s ease,
    opacity 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
