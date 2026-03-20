<title>Quiz</title>
<script>
    import { page } from "$app/state"; // store or state? both work (but stores needs $ symbol) 
    import { fade } from "svelte/transition";
    import * as wanakana from 'wanakana'

   
    let moji = $state({})
    let ji = $derived(page.url.searchParams.get("ji")) // add an option to switch query, no default
    
    async function getMoji(ji) {
        try{
        let response = await fetch(`http://localhost:8008/api/quiz?ji=${ji}`);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        moji = await response.json()
        nextMoji()   
        console.log(moji);
    } catch (error){
        console.log("An error occured", error);
    }}


    let entries = $derived(ji === "y"? moji : Object.entries(moji)) // Object.entries() to iterate an object. `cond? if true : else`
    let randomEntry = $state([])                 // Object.entries() returns an array of [key, value] pairs. so randomEntry would be something like ["あ", "a"]
    function nextMoji() {                        // or randomEntry[0] for kana, and  randomEntry[1] for romaji
        randomEntry = entries[Math.floor(Math.random() * entries.length)] // equivalent to random.choice(entries) in python
    }

    let answer = $state("")
    function check() {
        if (answer === randomEntry[1]){
            answer = "" // reset the answer upon correct guess
            nextMoji()
        }
    }

    // logic for wanakana
    let inputEle = $state("")
    $effect(() => {
        if (inputEle) {
            wanakana.bind(inputEle)
            return ()=> {if (inputEle) wanakana.unbind(inputEle)} // checks if inputEle isn't null
            }
    })

</script>

{#key ji}
    <div  in:fade={{duration: 250}}>
        {#if ji}
            <a href="/quiz">Back</a>
        {/if}

        <div class="quiz-container">
            {#if !ji}
                <div class="choices">
                    <a href="/quiz?ji=h" onclick={()=> getMoji("h")}>Hiragana</a>
                    <a href="/quiz?ji=k" onclick={()=> getMoji("k")}>Katakana</a>
                    <a href="/quiz?ji=y" onclick={()=> getMoji("y")}>四字熟語</a>
                </div>
                {/if}
                {#if ji}
                    <p style="font-size: 60px;">{randomEntry[0]}</p>
                    {#if ji === "y"}
                        <!-- this gets the value directly from the DOM event instead of relying on bind:value, so input reads the converted wanakana output -->
                        <input bind:this={inputEle} bind:value={answer} oninput={(e) => {answer = e.target.value; check()}}>
                    {:else}
                        <input bind:value={answer} oninput={check}> <!--checking in every input made if input matches the answer-->
                    {/if}
            {:else}
                <p>select an option</p>
            {/if}
            {#if ji === "y"}
                <p>Hint: {randomEntry[2]}</p>
            {/if}
        </div>

        {#if ji}
            <button class="button-bottom" onclick={()=> getMoji(ji)}>Hard Reset</button>
        {/if}
    </div>
{/key}