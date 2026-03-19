<script>
    import Switch from "svelte-toggle-switch";

    // stopwatch logic
    let time = $state(0);
    let minute = $derived(Math.floor(time/6000))
    let second = $derived(Math.floor(time%6000/100));
    let notms = $derived(time%100) // idk how i came up with all this

    let interval = $state();
    let startTimestamp;

    const startTime = ()=>{
        clearInterval(interval)
        startTimestamp = Date.now() // Date.now() instead of time++ to prevent drifting
        interval = setInterval(() => {
            // flooring doesn't affect acurracy at all in this case; it's only there to hide decimals
            time = Math.floor((Date.now() - startTimestamp)/ 10) 
        }, 10)
    }

    let show = $state(false) 
    let start = $state(false)
    let text = $state("")
    let count = $state()
    let cpm =  $derived((count / time)*6000)  // 60 for s, 600 for ds, 60000 for ms

    // text logic
    async function getText(field, diff) {
        try{
        let response = await fetch(`http://localhost:8008/api/reading?field=${field}&diff=${diff}`);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        let result = await response.json()
        text = result.text
        count = result.count
        clearInterval(interval)
        time = 0
        console.log(text);
    } catch (error){
        console.log("An error occured", error);
    }}

    // note to self: $effect runs when any reactive state it reads changes
    // so this will run whenever fieldValue or diffValue changes
    // which means no need for if statements for which text should be displayed 
    $effect(()=>{
        getText(fieldValue, diffValue);  

    })

    let fieldValue = $state("Literature")
    let diffValue = $state("Easy")
</script>
<div class="controls">
    {#if start === false} <!-- actually i prefer this approach over toggling the variable with `!start`, just less confusion overall-->
        <button onclick={()=> {startTime(); show = false; start = true}}>start</button>
    {:else}
        <button onclick={()=> {clearInterval(interval); show = true; start = false}}>stop</button>
    {/if}
    <!--padding only works with str so convert first-->
    <p style="font-size: 40px;"><b>{String(minute).padStart(2,"0")}:{String(second).padStart(2,"0")}:{String(notms).padStart(2,"0")}</b></p>
</div>

<Switch colorScheme="red" size="sm" bind:value={fieldValue} design="multi" options={["Literature", "Politics", "Technology"]} label="Field" rounded="true"/>
<Switch colorScheme="red" size="sm" bind:value={diffValue} design="multi" options={["Easy", "Medium", "Hard"]} label="Difficulty"/>

<div class="controls">
<p style="font-size: 20px;">{@html text}</p>
<br>
<p style="font-size: 40px;"><b>{String(minute).padStart(2,"0")}:{String(second).padStart(2,"0")}:{String(notms).padStart(2,"0")}</b></p>

{#if show && time > 0}
<p>your cpm is: {Math.round(cpm)}</p>
<button onclick={()=> time = 0}>reset</button>
{/if}
{#if start === false}
<button onclick={()=> {startTime(); show = false; start = true}}>start</button>
{:else}
<button onclick={()=> {clearInterval(interval); show = true; start = false}}>stop</button>
{/if}
</div>
