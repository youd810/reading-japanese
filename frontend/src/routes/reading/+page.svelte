<script>
    let time = $state(0);
    let interval = $state();
    let startTimestamp;

    const startTime = ()=>{
        clearInterval(interval)
        startTimestamp = Date.now() // Date.now() instead of time++ to prevent drifting
        interval = setInterval(() => {
            // flooring doesn't affect acurracy at all in this case; it's only there to hide decimals
            time = Math.floor((Date.now() - startTimestamp)/ 100) 
        }, 100)
    }
    let show = $state(false) 
    let text = $state("この世の中には「陰謀」が存在する")
    let cpm =  $derived((text.length / time)*600)  // 60 for s, 600 for ds, 60000 for ms
</script>

<button onclick={()=> {startTime(); show = false}}>start</button>
<button onclick={()=> {clearInterval(interval); show = true}}>stop</button>
<h1>{time}</h1>
<p>{text}</p>
{#if show && time > 0}
<p>your cpm is: {Math.round(cpm)}</p>
<button onclick={()=> time = 0}>reset</button>
{/if}