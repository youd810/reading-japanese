<script>
    let time = $state(0);
    let interval = $state()

    const startTime = ()=>{
        clearInterval(interval)
        interval = setInterval(() => {
        time++
        }, 1000)
    }
</script>

<button onclick={startTime}>start</button>
<button onclick={()=> clearInterval(interval)}>pause</button>
<button onclick={()=> time = 0}>reset</button>
<h1>{time}</h1>