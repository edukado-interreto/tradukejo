<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
	<ul class="navbar-nav mr-auto">
		<li class="nav-item dropdown" v-if="!editMode">
			<a class="nav-link dropdown-toggle" href="#" id="stringStateDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
				{{ currentStateFilter }}
			</a>
			<div class="dropdown-menu" aria-labelledby="stringStateDropdown">
				<router-link
					v-for="(name, key) in stateFilters"
					:key="key"
					class="dropdown-item"
					:to="translateLink({state: key})"
					>
					{{ name }}
				</router-link>
			</div>
		</li>
		<li class="nav-item dropdown">
			<a class="nav-link dropdown-toggle" href="#" id="sortDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
				{{ currentSortFilter }}
			</a>
			<div class="dropdown-menu" aria-labelledby="sortDropdown">
				<router-link
					v-for="(name, key) in sortFilters"
					:key="key"
					class="dropdown-item"
					:to="translateLink({sort: key})"
					>
					{{ name }}
				</router-link>
			</div>
		</li>
	</ul>
	<form class="form-inline my-2 my-lg-0" @submit.prevent="search">
		<input class="form-control mr-sm-2" type="search" :placeholder="$t('filters.search') + '…'" :aria-label="$t('filters.search')" v-model="searchString">
		<button class="clear-search" v-if="searchString" @click="clearSearch"><i class="fas fa-times-circle"></i></button>
		<button class="btn btn-secondary" type="submit">{{ $t('filters.search') }}</button>
  </form>
</nav>
</template>

<script>
export default {
	data() {
		return {
			searchString: this.queryStringQ,
			stateFilters: {
				[this.globals.STATE_FILTER_ALL]: this.$t('filters.all'),
				[this.globals.STATE_FILTER_UNTRANSLATED]: this.$t('filters.untranslated'),
				[this.globals.STATE_FILTER_OUTDATED]: this.$t('filters.outdated'),
				[this.globals.STATE_FILTER_OUTDATED_UNTRANSLATED]: this.$t('filters.untranslated_outdated'),
			},
			sortFilters: {
				[this.globals.SORT_STRINGS_BY_NAME]: this.$t('filters.order_name'),
				[this.globals.SORT_STRINGS_BY_OLDEST]: this.$t('filters.order_old'),
				[this.globals.SORT_STRINGS_BY_NEWEST]: this.$t('filters.order_new'),
			},
		};
	},
	computed: {
		currentStateFilter() {
			if (this.queryStringState in this.stateFilters) {
				return this.stateFilters[this.queryStringState];
			}
			else {
				return this.stateFilters[Object.keys(this.stateFilters)[0]]
			}
		},
		currentSortFilter() {
			if (this.queryStringSort in this.sortFilters) {
				return this.sortFilters[this.queryStringSort];
			}
			else {
				return this.sortFilters[Object.keys(this.sortFilters)[0]]
			}
		},
	},
	methods: {
		search() {
			this.$router.push(this.translateLink({q: this.searchString}));
		},
		clearSearch() {
			this.searchString = '';
			this.search();
		}
	}
}
</script>

<style lang="scss" scoped>
.clear-search {
	background: none;
	border: none;
	margin: 0;
	padding: 0;
	position: relative;
	right: 2em;
	bottom: 0px;
	color: #A8A8A8;
	width: 0;

	&:hover {
		color: #797979;
	}
}
</style>