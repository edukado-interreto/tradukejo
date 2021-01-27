<template>
	<ul v-if="Object.keys(directories).length > 0" class="subdirectory-list my-4">
		<li class="row mb-1 font-weight-bold">
			<div class="col-6 col-lg-9"></div>
			<div class="col text-center">Ĉenoj</div>
			<div class="col text-center">Vortoj</div>
			<div class="col text-center">Signoj</div>
		</li>
		<li v-for="(dir, name) in directories" :key="name">
			<router-link :to="translateLink({dir: dir.path})" class="row">
				<div class="col-6 col-lg-9"><i class="fas fa-folder mx-2"></i> {{ name }}</div>
				<div class="col text-center"><span class="badge badge-secondary">{{ dir.strings }}</span></div>
				<div class="col text-center"><span class="badge badge-secondary">{{ dir.words }}</span></div>
				<div class="col text-center"><span class="badge badge-secondary">{{ dir.characters }}</span></div>
			</router-link>
		</li>
	</ul>
</template>

<script>
export default {
	props: {
		directories: {
			type: Object,
			required: true,
		}
	}
}
</script>
