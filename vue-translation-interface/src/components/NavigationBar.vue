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
            >{{ currentLanguage.fields.name }}</a
          >
          <div
            class="dropdown-menu"
            aria-labelledby="dropdownLanguageVersionButton"
          >
            <router-link
              v-for="language in availableLanguages"
              :key="language"
              :to="{ name: 'translateLanguage', params: { lang: language.pk } }"
              class="dropdown-item"
              >{{ language.fields.name }}</router-link
            >
          </div>
        </span>
      </li>

      <li class="breadcrumb-item">
        <a href="/translate/7/eo/"><i class="fas fa-home"></i></a>
      </li>

      <li class="breadcrumb-item" aria-current="page">contact</li>
    </ol>
  </nav>
</template>

<script>
export default {

};
</script>
