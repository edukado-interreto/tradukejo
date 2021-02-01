<template>
  <div class="old-versions" :class="{ 'hide-deleted': !showDeleted }">
    <div class="text-center mt-3 mb-2">
      <button class="btn btn-secondary btn-sm" @click="toggleDeletedText">
        {{ showDeleted ? "Kaŝi" : "Montri" }} forigitajn partojn de tekstoj
      </button>
    </div>
    <div
      v-for="(version, index) in history"
      :key="version.id"
      class="old-version"
    >
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
      {{ index === 0 ? "(nuna versio)" : "" }}
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

<style lang="scss">
.hide-deleted del {
  display: none;
}

.old-version {
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 1rem;
  padding: 0.6rem 0.8rem;

  p {
    font-size: 1rem;
    margin-bottom: 0;
  }

  ins {
    color: #155724;
    background-color: #d4edda;
    text-decoration: none;
    font-weight: bold;
  }

  del {
    color: #721c24;
    background-color: #f8d7da;
  }
}
</style>