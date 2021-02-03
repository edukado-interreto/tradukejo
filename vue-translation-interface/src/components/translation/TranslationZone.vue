<template>
  <add-string
    v-if="editMode"
  ></add-string>
  <transition v-for="string in strings" :key="string.id" name="fade" mode="out-in">
    <translation-row v-if="!string.deleted" :string="string"></translation-row>
    <deleted-string v-else :string="string"></deleted-string>
  </transition>
  <load-more-strings v-if="canLoadMore"></load-more-strings>
</template>

<script>
import { defineAsyncComponent } from 'vue';
import TranslationRow from "./TranslationRow";
import DeletedString from "./DeletedString";
const AddString = defineAsyncComponent(() => import('./AddString'));
const LoadMoreStrings = defineAsyncComponent(() => import('./LoadMoreStrings'));

export default {
  components: {
    TranslationRow,
    DeletedString,
    AddString,
    LoadMoreStrings
  },
  props: ["strings"],
  computed: {
    canLoadMore() {
      return this.$store.getters.canLoadMore;
    }
  }
};
</script>

<style scoped>
.fade-enter-from {
  opacity: 0;
  transform: scaleY(0);
}

.fade-leave-to {
  opacity: 0;
  transform: scaleY(0);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: scaleY(1);
}

.fade-enter-active,
.fade-leave-active {
  transition: all .2s;
}
</style>