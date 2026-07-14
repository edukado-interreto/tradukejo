<script setup lang="ts">
import Mark from "mark.js"
import { useGlobals } from "@/composables/useGlobals"
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"

const store = useStore()
const { globals } = useGlobals()
const { editMode, queryStringQ, queryStringState, fetchDirectoriesTree } = useTranslation()

const props = defineProps<{ string: TrString }>()

const titleRef = useTemplateRef<HTMLElement>("title")

const stateLoading = ref(false)

const updateState = async (id: number, newState: any) => {
  stateLoading.value = true
  await store.updateStringState({
    id: id,
    translated: newState === globals.TRANSLATION_STATE_TRANSLATED,
  })
  stateLoading.value = false
  if (queryStringState.value !== globals.STATE_FILTER_ALL) {
    fetchDirectoriesTree?.()
  }
}

const deleteString = async (id: number) => {
  if (confirm("Ĉu vi certe volas forigi ĉi tiun ĉenon?")) {
    await store.deleteString(id)
    fetchDirectoriesTree()
  }
}

onMounted(() => {
  if (queryStringQ.value && titleRef.value) {
    const instance = new Mark(titleRef.value)
    instance.mark(queryStringQ.value, {
      separateWordSearch: false,
      diacritics: false,
    })
  }
})
</script>

<template>
  <header v-if="store.currentLanguage" class="row mb-2">
    <div class="col-6">
      <strong>
        <a :href="'#' + string.id" class="string-anchor" :title="$t('translate.link')" ref="title"
          >#{{ string.name }}</a
        >
      </strong>
      –
      <language-change-dropdown :string="string"></language-change-dropdown>
      <OnlineTranslatorLinks
        :language-from="string.original_text.language"
        :language-to="store.currentLanguage"
        :texts="string.original_text.raw_text"
      />
    </div>
    <div class="col-6 text-right translation-state-bar">
      <template v-if="!stateLoading">
        <button v-if="editMode" @click="deleteString(string.id)" class="btn btn-danger btn-sm">
          {{ $t("delete") }}
        </button>
        <template v-else>
          <a
            v-if="string.state === globals.TRANSLATION_STATE_TRANSLATED"
            href="#"
            @click.prevent="
              updateState(string.translated_text.id, globals.TRANSLATION_STATE_OUTDATED)
            "
            >{{ $t("translate.mark_outdated") }}</a
          >
          <a
            v-else-if="string.state === globals.TRANSLATION_STATE_OUTDATED"
            href="#"
            @click.prevent="
              updateState(string.translated_text.id, globals.TRANSLATION_STATE_TRANSLATED)
            "
            >{{ $t("translate.mark_translated") }}</a
          >

          <span
            v-if="string.state === globals.TRANSLATION_STATE_TRANSLATED"
            class="badge badge-success"
            >{{ $t("translate.translated") }}</span
          >
          <span
            v-else-if="string.state === globals.TRANSLATION_STATE_OUTDATED"
            class="badge badge-warning"
            >{{ $t("translate.outdated") }}</span
          >
          <span v-else class="badge badge-danger">{{ $t("translate.untranslated") }}</span>
        </template>
      </template>
      <LoadingSpinner v-else inline />
    </div>
  </header>
</template>

<style lang="scss" scoped>
.translation-state-bar a {
  font-size: 0.9rem;
  top: 1px;
  position: relative;
  margin-right: 9px;
}

.string-anchor {
  color: inherit;

  &:hover {
    text-decoration: none;
    color: #484848;
  }
}
</style>
