<template>
  <div class="old-versions" :class="{ 'hide-deleted': !showDeleted }">
    <div class="text-center mt-3 mb-2">
      <button class="btn btn-secondary btn-sm" @click="toggleDeletedText">
        {{ showDeleted ? "Kaŝi" : "Montri" }} forigitajn partojn de tekstoj
      </button>
    </div>
    <div v-for="(version, index) in history" :key="version.id" class="old-version">
      <template v-if="version.pluralized">
        <template v-for="(text, example) in version.comparison" :key="example">
          <div class="plural-number-explanation">
            Se la nombro estas {{ example }}:
          </div>
          <div v-html="text"></div>
        </template>
      </template>
      <div
        v-else
        v-html="version.comparison[Object.keys(version.comparison)[0]]"
      ></div>

      <hr class="my-2" />

      {{ version.create_date }}
      {{ index === 0 ? '(nuna versio)' : '' }}
      <template v-if="version.translated_by">
        –
        <a :href="version.translated_by.profile_url">{{
          version.translated_by.username
        }}</a>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: ["history"],
  data() {
    return {
      showDeleted: true,
    };
  },
  methods: {
    toggleDeletedText() {
      this.showDeleted = !this.showDeleted;
    },
  },
};
</script>

<style>
.hide-deleted del {
  display: none;
}
</style>