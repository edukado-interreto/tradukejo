<script setup lang="ts">
import { useI18n } from "vue-i18n"
import axios from "axios"
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue"
import { useTranslation } from "@/composables/useTranslation"

const StringHistory = defineAsyncComponent(() => import("./StringHistory.vue"))
const CommentsList = defineAsyncComponent(() => import("./CommentsList.vue"))

const props = defineProps<{
  stringtext: any
  isTranslation?: boolean
}>()

const { t } = useI18n()

const { editMode } = useTranslation()

const rowIsSelected = inject("rowIsSelected", false)

const showHistory = ref(false)
const historyLoading = ref(false)
const history = ref<TrStringTextHistory[] | null>(null)

const showComments = ref(false)
const commentsLoading = ref(false)
const comments = ref<TranslationComment[] | null>(null)
const commentBeingSaved = ref(false)

const commentCount = computed(() => {
  return comments.value === null ? props.stringtext.comments : comments.value.length
})

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const response = await axios.post("/vue/get-history/", {
      trstringtext_id: props.stringtext.id,
    })
    history.value = response.data
  } finally {
    historyLoading.value = false
  }
}

const loadComments = async () => {
  commentsLoading.value = true
  try {
    const response = await axios.post("/vue/get-comments/", {
      trstringtext_id: props.stringtext.id,
    })
    comments.value = response.data
  } finally {
    commentsLoading.value = false
  }
}

const toggleHistory = () => {
  showHistory.value = !showHistory.value
  if (showHistory.value && history.value === null) {
    loadHistory()
  }
}

const toggleComments = () => {
  showComments.value = !showComments.value
  if (showComments.value && comments.value === null && props.stringtext.comments > 0) {
    loadComments()
  }
}

const saveComment = async (text: string) => {
  commentBeingSaved.value = true
  try {
    const response = await axios.post("/vue/save-comment/", {
      trstringtext_id: props.stringtext.id,
      text: text,
    })
    if (comments.value === null) {
      comments.value = [response.data]
    } else {
      comments.value.push(response.data)
    }
  } finally {
    commentBeingSaved.value = false
  }
}

const deleteComment = async (id: number) => {
  try {
    const response = await axios.post("/vue/delete-comment/", {
      comment_id: id,
    })
    if (response.data.ok && comments.value) {
      const index = comments.value.findIndex((el) => el.id === id)
      if (index !== -1) comments.value.splice(index, 1)
    }
  } catch (error) {
    console.error(error)
  }
}

provide("deleteComment", deleteComment)

watch(
  () => props.stringtext,
  () => {
    if (showHistory.value) loadHistory()
    if (showComments.value) loadComments()
  },
)

onMounted(() => {
  const shouldOpenComments =
    rowIsSelected &&
    commentCount.value > 0 &&
    !showComments.value &&
    !(props.isTranslation && editMode.value)

  if (shouldOpenComments) {
    toggleComments()
  }
})
</script>

<template>
  <div class="translation-author">
    {{ stringtext.last_change }}
    –
    <template v-if="stringtext.translated_by">
      <a :href="stringtext.translated_by.profile_url">
        {{ stringtext.translated_by.username }}
      </a>
      |
    </template>

    <a href="#" @click.prevent="toggleComments" class="toggle" :class="{ open: showComments }">
      {{ commentCount === 0 ? t("comments.link") : t("comments.number", commentCount) }}
    </a>

    <template v-if="stringtext.old_versions > 0">
      |
      <a href="#" @click.prevent="toggleHistory" class="toggle" :class="{ open: showHistory }">
        {{ t("history.versions", stringtext.old_versions + 1) }}
      </a>

      <LoadingSpinner v-if="showHistory && historyLoading" small />

      <Transition name="slide">
        <StringHistory v-if="showHistory && !historyLoading" :history="history" />
      </Transition>
    </template>

    <LoadingSpinner v-if="showComments && commentsLoading" small />

    <Transition name="slide">
      <CommentsList
        v-if="showComments && !commentsLoading"
        :comments="comments"
        :language="stringtext.language"
        :loading="commentBeingSaved"
        @save="saveComment"
      />
    </Transition>
  </div>
</template>

<style lang="scss" scoped>
.translation-author {
  font-size: 0.9em;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(200, 200, 200, 0.6);
}

.toggle::after {
  display: inline-block;
  margin-left: 0.35em;
  vertical-align: 0.255em;
  content: "";
  border-top: 0.3em solid;
  border-right: 0.3em solid transparent;
  border-bottom: 0;
  border-left: 0.3em solid transparent;
  transform: rotate(0);
  transition: transform 0.2s;
}

.toggle.open::after {
  transform: rotate(180deg);
}
</style>
