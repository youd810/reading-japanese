<script>

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

    let words = $state([])
    let wordcount = $state(0)

</script>
<nav>
    <a href="/">home</a>
    <a href="/text">words</a>
</nav>
<br>
<textarea bind:value={naiyou} oninput={sendText} style="font-size: 16px;"></textarea>
<p>Word count estimation: {wordcount}</p>
<p style="font-size: 16px;">{words}</p>