<title>Reading Japanese</title>

<script>
    import { onMount } from "svelte";
    import Switch from "svelte-toggle-switch";

    let hoverVal = $state("")

    let letters = $state([]);
    let chars = $state([]);
    let canvas;
    let ctx;
    let anim;
    let off = $state();
    

    async function getChars() {
        try{
        let response = await fetch(`http://localhost:8008/api/home`);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        letters = await response.json()
        } catch (error){
        console.log("An error occured", error);
        }
    }

    // animation logic
    function rain(){ // runs for 1 frame
        ctx.clearRect(0, 0, canvas.width, canvas.height) // clears canvas on every frame to prevent trailing
        for (let i = 0; i < chars.length; i++){
            ctx.font = `${chars[i].size}px serif`
            chars[i].y += chars[i].speed;
            chars[i].rotation += chars[i].speed * 0.015;
            ctx.save()
            ctx.translate(chars[i].x, chars[i].y) // set the origin pos (0) to current i pos (x, y) respectively
            ctx.rotate(chars[i].rotation) // always rotates around the current origin pos, that's why you have to translate() first
            ctx.textAlign = "center" // these fix the axis problem (x axis)
            ctx.textBaseline = "middle" // (y axis)
            ctx.fillText(chars[i].char, 0, 0) // 0 because read translate()
            ctx.restore() // reset translate - baseline back for the next i
            if (chars[i].y > (canvas.height + chars[i].size)){
                chars.splice(i, 1)
                // shifts back i after splicing, because splicing brings the next item down to index i, but then i++ skips it
                // and because the next step is i++, then animate(i), what we want is  i > i-- > i++ = i
                // otherwise the skipped i will flicker
                i-- 
            }
        }
        anim = requestAnimationFrame(rain); // runs again (60 calls per second (bound by fps) by default)
    }

    let interval;

    function pushChar(){
        chars.push({ 
            char : letters[Math.floor(Math.random() * letters.length)], // function to reference a reactive var
            size: Math.random() * 40 + 50,  // 40-90px
            speed: Math.random() * 3 + 1,   // 1-4px per frame 
            x: Math.random() * canvas.width,
            y: 0,                           // starts at top
            rotation: 0                     // starts at 0, increments each frame
        })
    }

    function stopAnim(){
        chars = []
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        cancelAnimationFrame(anim)
        clearInterval(interval)
        interval = 0 // set interval to false for a check
    }

    function startAnim(){
        if (interval) return // this prevents interval from going haywire in case user keeps calling startanim with onclick
        interval = setInterval(pushChar, 1000)
        anim = requestAnimationFrame(rain)
    }

    function handleVisibility() {
        if (document.hidden) { // pauses the animation when in other tabs to save on performance
            cancelAnimationFrame(anim)
            clearInterval(interval)
            interval = 0
        } else if (!document.hidden && !off) {
            startAnim()
        }
    }

    onMount( async ()=> { // onmount instead of effect for the preps because you want it to run only once
        await getChars() // wait for this otherwise the first few chars would be undefined
        document.addEventListener("visibilitychange", handleVisibility) 
        ctx = canvas.getContext("2d") // this is a native js API so no need to import
        canvas.width = window.innerWidth
        canvas.height = window.innerHeight
        startAnim()
    })

    // cleanup function for interval so it stops running after navigating out of homepage
    // moved it out of onmount async because async will always return promise, and svelte expects a function 
    // so it will just ignore the cleanup function inside of an async function even though the function is inside the promise
    $effect(()=> { 
        return ()=> { 
            clearInterval(interval)
            cancelAnimationFrame(anim)
            document.removeEventListener("visibilitychange", handleVisibility)
        }
    })


</script>

<style>
    :global(body) {
        overflow-x: hidden;
    }
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

<canvas bind:this={canvas}></canvas> <!-- set up the canvas first before everything else -->

<div class= "off-toggle" onclick={()=> off ? stopAnim() : startAnim()}> <!-- this implementation is dumb but it works so w/e -->
    <Switch design="slider" colorScheme="red" bind:value={off} label="雨うぜぇ！"/>
</div>

<div class="homepage">
<h1>Welcome!</h1>

<a href="/text" onmouseenter={()=> hoverVal = "text"} onmouseleave={()=> hoverVal = ""}>Text</a>
<a href="/reading" onmouseenter={()=> hoverVal = "reading"} onmouseleave={()=> hoverVal = ""}>Reading</a>
<a href="/quiz" onmouseenter={()=> hoverVal = "quiz"} onmouseleave={()=> hoverVal = ""}>Quiz</a>
<a href="/misc" onmouseenter={()=> hoverVal = "misc"} onmouseleave={()=> hoverVal = ""}>Misc</a>
</div>

<div class="message">
    {#if hoverVal === "text"}
        <span>Analyze your text (word segmenter, one-click dictionary, and more)</span>
    {:else if hoverVal === "reading"}
        <span>Test your reading speed</span>
    {:else if hoverVal === "quiz"}
        <span>Test your knowledge in Japanese characters</span>
    {:else if hoverVal === "misc"}
        <span>Other stuff</span>
    {/if}
</div>


