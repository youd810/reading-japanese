<script>
    let src = $state("https://www.youtube.com/embed/BlPIXRHMCZ0")

    function handleToggle(e) {
        if (!e.target.open) {
            src = ""
        } else {
            src = "https://www.youtube.com/embed/BlPIXRHMCZ0"
        }
    }
</script>

<h1>SOURCES</h1>
<h2>Tools</h2>
<div class="sauce">
<a href="https://github.com/yomidevs/jmdict-yomitan?tab=readme-ov-file#jmdict-for-yomitan">JMDict English (legacy version)</a>
<a href="https://github.com/FooSoft/yomichan">Inspiration for the one-click dictionary</a>

<h2>Reading</h2>
<a href="https://www.aozora.gr.jp/cards/000329/files/18376_12100.html">桃太郎 (literature easy)</a>
<a href="https://www.aozora.gr.jp/cards/000148/files/789_14547.html">吾輩は猫である (literature medium)</a> 
<a href="https://www.aozora.gr.jp/cards/000125/files/1317_23268.html">黒死館殺人事件 (literature hard)</a> 
<a href="https://news.web.nhk/news/easy/ne2026030911336/ne2026030911336.html">イラン　新しいトップにハメネイ師の息子モジタバ師を選んだ (politics easy)</a> 
<a href="https://www.aozora.gr.jp/cards/000296/files/47061_29420.html">学問のすすめ (politics medium)</a>  
<a href="https://www.shugiin.go.jp/internet/itdb_annai.nsf/html/statics/shiryo/dl-constitution.htm">日本国憲法 (politics hard)</a> 
<a href="https://web-japan.org/kidsweb/ja/cool/25/202508_coding_ja.html">コードを解き明かせ！日本で広がる楽しいプログラミング学習 (technology easy)</a> 
<a href="https://ja.wikipedia.org/wiki/%E6%88%A6%E8%89%A6 ">戦艦 (technology medium)</a>
<a href="https://www.j-platpat.inpit.go.jp/c1801/PU/JP-2000-330832/11/ja">パーティションデータの変換システム、変換方法および記録媒体 (technology hard)</a>


<h1>その他</h1>
<a href="https://github.com/youd810/reading-japanese">Github</a>
</div>
<details ontoggle={handleToggle}>
<summary>An Actually Good Advice for Beginners</summary>
    <iframe title="test" width="720" height="405" src={src}>
    </iframe>
</details>