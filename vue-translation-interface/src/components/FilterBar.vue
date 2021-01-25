<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
	<ul class="navbar-nav mr-auto">
		<li class="nav-item dropdown">
			<a class="nav-link dropdown-toggle" href="#" id="stringStateDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
				
				Ĉiuj ĉenoj
				
			</a>
			<div class="dropdown-menu" aria-labelledby="stringStateDropdown">
				<a class="dropdown-item" href="./">Ĉiuj ĉenoj</a>
				<a class="dropdown-item" href="./?state=untr">Nur netradukitaj</a>
				<a class="dropdown-item" href="./?state=outd">Nur retradukendaj</a>
				<a class="dropdown-item" href="./?state=unout">Netradukitaj kaj retradukendaj</a>
			</div>
		</li>
		<li class="nav-item dropdown">
			<a class="nav-link dropdown-toggle" href="#" id="sortDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
				
				Ordigi laŭ nomo
				
			</a>
			<div class="dropdown-menu" aria-labelledby="sortDropdown">
				<a class="dropdown-item" href="./">Ordigi laŭ nomo</a>
				<a class="dropdown-item" href="./?sort=old">Ordigi laŭ plej malnovaj</a>
				<a class="dropdown-item" href="./?sort=new">Ordigi laŭ plej novaj</a>
			</div>
		</li>
	</ul>
	<form class="form-inline my-2 my-lg-0" action="/translate/7/eo/" method="get">
		
		
		
		<input class="form-control mr-sm-2" type="search" placeholder="Serĉi…" aria-label="Serĉi" value="" name="q">
		<button class="btn btn-secondary" type="submit">Serĉi</button>
    </form>
</nav>
</template>

<script>
export default {

}
</script>
