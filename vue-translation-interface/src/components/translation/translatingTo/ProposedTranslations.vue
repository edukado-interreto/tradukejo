<template>
  <div>
    <h5>{{ $t('translate.suggestions') }}</h5>
    <ul>
      <li
        v-for="translation in translations"
        :key="translation"
        @click="pickTranslation(translation)"
        >
        <span
          v-for="pluralVersion in translation"
          :key="pluralVersion">
          {{ pluralVersion }}
        </span>
      </li>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
h5 {
  font-weight: bold;
  font-size: 1.2rem;
  color: #514f4e;
}

div {
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin: 1rem 0;
  padding: 0.6rem 0.8rem;
}

ul {
  margin-bottom: 0;
  padding-left: 20px;
}

li {
  transition: color .2s;

  &:hover {
    color: #555;
    cursor: pointer;
  }
}

span {
  display: block;
}
</style>

<script>
export default {
  props: ['translations'],
  methods: {
    pickTranslation(text) {
      this.$emit('pick-translation', text);
    }
  }
}
</script>