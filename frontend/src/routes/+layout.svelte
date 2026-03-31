<script>
	import favicon from '$lib/assets/favicon.svg';
	import '/src/global.css';
	import { beforeNavigate, afterNavigate } from '$app/navigation';
	import {blur, draw, fade, fly, scale, slide} from 'svelte/transition'
	import {page} from '$app/state'
	import { animState } from '$lib/stores/offswitch.svelte';
	import Switch from 'svelte-toggle-switch';

	let { children } = $props();
	let off = $derived(animState.off)
	let status = $state("")	
	
	beforeNavigate(() => status = "active")
	afterNavigate(() => {status = "done", console.log(status)})
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<style>
	.off-toggle{ /* put these (not this one in particular) in here because toggle switch is an external lib and needs to be imported */
	position: fixed;
	bottom: 2%;
	left: 2%
    }
    .off-toggle :global(.switch--slider) {
        width: 2.5em;   
        height: 1.5em; 
        
    }
    .off-toggle :global(.switch-container) {
        font-family: 'Shippori Mincho', sans-serif;
        font-size: 16px;
    }
    .off-toggle :global(.switch-thumb) {
    width: 1.2em;   
    height: 1.2em;
    }
    .off-toggle :global(.switch--slider.checked .switch-thumb) {
        transform: translateX(1.0em); /* travel = track width - ball width - (2 * offset) */
    }
</style>

{#if status}
<div class="loading-bar {status}" onanimationend={()=> {if (status === "done") status = ""}}></div>
{/if}

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
{:else}
	<div class= "off-toggle" onclick={()=> !animState.off ? animState.off = true : animState.off = false}> <!-- this implementation is dumb but it works so w/e -->
		<Switch design="slider" colorScheme="red" bind:value={off} label="雨うぜぇ！"/>
	</div>
{/if}

{#key page.url.pathname}
<div class="container" in:fly={{x: 200, duration: 250}}>
	{@render children()}
</div>
{/key}