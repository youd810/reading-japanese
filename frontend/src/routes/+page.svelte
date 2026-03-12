<script>
    import { page } from "$app/state"; // store or state? both work (but stores needs $ symbol) 

    let kana = $state({})
    let ji = $derived(page.url.searchParams.get("ji") ?? "h") // add an option to switch query, with the default being "h"
    
    async function getKana(ji) {
        try{
        let response = await fetch(`http://localhost:8008/api/kana?ji=${ji}`);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        kana = await response.json()
        nextKana()   
        console.log(kana);
    } catch (error){
        console.log("An error occured", error);
    }}

    $effect(()=>{
            getKana(ji);    // get the argument from the reactive ji var, which will change the letter upon clicking the link
        })
    
    let entries = $derived(Object.entries(kana)) // Object.entries() to iterate an object
    let randomEntry = $state([])                 // Object.entries() returns an array of [key, value] pairs. so randomEntry would be something like ["あ", "a"]
    function nextKana() {                        // or randomEntry[0] for kana, and  randomEntry[1] for romaji
        randomEntry = entries[Math.floor(Math.random() * entries.length)] // equivalent to random.choice(entries) in python
    }

    let answer = $state("")
    function check() {
        if (answer === randomEntry[1]){
            answer = "" // reset the answer upon correct guess
            nextKana()
        }
    }
</script>
<nav>
    <a href="/">home</a>
    <a href="/text">words</a>
</nav>
<h1>Testing</h1>
<p>Homepage</p>
<a href="/?ji=h">Hiragana</a>
<a href="/?ji=k">Katakana</a>
<p style="font-size: 40px;">{randomEntry[0]}</p>
<input bind:value={answer} oninput={check}> <!--checking in every input made if input matches the answer-->

