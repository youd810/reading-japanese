<script>
	import favicon from '$lib/assets/favicon.svg';
	import '/src/global.css';
	import {blur, draw, fade, fly, scale, slide} from 'svelte/transition'
	import {page} from '$app/state'

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if page.url.pathname !== "/"}
<div class="nav">
	<nav>
		<a href="/">Home</a>
		<a href="/text">Text</a>
		<a href="/reading">Reading</a>
		<a href="/quiz">Quiz</a>
		<a href="/misc">Misc</a>
	</nav>
</div>
{/if}

{#key page.url.pathname}
<div class="container" in:fly={{x: 200, duration: 250}}>
	{@render children()}
</div>
{/key}