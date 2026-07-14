<script setup lang="ts">
import { useTranslation } from "@/composables/useTranslation"

type DirStats = {
  count: number
  words: number
  characters: number
}

type Directory = {
  strings: DirStats
  strings_in_children: DirStats
}

const props = defineProps<{ directories: Record<string, Directory> }>()

const { translateLink, queryStringDir } = useTranslation()
</script>

<template>
  <ul v-if="Object.keys(directories).length > 0" class="subdirectory-list mb-4">
    <li class="row mb-1 font-weight-bold">
      <div class="col-6 col-lg-9"></div>
      <div class="col text-center">{{ $t("navigation.strings") }}</div>
      <div class="col text-center">{{ $t("navigation.words") }}</div>
      <div class="col text-center">{{ $t("navigation.characters") }}</div>
    </li>
    <li v-for="(dir, name) in directories" :key="name">
      <RouterLink
        :to="
          translateLink({
            dir: queryStringDir ? `${queryStringDir}/${name}` : (name as string),
          })
        "
        class="row"
      >
        <div class="col-6 col-lg-9"><i class="fas fa-folder mx-2"></i> {{ name }}</div>
        <div class="col text-center">
          <span class="badge badge-secondary">
            {{ dir.strings.count + dir.strings_in_children.count }}
          </span>
        </div>
        <div class="col text-center">
          <span class="badge badge-secondary">
            {{ dir.strings.words + dir.strings_in_children.words }}
          </span>
        </div>
        <div class="col text-center">
          <span class="badge badge-secondary">
            {{ dir.strings.characters + dir.strings_in_children.characters }}
          </span>
        </div>
      </RouterLink>
    </li>
  </ul>
</template>

<style lang="scss" scoped>
.subdirectory-list {
  list-style-type: none;
  padding: 0;
  margin: 0 1rem;

  a {
    text-decoration: none;
    padding: 8px 0;

    svg {
      color: #333;
    }

    &:hover {
      background: #f1f1f1;
      text-decoration: none;
    }
  }

  li + li {
    border-top: 1px solid #f0f0f0;
  }
}
</style>
