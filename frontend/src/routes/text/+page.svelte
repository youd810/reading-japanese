<script>
    import Switch from 'svelte-toggle-switch'

    // word counter and text highlighting logic 

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
    let textValue = $state("highlight")
    let hlValue = $state("word")
    let lValue = $state("English")
    let words = $state([])
    let wordcount = $state(0)
    const colors = [
    "#FFB3B3", // pastel red 0
    "#FFD9B3", // pastel orange 1
    "#FFFFB3", // pastel yellow 2
    "#B3FFB3", // pastel green 3
    "#B3D9FF", // pastel blue 4
    "#CCB3FF", // pastel indigo 5
    "#FFB3FF"  // pastel violet 6
    ]

    function getCharType(char) {
    if (/[\u3040-\u309F]/.test(char)) return "hiragana" // unicode range
    if (/[\u30A0-\u30FF]/.test(char)) return "katakana"
    if (/[\u4E00-\u9FAF]/.test(char)) return "kanji"
    return "other"
    }

    const charColors = {
    hiragana: colors[0], // red
    katakana: colors[4], // blue
    kanji: colors[5], // indigo
    other: colors[3] // green
    }

    // for the mouse hover logic
    let timerdict;
    function getDict(chars, lang) {
        clearTimeout(timerdict)         
        timerdict = setTimeout(async () => {   
            try{
            let response = await fetch(`http://localhost:8008/api/lookup?word=${chars}&dict=${lang}`);
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }
            let result = await response.json(); 
            dict = result
            console.log(result);
            } catch (error){
            console.log("An error occured", error)
            alert("An error occured")
            }
        }, 300)
    }
    
    let dict = $state([])
    
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

<!-- hiding this with conditional statements-->
<Switch colorScheme="red" size="sm" bind:value={textValue} design="multi" options={["highlight", "dictionary"]} label="Text mode" />
{#if textValue === "highlight"}
<Switch colorScheme="red" size="sm" bind:value={hlValue} design="multi" options={["word", "char"]} label="Highlighting options" />
{:else if textValue === "dictionary"}
<Switch colorScheme="red" size="sm" bind:value={lValue} design="multi" options={["English", "Japanese"]} label="Language options" />
{/if}
<br>
{#if textValue === "highlight"}
    {#if hlValue === "word"}
        {#each words as word, i}
            <!--`span` for iterating elements without a newline-->
            <span style="font-size: 18px; background-color: {colors[i%colors.length]}">{word}</span>
        {/each}
    {:else if hlValue == "char"}
        {#each naiyou as char}
            <!--call the getCharType with char as arg first then what it returns will become the key-->
            <span style="font-size: 18px; background-color: {charColors[getCharType(char)]}">{char}</span>
        {/each}
    {/if}
<!-- dict mode -->
{:else if textValue === "dictionary"}
    {#if lValue === "English"}
        {#each naiyou as char, i}
            <span onmouseenter={()=> getDict(naiyou.slice(i, i + 10), "en")} style="font-size: 18px;">{char}</span>
        {/each}
    {:else}
        {#each naiyou as char, i}
            <span onmouseenter={()=> getDict(naiyou.slice(i, i + 10), "jp")} style="font-size: 18px;">{char}</span>
        {/each}
    {/if}
    {#each dict as {word, reading, definition}}
        <p>{word}, {reading}, {definition}</p>
    {/each}
{/if}