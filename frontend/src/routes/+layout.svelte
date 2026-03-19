<script>
	import favicon from '$lib/assets/favicon.svg';
	import '/src/global.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav>
    <a href="/">home</a>
    <a href="/text">words</a>
	<a href="/quiz">quiz</a>
	<a href="/reading">reading</a>
	<a href="/misc">misc</a>
</nav>

<div class="container">
	{@render children()}
</div>
