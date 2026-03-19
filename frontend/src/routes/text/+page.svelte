<script>
    import Switch from 'svelte-toggle-switch'

    // word counter and text highlighting logic 

    let naiyou = $state("")         // debounce simplified ver: 
    let timer                       // user calls on input > cancel the previous timer > 
    function sendText() {           // start a new one (x ms) under the same var (timer) but different id  >
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
    function getDict(chars, lang, i) {
        clearTimeout(timerdict)         
        timerdict = setTimeout(async () => {   
            try{
            let response = await fetch(`http://localhost:8008/api/lookup?word=${chars}&dict=${lang}`);
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }
            let result = await response.json(); 
            dict = result
            index = i
            console.log(result);
            } catch (error){
            console.log("An error occured", error)
            alert("An error occured")
            }
        }, 0) // the timer is useless with mouse click but I can't be bothered to dismantle the whole thing
    }
    
    let dict = $state([])
    let index = $state()
    // the longest len (can be either from reading or word) in the dict (index 0 because it's the longest from sorting in the backend), default value is 0
    let maxlength = $derived(dict[0]?.len ?? 0) // optional chaining (?.) is equal to .get() in python

    
    function getDictColor(i) {
        if (i >= index && i < index + maxlength){
            return {bg: "red", font: "white"}
        }
        return {bg: "transparent", font: "black"} // fallback for chars outside of index - maxlength range
    }
    
</script>

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
<!--todo: highlight selected text--> 
    {#if lValue === "English"}
        {#each naiyou as char, i}
            <!--declare the colors to shorten the line for char-->
            {@const {bg, font} = getDictColor(i)} 
            <span onclick={()=> getDict(naiyou.slice(i, i + 10), "en", i)} style="font-size: 18px; background-color: {bg}; color: {font}">{char}</span>
        {/each}
    {:else}
        {#each naiyou as char, i}
            {@const {bg, font} = getDictColor(i)} 
            <span onclick={()=> getDict(naiyou.slice(i, i + 10), "jp", i)} style="font-size: 18px; background-color: {bg}; color: {font}">{char}</span>
        {/each}
    {/if}
    {#each dict as {word, reading, definition}, i}
        <p>
            Word: {word}<br>
            Reading: {reading}<br> 
            Definition: {definition}<br>
        </p>
    {/each}
{/if}