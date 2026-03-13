<script>
    import Switch from 'svelte-toggle-switch'
    let naiyou = $state("")         // debounce simplified ver: 
    let timer                       // user calls on input > cancel the previous timer > 
    function sendText() {           // start a new one (x ms) under the same var id (timer) >
        clearTimeout(timer)         // repeat until the timer runs out > once the timer runs out, run the request.
        timer = setTimeout(async () => {    // moved async to here
            try {
            let response = await fetch("http://localhost:8008/api/text", {
                method : "POST", 
                headers : {
                    "Content-Type" : "application/json"
                },
                body : JSON.stringify({ 
                    text : naiyou
                })
            });
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }
            let result = await response.json(); // .json() or .text
            words = result.words
            wordcount = result.words.length    // reassign a global scope instead of fetching from a local one
            console.log(result);
            } catch (error){
                console.log("An error occured", error)
                alert("An error occured")
            }
        }, 500) // set a timer (in ms). wait for user to stop inputting for x ms before sending the request
    }
    let switchValue = $state("word")
    let words = $state([])
    let wordcount = $state(0)
    const colors = [
    "#FFB3B3", // pastel red
    "#FFD9B3", // pastel orange
    "#FFFFB3", // pastel yellow
    "#B3FFB3", // pastel green
    "#B3D9FF", // pastel blue
    "#CCB3FF", // pastel indigo
    "#FFB3FF"  // pastel violet
    ]

    function getCharType(char) {
    if (/[\u3040-\u309F]/.test(char)) return "hiragana" // unicode range
    if (/[\u30A0-\u30FF]/.test(char)) return "katakana"
    if (/[\u4E00-\u9FAF]/.test(char)) return "kanji"
    return "other"
    }

    const charColors = {
    hiragana: colors[0], // red
    katakana: colors[3], // green
    kanji: colors[4], // blue
    other: colors[6] // violet
    }

</script>
<nav>
    <a href="/">home</a>
    <a href="/text">words</a>
</nav>
<br>
<textarea bind:value={naiyou} oninput={sendText} style="font-size: 16px;"></textarea>
<p>Word count estimation: {wordcount}</p>
<p>Character count: {naiyou.length}</p> <!--for char it's straightforward-->
<p><b>NOTE: this word counter works by using an arbitrary indicator of how words should be segmented, as there is no objective way to count words in Japanese.</b></p>
<Switch colorScheme="red" size="sm" bind:value={switchValue} design="multi" options={["word", "char"]} label="Highlighting options" />
<br>
{#if switchValue === "word"}
    {#each words as word, i}
        <!--`span` for iterating elements without a newline-->
        <span style="font-size: 18px; background-color: {colors[i%colors.length]}">{word}</span>
    {/each}
{:else}
    {#each naiyou as char}
        <!--call the getCharType with char as arg first then what it returns will become the key-->
        <span style="font-size: 18px; background-color: {charColors[getCharType(char)]}">{char}</span>
    {/each}
{/if}