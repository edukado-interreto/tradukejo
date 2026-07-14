<script setup lang="ts">
import { useRouter } from "vue-router"
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"
import { useI18n } from "vue-i18n"

import StringInfo from "@/components/translation/bottom/StringInfo.vue"
import DisplayText from "@/components/translation/DisplayText.vue"
import TranslateForm from "./TranslateForm.vue"

const { string } = defineProps<{ string: TrString }>()

const store = useStore()
const router = useRouter()
const { t } = useI18n()
const { editMode, translateLink, fetchDirectoriesTree, queryStringState } = useTranslation()

const editing = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const translateBtn = ref<HTMLButtonElement | null>(null)

const STATE_FILTER_ALL = "all"

const currentIndex = computed(() => store.indexOfString(string.id) + 1)

const pluralized = computed(() => string.original_text.pluralized)

const texts = computed(() => (string.translated_text ? string.translated_text.raw_text : {}))

const specialTokens = computed<string[]>(() => {
  const originalTexts = Object.values(string.original_text.text)
  const tokens = originalTexts.flatMap((text) =>
    Array.from(text.matchAll(/<code>([^<]*?)<\/code>/g), (m) => m[1]),
  )
  return [...new Set(tokens.filter((t): t is string => !!t))]
})

const setTranslationIsBeingEdited = inject<(status: boolean) => { value: boolean }>(
  "setTranslationIsBeingEdited",
)
const showForm = () => {
  editing.value = true
  setTranslationIsBeingEdited?.(true)
}

const hideForm = () => {
  editing.value = false
  setTranslationIsBeingEdited?.(false)
  nextTick(() => {
    if (document.activeElement?.tagName !== "TEXTAREA") {
      translateBtn.value?.focus()
    }
  })
}

const saveTranslation = async (data: TranslationData) => {
  if (!editMode.value && specialTokens.value.length > 0) {
    const unusedTokens = specialTokens.value.filter(
      (token) => !data.text.some((t) => t.includes(token)),
    )

    if (unusedTokens.length > 0) {
      const confirmMsg = t("translate.special_symbols", unusedTokens.join(", "))
      const sure = confirm(confirmMsg)
      if (!sure) return
    }
  }

  loading.value = true
  error.value = null
  const oldPath = string.path

  try {
    await store.saveTranslation(data)
    hideForm()

    setTimeout(() => {
      if (string.path !== oldPath) {
        router.push(translateLink({ dir: string.path, params: { force: true } }))
        fetchDirectoriesTree()
      }
    }, 200)
  } catch (e: any) {
    error.value = e.message
  } finally {
    if (queryStringState.value !== STATE_FILTER_ALL) {
      fetchDirectoriesTree()
    }
    loading.value = false
  }
}
</script>

<template>
  <div class="col-md-6">
    <DisplayText
      v-if="string.translated_text && !editing && store.currentLanguage"
      :texts="string.translated_text.text"
      :pluralized="string.translated_text.pluralized"
      :click-to-edit="true"
      :language="store.currentLanguage"
      @click="showForm"
    />

    <div v-if="!editing" class="text-center">
      <button
        ref="translateBtn"
        class="btn btn-secondary mb-2 mt-3"
        :tabindex="currentIndex"
        @click="showForm"
      >
        {{ string.translated_text ? $t("translate.edit") : $t("translate.translate") }}
      </button>
    </div>

    <Transition name="slide">
      <TranslateForm
        v-if="editing"
        :name="string.name"
        :path="string.path"
        :pluralized="pluralized"
        :texts="texts"
        :loading="loading"
        :context="string.context"
        :error="error"
        @cancel="hideForm"
        @save-translation="saveTranslation"
      />
    </Transition>

    <StringInfo
      v-if="string.translated_text"
      :stringtext="string.translated_text"
      :is-translation="true"
    />
  </div>
</template>
