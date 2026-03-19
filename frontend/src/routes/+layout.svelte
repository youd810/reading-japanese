<script>
	import favicon from '$lib/assets/favicon.svg';
	import '/src/global.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="nav">
	<nav>
		<a href="/">Home</a>
		<a href="/text">Text</a>
		<a href="/reading">Reading</a>
		<a href="/quiz">Quiz</a>
		<a href="/misc">Misc</a>
	</nav>
</div>

<div class="container">
	{@render children()}
</div>
