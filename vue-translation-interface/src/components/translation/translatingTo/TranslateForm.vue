<template>
  <form @submit.prevent="sendForm" class="translation-form">
    <div v-if="pluralized" class="form-group"></div>
    <div v-else class="form-group">
      <textarea
        rows="6"
        class="form-control"
        :dir="currentLanguage.direction"
        :lang="currentLanguage.code"
        v-model="enteredTexts[0]"
      ></textarea>
    </div>
    <div class="form-group">
      <input type="submit" class="btn btn-primary mr-2" value="Konservi" />
      <input
        type="button"
        class="btn btn-secondary"
        value="Nuligi"
        @click="cancel"
      />
    </div>
  </form>
</template>

<script>
export default {
  emits: ["save-translation", "cancel"],
  props: ["pluralized", "texts"],
  data() {
    return {
      showForm: false,
      enteredTexts: Object.values(this.texts),
    };
  },
  methods: {
    sendForm() {
      alert("oui");
    },
    cancel() {
      this.$emit("cancel");
    },
  },
};
</script>