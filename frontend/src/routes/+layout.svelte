<script>
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav>
    <a href="/">home</a>
    <a href="/text">words</a>
	<a href="/kana">kana quiz</a>
	<a href="/reading">reading</a>
</nav>

{@render children()}
