<script>

    let naiyou = $state("")
    let timer                       // debounce steps: user types > cancel old timer > start new timer >
    async function sendText() {     // user types again > cancel old timer > start new timer >
        clearTimeout(timer)         // user stops > timer runs out > request is made
        timer = setTimeout(async () => {
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
            console.log(result);
            } catch (error){
                console.log("An error occured", error)
                alert("An error occured")
            }
        }, 500) // set a timer (in ms). wait for user to stop inputting for x ms before sending the request
    }

</script>

<textarea bind:value={naiyou} oninput={sendText}></textarea>
<p></p>