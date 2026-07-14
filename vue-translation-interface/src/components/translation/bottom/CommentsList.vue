<script setup lang="ts">
const {
  comments = [],
  language,
  loading,
} = defineProps<{
  comments: TranslationComment[] | null
  language: Language
  loading: boolean
}>()

const enteredComment = ref("")

const canSubmit = computed(() => enteredComment.value != "")

defineEmits<{
  save: [comment: string]
  deleteComment: [id: number]
}>()

watch(
  () => loading,
  (isLoading) => {
    if (!isLoading) enteredComment.value = ""
  },
)
</script>

<template>
  <div class="comments">
    <h5>{{ $t("comments.comments") }}</h5>
    <TransitionGroup name="slide">
      <StringComment
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :language="language"
      />
    </TransitionGroup>

    <form @submit.prevent="$emit('save', enteredComment)">
      <div class="form-group">
        <textarea
          rows="3"
          class="form-control"
          required
          :lang="language.code"
          :dir="language.direction"
          :placeholder="$t('comments.write')"
          v-model.trim="enteredComment"
          :disabled="loading"
        ></textarea>
      </div>
      <div class="form-group">
        <LoadingButton
          class="btn btn-primary"
          :class="{ 'can-submit': canSubmit }"
          :disabled="!canSubmit"
          :loading="loading"
        >
          {{ $t("comments.add") }}
        </LoadingButton>
      </div>
    </form>
  </div>
</template>

<style lang="scss" scoped>
form {
  margin-top: 1rem;
}

h5 {
  margin-top: 0.7rem;
  font-weight: bold;
  font-size: 1.2rem;
  color: rgb(81, 79, 78);
}

article {
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 1rem;
  padding: 0.6rem 0.8rem;

  blockquote {
    font-size: 1rem;
    margin-bottom: 0;
    white-space: pre-line;
  }
}

textarea:invalid {
  box-shadow: none;
}
</style>
