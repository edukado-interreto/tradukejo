<script setup lang="ts">
import Mark from "mark.js"
import { useBus } from "@/composables/useBus"
import { useTranslation } from "@/composables/useTranslation"

const { queryStringQ } = useTranslation()

const { bus: eventBus } = useBus()

const props = defineProps<{
  texts: Record<number, string>
  pluralized?: boolean
  clickToEdit?: boolean
  isTextFrom?: boolean
  language: Language
}>()

const translationIsBeingEdited = inject<{ value: boolean }>("translationIsBeingEdited")
const stringId = inject<string | number>("stringId")

const textRefs = useTemplateRef<(HTMLElement | null)[]>("textRefs")

const firstText = computed(() => Object.values(props.texts)[0])

const canAddSymbols = computed(() => {
  return props.isTextFrom && translationIsBeingEdited?.value
})

const clickClasses = computed(() => ({
  "click-to-edit": props.clickToEdit,
  "can-add-symbols": canAddSymbols.value,
}))

const addSymbol = (e: MouseEvent, index: number) => {
  if (canAddSymbols.value) {
    const target = e.target as HTMLElement
    if (target.tagName === "CODE") {
      eventBus?.emit("insert-symbol", {
        index,
        stringId: stringId as number,
        text: target.textContent,
      })
    }
  }
}

onMounted(() => {
  if (queryStringQ && textRefs.value) {
    textRefs.value.forEach((context) => {
      if (context) {
        const instance = new Mark(context)
        instance.mark(queryStringQ.value, {
          separateWordSearch: false,
          acrossElements: true,
        })
      }
    })
  }
})
</script>

<template>
  <div
    v-if="!pluralized"
    class="original-text"
    :class="clickClasses"
    v-html="firstText"
    :lang="language.code"
    :dir="language.direction"
    @click="addSymbol($event, 0)"
    ref="text0"
  ></div>
  <div v-else class="original-text" :class="clickClasses">
    <div class="context mt-1">
      <i class="fas fa-question-circle" :title="$t('translate.context')"></i>
      {{ $t("translate.number_explanations") }}
    </div>
    <template v-for="(text, example, index) in texts" :key="example">
      <div class="plural-number-explanation">
        {{ $t("translate.number", { n: example }) }}
      </div>
      <div v-html="text" @click="addSymbol($event, index)" :ref="'text' + index"></div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.click-to-edit {
  cursor: pointer !important;
  transition: opacity 100ms;

  &:hover {
    opacity: 0.86;
  }
}
</style>

<style lang="scss">
.original-text code {
  border: 1px solid transparent;
  padding: 1px 0;
  border-radius: 3px;
  transition: all 0.2s;
}

.can-add-symbols {
  code {
    cursor: pointer;
    background-color: rgba(220, 220, 220, 0.5);
    border-color: rgba(120, 120, 120, 0.6);

    &:hover {
      opacity: 0.75;
    }
  }
}
</style>
