<script setup lang="ts">
import { encode } from "html-entities"
import { useI18n } from "vue-i18n"
import { useGlobals } from "@/composables/useGlobals"

const { t } = useI18n()
const { vueTranslationInterface: session } = useGlobals()

const { comment, language } = defineProps<{ comment: TranslationComment; language: Language }>()

const deleteComment = inject("deleteComment") as (id: number) => void

const beingDeleted = ref(false)

const canComment = computed(() => comment.author?.id === session.userId || session.isAdmin)

const URL_REGEX = /(((https?:\/\/)|(www\.))[^\s]+)/g
const ensure_proto = (url: string) => (url.match("^https?://") ? url : `https://${url}`)
const as_link = (url: string) =>
  `<a href="${ensure_proto(url)}" target="_blank" rel="noopener noreferrer">${url}</a>`

const formattedComment = computed(() => encode(comment.text).replace(URL_REGEX, as_link))

const deleteThis = () => {
  if (confirm(t("comments.delete_confirm"))) {
    beingDeleted.value = true
    deleteComment(comment.id)
  }
}
</script>

<template>
  <article>
    <LoadingButton
      v-if="canComment"
      class="btn btn-sm btn-danger float-right mb-1"
      @click="deleteThis"
      :loading="beingDeleted"
    >
      {{ $t("delete") }}
    </LoadingButton>
    <blockquote
      :lang="language.code"
      :dir="language.direction"
      v-html="formattedComment"
    ></blockquote>

    <hr class="my-2" style="clear: right" />

    {{ comment.create_date }}
    <template v-if="comment.author">
      –
      <a :href="comment.author.profile_url">{{ comment.author.username }}</a>
    </template>
  </article>
</template>

<style lang="scss" scoped>
blockquote {
  white-space: pre-line;
}
</style>
