<script>
    let kana = $state({})
    
    async function getKana() {
        try{
        let response = await fetch("http://localhost:8008/api/kana");
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
            getKana();
        })
    
    let entries = $derived(Object.entries(kana)) // Object.entries() to iterate an object
    let randomEntry = $state([])                 // Object.entries() returns an array of [key, value] pairs. so randomEntry would be something like ["あ", "a"]
    function nextKana() {                        // or randomEntry[0] for kana, and  randomEntry[1] for romaji
        randomEntry = entries[Math.floor(Math.random() * entries.length)] // equivalent to random.choice(kana) in python
    }

    let answer = $state("")
    function check() {
        if (answer === randomEntry[1]){
        answer = "" // reset the answer upon correct guess
        nextKana()
        }
    }
</script>

<h1>Testing</h1>
<p>Homepage</p>
<p style="font-size: 40px;">{randomEntry[0]}</p>
<input bind:value={answer} oninput={check}> <!--checking in real time if input matches the answer-->

