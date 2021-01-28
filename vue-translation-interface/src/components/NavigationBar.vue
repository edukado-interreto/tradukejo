<template>
  <nav aria-label="breadcrumb" class="my-4">
    <ol class="breadcrumb translation-path p-1">
      <li class="breadcrumb-item">
        <span class="dropdown">
          <a
            class="dropdown-toggle"
            href="#"
            type="button"
            id="dropdownLanguageVersionButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
            >{{ currentLanguage.name }}</a
          >
          <div
            class="dropdown-menu"
            aria-labelledby="dropdownLanguageVersionButton"
          >
            <router-link
              v-for="language in availableLanguages"
              :key="language"
              :to="translateLink({ lang: language.code })"
              class="dropdown-item"
              >{{ language.name }}</router-link
            >
          </div>
        </span>
      </li>

      <li class="breadcrumb-item">
        <router-link :to="translateLink({ dir: '' })"><i class="fas fa-home"></i></router-link>
      </li>
      <li
        v-for="(directory, index) in pathWithLinks"
        :key="index"
        :aria-current="index === pathWithLinks.length - 1 ? 'page' : null"
        class="breadcrumb-item"
        >
        <router-link
          v-if="index < pathWithLinks.length - 1"
          :to="translateLink({ dir: directory.path })"
          >
          {{ directory.name }}
        </router-link>
        <template v-else>{{ directory.name }}</template>
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  computed: {
    path() {
      return this.queryStringDir.split('/');
    },
    pathWithLinks() {
      let currentPath = '';
      const items = [];
      this.path.forEach((item) => {
        if (currentPath === '') {
          currentPath = item;
        }
        else {
          currentPath += '/' + item;
        }
        items.push({
          name: item,
          path: currentPath
        });
      });
      return items;
    }
  }
};
</script>
