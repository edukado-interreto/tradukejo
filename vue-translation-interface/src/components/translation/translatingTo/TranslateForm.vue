<script setup lang="ts">
import axios from "axios"
import { useBus } from "@/composables/useBus"
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"

const ProposedTranslations = defineAsyncComponent(() => import("./ProposedTranslations.vue"))

type Props = {
  path?: string
  name?: string
  pluralized?: boolean
  texts?: Record<string, string>
  loading?: boolean
  context?: string
  error?: string | null
  newString?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  path: "",
  name: "",
  pluralized: false,
  texts: () => ({}),
  loading: false,
  context: "",
  error: null,
  newString: false,
})

const emit = defineEmits<{
  (e: "save-translation", payload: TranslationData): void
  (e: "cancel"): void
}>()

const { bus: eventBus } = useBus()
const store = useStore()
const { editMode } = useTranslation()
const stringId = inject<string | number>("stringId")

const textareas: Record<number, HTMLTextAreaElement> = reactive({})
const append_area = (el: HTMLTextAreaElement | null, index: number) => {
  if (el) textareas[index] = el
}

const enteredTexts = ref<string[]>(Object.values(props.texts))
const enteredPluralized = ref(props.pluralized)
const enteredContext = ref(props.context)
const enteredName = ref(props.name)
const enteredPath = ref(props.path)
const minor = ref(false)
const proposedTranslations = ref([])

const newTranslation = computed(() => Object.keys(props.texts).length === 0)

const textsWithPluralExamples = computed(() => {
  const texts: Record<string, string> = {}
  const examples = store.currentLanguage?.plural_examples_list || []
  examples.forEach((example: string) => {
    texts[example] = !newTranslation.value ? props.texts[example] || "" : ""
  })
  return texts
})

const canSubmit = computed(() => {
  if (!store.currentLanguage) return false
  if (props.newString && enteredName.value === "") return false

  if (!newTranslation.value) {
    const oldTexts = Object.values(props.texts)
    let differences = false

    for (let i = 0; i < enteredTexts.value.length; i++) {
      if (enteredTexts.value[i] !== oldTexts[i]) {
        differences = true
        break
      }
    }
    if (
      !differences &&
      (props.context !== enteredContext.value ||
        props.pluralized !== enteredPluralized.value ||
        props.name !== enteredName.value ||
        props.path !== enteredPath.value)
    ) {
      differences = true
    }
    if (!differences) return false
  } else {
    if (
      Object.keys(enteredTexts.value).length === 0 ||
      (enteredPluralized.value &&
        Object.keys(enteredTexts.value).length < store.currentLanguage.plural_examples_list.length)
    ) {
      return false
    }
  }

  return enteredTexts.value.every((t) => t !== "")
})

const sendForm = () => {
  if (canSubmit.value) {
    emit("save-translation", {
      trstring_id: stringId as number,
      text: enteredTexts.value,
      name: enteredName.value,
      path: enteredPath.value,
      pluralized: enteredPluralized.value,
      context: enteredContext.value,
      minor: minor.value,
    })
  }
}

const setTranslation = (texts: string[]) => {
  texts.forEach((text, i) => {
    enteredTexts.value[i] = text
  })
}

const insertSymbol = (args: InsertSymbol) => {
  if (args.stringId === stringId) {
    const textarea = textareas[args.index]
    if (!textarea) return

    const insertPosition = textarea.selectionEnd
    const oldText = enteredTexts.value[args.index] || ""
    const newText = oldText.slice(0, insertPosition) + args.text + oldText.slice(insertPosition)
    enteredTexts.value[args.index] = newText

    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(
        insertPosition + args.text.length,
        insertPosition + args.text.length,
      )
    })
  }
}

;(async () => {
  if (!props.newString && Object.keys(props.texts).length === 0) {
    const response = await axios.post("/vue/get-translation-suggestions/", {
      trstring_id: stringId,
      language: store.currentLanguage?.code,
    })
    proposedTranslations.value = response.data
  }
})()

onMounted(() => {
  textareas[0]?.focus()
  eventBus.on("insert-symbol", insertSymbol)
})

onBeforeUnmount(() => {
  eventBus.off("insert-symbol")
})
</script>

<template>
  <form @submit.prevent="sendForm" class="translation-form" v-if="store.currentLanguage">
    <transition name="jump">
      <div v-if="!!error" class="alert alert-danger">
        {{ error }}
      </div>
    </transition>
    <template v-if="editMode">
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          v-model.trim="enteredName"
          :placeholder="$t('translate.string_name')"
          :disabled="loading"
          required
        />
      </div>
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          v-model.trim="enteredPath"
          :placeholder="$t('translate.string_path')"
          :disabled="loading"
        />
      </div>
    </template>

    <template v-if="enteredPluralized">
      <div
        v-for="(text, example, index) in textsWithPluralExamples"
        :key="example"
        class="form-group"
      >
        <div class="plural-number-explanation">
          <label :for="'txt' + stringId + '-' + index">
            {{ $t("translate.number", { n: example }) }}
          </label>
        </div>
        <textarea
          rows="4"
          class="form-control"
          :dir="store.currentLanguage.direction"
          :lang="store.currentLanguage.code"
          :ref="(el) => append_area(el as HTMLTextAreaElement, index)"
          :title="index === 0 ? 'textarea' : undefined"
          :id="`txt${stringId}-${index}`"
          v-model.trim="enteredTexts[index]"
          :disabled="loading"
          required
        ></textarea>
      </div>
    </template>
    <div v-else class="form-group">
      <textarea
        rows="6"
        class="form-control"
        :dir="store.currentLanguage.direction"
        :lang="store.currentLanguage.code"
        :ref="(el) => append_area(el as HTMLTextAreaElement, 0)"
        v-model.trim="enteredTexts[0]"
        :disabled="loading"
        required
      ></textarea>
    </div>

    <template v-if="editMode">
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          :dir="store.currentLanguage.direction"
          v-model.trim="enteredContext"
          placeholder="Helpa teksto por tradukistoj"
          :disabled="loading"
        />
      </div>
      <div class="form-group">
        <div class="custom-control custom-checkbox">
          <input
            type="checkbox"
            class="custom-control-input pluralized"
            v-model="enteredPluralized"
            :id="'pluralized' + stringId"
            :disabled="loading"
          />
          <label class="custom-control-label" :for="'pluralized' + stringId"
            >Ĉeno kun pluralaj formoj</label
          >
        </div>
      </div>
      <div class="form-group" v-if="!newString">
        <div class="custom-control custom-checkbox">
          <input
            type="checkbox"
            class="custom-control-input minor-change"
            v-model="minor"
            :id="'minor' + stringId"
            :disabled="loading"
          />
          <label class="custom-control-label" :for="'minor' + stringId"
            >Malgrava ŝanĝo (ne marki la ĉenon kiel retradukendan)</label
          >
        </div>
      </div>
    </template>

    <proposed-translations
      v-if="proposedTranslations.length > 0"
      :translations="proposedTranslations"
      @pick-translation="setTranslation($event)"
    />

    <div class="form-group">
      <loading-button
        class="btn btn-primary mr-2 text-center"
        :class="{ 'can-submit': canSubmit }"
        :disabled="!canSubmit"
        :loading="loading"
      >
        {{ $t("translate.save") }}
      </loading-button>
      <input
        type="button"
        class="btn btn-secondary"
        :value="$t('translate.cancel')"
        @click="emit('cancel')"
        :disabled="loading"
      />
    </div>
  </form>
</template>

<style lang="scss" scoped>
.translation-form .plural-number-explanation {
  margin-bottom: 0;
  margin-top: 0;
}

:invalid {
  box-shadow: none;
}
</style>
