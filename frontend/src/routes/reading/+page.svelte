<title>Reading</title>
<script>
    import Switch from "svelte-toggle-switch";
    import { fade, fly, slide } from "svelte/transition";

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
            console.log("tick")
            // flooring doesn't affect acurracy at all in this case; it's only there to hide decimals
            time = Math.floor((Date.now() - startTimestamp)/ 10) 
        }, 10)
    }

    $effect(()=> {
        return ()=> {
            clearInterval(interval) // cleanup in case user starts a timer then navigate away without stopping it
        }
    })

    let show = $state(false) 
    let start = $state(false)
    let text = $state("")
    let count = $state()
    let cpm =  $derived((count / time)*6000)  // 60 for s, 600 for ds, 60000 for ms

    // auto scroll for cpm/reset button
    let resultEle
    $effect(() => {
        if (show && time) { // time > 0 is really just a boolean statement
            resultEle?.scrollIntoView({behavior: "smooth"})
        }
    })

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
    <!--padding only works with str so convert first-->
    <p style="font-size: 40px;"><b>{String(minute).padStart(2,"0")}:{String(second).padStart(2,"0")}:{String(notms).padStart(2,"0")}</b></p>

    {#if !start && !time} 
        <!-- actually i prefer this approach over toggling the variable with `!start`, just less confusion overall-->
        <button class="button-timer" onclick={()=> {startTime(); show = false; start = true}}>START</button>
    {:else}
        <button class="button-timer hidden" onclick={()=> {startTime(); show = false; start = true}}>START</button>
    {/if}
</div>

<Switch colorScheme="red" size="sm" bind:value={fieldValue} design="multi" options={["Literature", "Politics", "Technology"]} label="Field" rounded="true"/>
<Switch colorScheme="red" size="sm" bind:value={diffValue} design="multi" options={["Easy", "Medium", "Hard"]} label="Difficulty"/>

<div class="controls">
    {#key text} <!-- makes it so the transition happens on text change-->
        <p style="font-size: 22px;" in:fly={{x: 200, duration: 250}}>{@html text}</p>
    {/key}
    <br>
    {#if start || time}
        <p style="font-size: 40px;"><b>{String(minute).padStart(2,"0")}:{String(second).padStart(2,"0")}:{String(notms).padStart(2,"0")}</b></p>
    {:else}
        <p class="hidden" style="font-size: 40px;">you aren't supposed to see this</p>
    {/if}

    <div bind:this={resultEle}>
        {#if show && time}
            <p style="display: flex; flex-direction: column; align-items: center">Your cpm is: {Math.round(cpm)}</p>
            <button class="button-timer" onclick={()=> time = 0}>Reset</button>
        {/if}
    </div>
    {#if start}
        <button class="button-timer" onclick={()=> {clearInterval(interval); show = true; start = false}}>STOP</button>
    {/if}
</div>
