<title>Reading Japanese</title>
<script>
    let hoverVal = $state("")
</script>
<div class="homepage">
<h1>Welcome!</h1>

<a href="/text" onmouseenter={hoverVal = "text"} onmouseleave={hoverVal = ""}>Text</a>
<a href="/reading" onmouseenter={hoverVal = "reading"} onmouseleave={hoverVal = ""}>Reading</a>
<a href="/quiz" onmouseenter={hoverVal = "quiz"} onmouseleave={hoverVal = ""}>Quiz</a>
<a href="/misc" onmouseenter={hoverVal = "misc"} onmouseleave={hoverVal = ""}>Misc</a>
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
