<template>
  <li :class="{first}">
    <span v-if="hasChildren" @click="toggle" :class="{open}">
      <i class="fas fa-angle-right"></i>
    </span>
    <span v-if="folderOpen" class="folder" :class="{'has-children': hasChildren}">
      <i class="fas fa-folder-open mr-1"></i>
    </span>
    <span v-else class="folder closed" :class="{'has-children': hasChildren}">
      <i class="fas fa-folder mr-1"></i>
    </span>
    <router-link
      :to="translateLink({ dir: path })"
      :class="{active}"
      :title="title"
      >
      {{ name }} ({{ node.strings.count + node.strings_in_children.count}})
    </router-link>
    <transition name="slide">
      <ul v-if="hasChildren && open">
        <directory-node
          v-for="(child, name) in node.children"
          :key="name"
          :node="child"
          :node-name="name"
          :parent-path="path"
          ></directory-node>
      </ul>
    </transition>
  </li>
</template>

<script>
export default {
  props: {
    nodeName: {
      type: String,
      required: false,
      default: '',
    },
    node: {
      type: Object,
      required: true,
    },
    first: {
      type: Boolean,
      required: false,
      default: false,
    },
    parentPath: {
      type: String,
      required: false,
      default: '',
    },
  },
  data() {
    return {
      open: this.first
    }
  },
  computed: {
    name() {
      return this.first ? 'Ĉiuj' : this.nodeName;
    },
    path() {
      return (this.first || this.parentPath === '') ? this.nodeName : this.parentPath + '/' + this.nodeName;
    },
    hasChildren() {
      return Object.keys(this.node.children).length > 0;
    },
    active() {
      return this.queryStringDir === this.path || this.first && !this.queryStringDir;
    },
    folderOpen() {
      return (this.open && this.hasChildren) || this.active;
    },
    title() {
      if (this.hasChildren) {
        return this.$t('navigation.count_children', {
          strings: this.node.strings.count,
          strings2: this.node.strings_in_children.count,
          words: this.node.strings.words,
          words2: this.node.strings_in_children.words
        })
      }
      else {
        return this.$t('navigation.count', {strings: this.node.strings.count, words: this.node.strings.words})
      }
    }
  },
  watch: {
    active(newValue) {
      if (newValue) {
        this.open = true;
      }
    }
  },
  methods: {
    toggle() {
      this.open = !this.open;
    },
  },
  created() {
    if (this.first || this.queryStringDir === this.path || this.queryStringDir.startsWith(this.path + '/')) {
      this.open = true;
    }
  }
};
</script>

<style lang="scss" scoped>
ul {
  padding-left: 9px;
  margin-top: 1px;
  margin-bottom: 1px;
  margin-left: 4px;
  list-style-type: none;
  border-left: 1px solid #999;
}

a {
  padding-left: 2px;

  &.active {
    font-weight: bold;
    background: $link-color;
    color: white;
    padding: 2px 4px;
    margin: 1px 0;
    border-radius: 6px;
    font-size: .9rem;

    &:hover {
      background: $link-hover-color;
      text-decoration: none;
    }
  }
}

li {
  &.first > a::before {
    display: none;
  }
}

.fa-angle-right {
  margin-right: 4px;
  position: relative;
  top: 1px;
  transition: transform .2s;
  cursor: pointer;
}

.open .fa-angle-right {
  transform: rotate(90deg);
}

.folder {
  margin-left: 14px;

  &.closed {
    margin-right: 2px;
  }

  &.has-children {
    margin-left: 2px;
  }
}
</style>