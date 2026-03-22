<title>Reading Japanese</title>

<script>
    import { onMount } from "svelte";
    
    let hoverVal = $state("")


    let letters = $state([]) 
    let letter = $state({})
    let chars = $state([])
    let canvas;
    let ctx
    

    async function getChars() {
        try{
        let response = await fetch(`http://localhost:8008/api/home`);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        letters = await response.json()
        console.log(letters);
        } catch (error){
        console.log("An error occured", error);
        }
    }

    // animation logic
    function rain(){
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        for (let i = 0; i < chars.length; i++){
            ctx.font = `${chars[i].size}px serif`
            chars[i].y += chars[i].speed;
            chars[i].rotation += chars[i].speed * 0.015;
            ctx.save()
            ctx.translate(chars[i].x, chars[i].y)
            ctx.rotate(chars[i].rotation)
            ctx.textAlign = "center" // these fix the axis problem
            ctx.textBaseline = "middle"
            ctx.fillText(chars[i].char, 0, 0)
            ctx.restore()
            if (chars[i].y > (canvas.height + chars[i].size)){
                chars.splice(i, 1)
                // shifts back i after splicing, because splicing brings the next element down to index i, but then i++ skips it
                // because the next step is i++, then animate(i), what we want is  i > i-- > i++ = i
                // otherwise the skipped i will flicker
                i-- 
            }
        }
        requestAnimationFrame(rain);
    }
     
    onMount(async ()=> { // onmount instead of effect because you want it to run only once
        await getChars() // wait for this otherwise the first few chars would be undefined
        setInterval(() => {
            chars.push({ // put this inside of `effect` otherwise canvas would be undefined
                char : letters[Math.floor(Math.random() * letters.length)], // function to reference a reactive var
                size: Math.random() * 40 + 50,  // 40-90px
                speed: Math.random() * 3 + 1,   // 1-4px per frame 
                x: Math.random() * canvas.width,
                y: 0,                            // starts at top
                rotation: 0                      // starts at 0, increments each frame
            })
        }, 1000);
        ctx = canvas.getContext("2d") // this is a native lib so no need to import
        canvas.width = window.innerWidth
        canvas.height = window.innerHeight
        requestAnimationFrame(rain)
    })

</script>

<style>
    :global(body) {
        overflow-x: hidden;
    }
</style>

<canvas bind:this={canvas}></canvas> <!-- set up the canvas first before everything else -->

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
