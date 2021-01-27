<template>
  <transition v-for="string in strings" :key="string.id" name="fade" mode="out-in">
    <translation-row v-if="!string.deleted" :string="string"></translation-row>
    <deleted-string v-else :string="string"></deleted-string>
  </transition>
</template>

<script>
import TranslationRow from "./translation/TranslationRow";
import DeletedString from "./translation/DeletedString";

export default {
  components: {
    TranslationRow,
    DeletedString,
  },
  props: ["strings"],
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