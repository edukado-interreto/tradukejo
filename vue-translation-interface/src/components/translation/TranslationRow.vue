<script setup lang="ts">
import axios from "axios"
import { useGlobals } from "@/composables/useGlobals"
import { useTranslation } from "@/composables/useTranslation"
import { useStore } from "@/store"

const props = defineProps<{ string: TrString }>()

const store = useStore()
const {
  vueTranslationInterface: { projectLanguage },
  globals,
} = useGlobals()
const rowRef = useTemplateRef<HTMLElement>("row")

const translationIsBeingEdited = ref(false)
const languageFromLoading = ref(false)
const currentOriginalText = ref(props.string.original_text)

const { chosenStringId } = useTranslation()
const isSelected = computed(() => chosenStringId.value === props.string.id)

const stringToShow = computed(() => ({
  ...props.string,
  original_text: currentOriginalText.value,
}))

const translationRowClasses = computed(() => ({
  translated: props.string.state === globals.TRANSLATION_STATE_TRANSLATED,
  outdated: props.string.state === globals.TRANSLATION_STATE_OUTDATED,
  untranslated: props.string.state === globals.TRANSLATION_STATE_UNTRANSLATED,
  selected: isSelected.value,
}))

const rowAlignClasses = computed(() => ({
  "d-flex":
    props.string.state === globals.TRANSLATION_STATE_UNTRANSLATED &&
    !translationIsBeingEdited.value,
  "align-items-center":
    props.string.state === globals.TRANSLATION_STATE_UNTRANSLATED &&
    !translationIsBeingEdited.value,
}))

const loadLanguageFrom = async (code: string) => {
  if (code === projectLanguage) {
    currentOriginalText.value = props.string.original_text
  } else if (code === store.currentLanguage?.code) {
    currentOriginalText.value = props.string.translated_text
  } else {
    languageFromLoading.value = true
    try {
      const response = await axios.post("/vue/get-string-translation/", {
        trstring_id: props.string.id,
        language: code,
      })
      currentOriginalText.value = response.data
    } catch (error) {
      console.log(error)
    } finally {
      languageFromLoading.value = false
    }
  }
}

const setTranslationIsBeingEdited = (status: boolean) => {
  translationIsBeingEdited.value = status
  if (store.currentLanguage?.id === currentOriginalText.value?.language?.id) {
    currentOriginalText.value = props.string.original_text
  }
}

provide("loadLanguageFrom", loadLanguageFrom)
provide("stringId", stringToShow.value.id)
provide("setTranslationIsBeingEdited", setTranslationIsBeingEdited)
provide(
  "translationIsBeingEdited",
  computed(() => translationIsBeingEdited.value),
)
provide("rowIsSelected", isSelected.value)

onMounted(() => {
  if (isSelected.value && rowRef.value) {
    rowRef.value.scrollIntoView({ behavior: "smooth" })
  }
})
</script>

<template>
  <article class="translation-row" :class="translationRowClasses" :id="String(string.id)" ref="row">
    <TranslationRowHeader :string="stringToShow" />
    <div class="row mt-1" :class="rowAlignClasses">
      <text-from
        v-if="!languageFromLoading"
        :stringtext="currentOriginalText"
        :context="string.context"
      ></text-from>
      <LoadingSpinner v-else small />
      <TextTo :string="stringToShow" />
    </div>
  </article>
</template>

<style lang="scss">
.translation-row {
  border: 1px solid black;
  border-radius: 5px;
  margin: 0;
  margin-bottom: 1rem;
  padding: 0.5rem 0.6rem;

  &.translated {
    border-color: #90bda0;
    background-color: #d4edda;
  }

  &.untranslated {
    border-color: #bd9090;
    background-color: #f8d7da;
  }

  &.outdated {
    border-color: #bdb590;
    background-color: #fff3cd;
  }

  &.selected {
    border: 2px solid #007bff;
    box-shadow: 0 0 5px #333;
  }

  input[type="text"] {
    width: 100%;
  }

  code {
    font-weight: bold;
    color: #304060;
    font-size: 1em;
    line-height: 1em;
  }

  .context {
    color: #555;
    font-weight: bold;
    margin-top: 1rem;
    font-size: 0.9rem;

    svg {
      cursor: help;
    }
  }
}

.plural-number-explanation {
  color: #555;
  font-weight: bold;
  margin-top: 0.8rem;
  margin-bottom: 0.3rem;
  font-size: 0.9rem;

  &:first-child {
    margin-top: 0;
  }
}

mark {
  background-color: #ffee00;
  padding: 0;
  border-radius: 3px;
}
</style>
