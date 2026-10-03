"""Seed content: the nine Raccoon Stories mnemonics, the cast, and the card decks.

Ported from the Raccoon Stories site so the prose lives in exactly one place.
Every card that has a `story` + `beat` points back at the paragraph of that
story which explains it -- that is what powers the reteach step after a lapse.
`beat` is a 0-based index into the story's `body` list.

Cards with no `story` are the plain T1 basics that never needed a mnemonic.
"""
from __future__ import annotations


def c(cid, lang, tier, prompt, answer, accept=None, hint=None, code=False, story=None, beat=None):
    return {
        "id": cid,
        "lang": lang,
        "tier": tier,
        "prompt": prompt,
        "answer": answer,
        "accept": accept or [],
        "hint": hint,
        "code": code,
        "story_id": story,
        "beat": beat,
    }


def _art(seed: str) -> str:
    return f"https://picsum.photos/seed/{seed}/1200/1500"


STORIES = [
    {
        "story_id": "raccoon-trail", "n": 1, "language": "HTML",
        "title": "The Raccoon's Trail", "concept": "href vs src",
        "scene": "A signpost in the woods, and a wife walking back through a cottage door.",
        "image_url": _art("raccoon-trail-forest"),
        "image_alt": "A wooded fork in the path beside a weathered wooden signpost",
        "body": [
            "The raccoon is hunting for his wife. At a fork in the woods he finds a signpost with an arrow carved into it, pointing off down the trail. She went that way. To follow it you leave where you are and travel to the destination. That is href: a pointer to somewhere else, the thing behind every link.",
            "But when he finally finds her, she moves back into the cottage and becomes part of your home. That is src: the real thing pulled inside your page, the thing behind every image and script.",
            "So a signpost points, the wife arrives. One sends you away, one brings content in.",
        ],
        "unpacking": "href = a signpost you walk to (link out). src = the wife moving in (content embedded in the page).",
    },
    {
        "story_id": "barn-and-coop", "n": 2, "language": "HTML",
        "title": "The Barn and the Coop", "concept": "section / article / aside / div",
        "scene": "Every animal and bird sorted into pens, plus one stray crate.",
        "image_url": _art("barn-coop-stalls"),
        "image_alt": "The inside of a warm barn with stalls for animals and a row of nesting boxes",
        "body": [
            "You stand in the middle of the barn, every animal and bird sorted into it. That whole building is a section: a big thematic grouping that holds related things together.",
            "Each stall holds one complete animal you could carry off and sell on its own. Self-contained, whole without the rest of the barn. That is an article.",
            "The small shed tacked onto the side holds the odd bits that do not belong to the main herd. That is an aside: related, but off to the side. And the plain unmarked crate you grab when nothing else fits, carrying no meaning at all? That is a div.",
        ],
        "unpacking": "section = the barn. article = a sellable stall. aside = the side shed. div = an empty crate.",
    },
    {
        "story_id": "farmhouse-deed", "n": 3, "language": "HTML",
        "title": "The Farmhouse Deed", "concept": "doctype / head / body + void elements",
        "scene": "Paperwork by the door, fields behind it, and one lone fish.",
        "image_url": _art("farmhouse-deed-door"),
        "image_alt": "The front of a rustic farmhouse with a deed nailed by the door",
        "body": [
            "On the front door hangs a deed proving this is a legitimate farm. That is the doctype: the one line that tells the browser which rules to follow.",
            "Beside it, a signboard and a stack of paperwork hold information about the farm that no visitor ever sees once inside. That is the head. The fields and buildings everyone actually walks through are the body.",
            "Now look at the shelf by the door. A single caught fish sits there with no matching other half, no partner, no twin. It just shows up, finished. That is a void element: img, br, input, meta. One appearance, and no closing tag, because there is nothing to close.",
        ],
        "unpacking": "deed / signboard / fields = doctype / head / body. A lone fish = a void tag with no closing pair.",
    },
    {
        "story_id": "farm-plot", "n": 4, "language": "CSS",
        "title": "farmerB and maya's Plot", "concept": "the box model",
        "scene": "Crops, tilled soil, a fence, and a strip of grass kept clear.",
        "image_url": _art("farm-plot-crops-fence"),
        "image_alt": "A tidy farm plot: crops, a ring of tilled soil, and a wooden fence",
        "body": [
            "In the morning light, farmerB tills and maya builds. The crops in the middle are the content, the thing you actually came to grow.",
            "farmerB tills a ring of loose soil hugging the crops so the roots can breathe. That ring is padding, and it sits inside the fence. Robin raises the fence around it. That fence is the border, and the padding never escapes past it.",
            "Outside the fence, maya leaves a strip of empty grass so Marnie's cows cannot trample in. That is the margin, and it pushes neighbours away from the outside.",
            "Then the town clock chimes and you water on the shorthand, following the hands as they sweep clockwise from twelve: top, right, bottom, left.",
        ],
        "unpacking": "content, padding, border, margin (inside out). Padding sits inside the fence, margin outside it. Shorthand runs clockwise from the top.",
    },
    {
        "story_id": "house-of-axes", "n": 5, "language": "CSS",
        "title": "Robin and Demetrius Run the House", "concept": "justify-content vs align-items",
        "scene": "Two partners, one hallway, one wall of shelves.",
        "image_url": _art("farmhouse-hallway-shelves"),
        "image_alt": "A wooden farmhouse hallway lined with shelves",
        "body": [
            "They are a couple, so each of them leads a direction. Robin walks the main hallway, arranging things along the way. That is justify-content, and it works along the main axis.",
            "Demetrius stands across from her, hanging things on the shelves that run the other way. That is align-items, and it works on the cross axis.",
            "Now flip flex-direction to column and the whole house rotates. They swap: Robin walks top to bottom and Demetrius goes across. The main axis is simply whatever flex-direction names.",
        ],
        "unpacking": "justify-content = the main axis (Robin, leading the hall). align-items = the cross axis (Demetrius, across from her). Flip the direction and the two swap roles.",
    },
    {
        "story_id": "harveys-board", "n": 6, "language": "CSS",
        "title": "Harvey's Price Board", "concept": "specificity",
        "scene": "A clinic where the bill climbs with importance.",
        "image_url": _art("clinic-wooden-price-board"),
        "image_alt": "A village clinic interior with a tall wooden board of prices",
        "body": [
            "At Harvey's clinic the bill climbs with how important the visit is. A routine element checkup costs 1.",
            "A class-level treatment costs 10. An ID-level specialist consultation costs 100. And an inline emergency house-call costs 1000.",
            "When two rules both apply, the more expensive one wins. Unless you write !important, and then Harvey simply bills you whatever he likes, ignoring the board entirely.",
        ],
        "unpacking": "inline 1000 beats ID 100 beats class 10 beats element 1. !important overrides the whole ladder.",
    },
    {
        "story_id": "loose-trades", "n": 7, "language": "JS",
        "title": "The Raccoon's Loose Trades", "concept": "== vs ===",
        "scene": "A woodland stall, a bundle of wood, and one honest scale.",
        "image_url": _art("woodland-market-scale"),
        "image_alt": "A woodland market stall with a brass weighing scale",
        "body": [
            "You offer the raccoon five wood and he shrugs. Five is five, close enough. He takes the string \"5\" as the number 5 and the deal goes through. That is ==, the loose trader who fudges types to make the trade.",
            "The honest scale beside him refuses. It will not read a string as a number, will not accept a near-miss. Number for number, or nothing. That is ===.",
            "One of them converts types to force a match. The other demands the same type and the same value, exactly.",
        ],
        "unpacking": "== converts types to force equality (\"close enough\"). === demands identical type AND value.",
    },
    {
        "story_id": "iridium-rods", "n": 8, "language": "JS",
        "title": "Your Iridium Rods", "concept": "the event loop",
        "scene": "Two lines in the water at dusk: quick nibbles, and one slow legend.",
        "image_url": _art("fishing-dock-dusk-rods"),
        "image_alt": "A wooden dock at dusk with two fishing rods over still water",
        "body": [
            "You and your partner are fishing side by side. Every cast, tiny fish nibble instantly, reeled in the moment they bite, before anything else on the line gets a turn. Those quick nibbles are the microtasks, the promises waiting to resolve.",
            "The huge legendary fish on the second rod only bites after a long scheduled wait, and it refuses to bite until every quick nibble has been cleared first. That is the macrotask, the setTimeout at the back of the queue.",
            "So the order is fixed: the small fish drain completely, then the big one surfaces.",
        ],
        "unpacking": "Microtasks (instant nibbles) drain completely first. Macrotasks (the slow legendary fish) only run after the microtask queue is empty.",
    },
    {
        "story_id": "who-owns-this", "n": 9, "language": "JS",
        "title": "Who Owns this Today?", "concept": "this binding",
        "scene": "Five little scenes in one town, all asking the same question.",
        "image_url": _art("pelican-town-village-evening"),
        "image_alt": "A wide village scene at evening with a barn, woods, and a lone raccoon",
        "body": [
            "The raccoon, all alone in the woods with no owner, is the default: this points at the wild, the global.",
            "Robin chops wood, and the owner is whoever stands right before the dot, so this is Robin. That is the implicit rule.",
            "Harvey calls you in by name, asking for farmerB specifically rather than whoever happens to be around. That is explicit, and call, apply and bind set this on demand. Robin builds a brand-new barn, and with new, this becomes that fresh barn.",
            "Finally the barn animals do not care who is calling. They behave exactly as they learned at home, lexically, from wherever they were born. Those are arrow functions, and they ignore every rule above.",
        ],
        "unpacking": "default = the lost raccoon. implicit = the owner before the dot. explicit = Harvey naming you. new = the new barn. arrow = animals acting like home.",
    },
]

CAST = [
    {"name": "Robin", "role": "The builder. Borders, construction, and the new keyword."},
    {"name": "Demetrius", "role": "Stands across from her on the cross axis."},
    {"name": "Harvey", "role": "Charges more the more important you are. The specificity ladder."},
    {"name": "The raccoon", "role": "Always searching. Pointers, the default this, and loose trades."},
    {"name": "Linus", "role": "Sneaks things up out of the mines. Hoisting, next chapter."},
    {"name": "Your iridium rods", "role": "Quick nibbles and one slow legend. The event loop."},
    {"name": "The barn and coop", "role": "Every animal sorted into pens. Semantic elements."},
    {"name": "The town clock", "role": "Read it once, clockwise. Shorthand order."},
    {"name": "farmerB and maya", "role": "The two farmers who walk every layout."},
]

# --- tier 2 / 3: the fiddly bits, straight out of the stories ----------------
STORY_CARDS = [
    # 1. href vs src
    c("html-href", "HTML", 1, "Which attribute points off to somewhere else -- the thing behind every link?",
      "href", accept=["href attribute"], hint="A signpost you walk to.", story="raccoon-trail", beat=0),
    c("html-src", "HTML", 1, "Which attribute pulls a real file into your own page -- the thing behind every image and script?",
      "src", accept=["src attribute"], hint="The wife moving in.", story="raccoon-trail", beat=1),
    # 2. section / article / aside / div
    c("html-section", "HTML", 1, "Which element is a large thematic grouping that holds related things together?",
      "<section>", accept=["section"], hint="The whole barn.", story="barn-and-coop", beat=0),
    c("html-article", "HTML", 1, "Which element is self-contained -- whole on its own, without the rest of the page?",
      "<article>", accept=["article"], hint="A stall you could sell on its own.", story="barn-and-coop", beat=1),
    c("html-aside", "HTML", 1, "Which element holds content that is related but off to the side?",
      "<aside>", accept=["aside"], hint="The small shed tacked on.", story="barn-and-coop", beat=2),
    c("html-div", "HTML", 1, "Which element carries no meaning at all -- the container of last resort?",
      "<div>", accept=["div"], hint="The unmarked crate.", story="barn-and-coop", beat=2),
    # 3. doctype / head / body / void
    c("html-doctype", "HTML", 2, "Which single line tells the browser which set of rules to follow?",
      "<!DOCTYPE html>", accept=["doctype", "<!doctype html>"], hint="The deed on the door.", story="farmhouse-deed", beat=0, code=True),
    c("html-head", "HTML", 2, "Which element holds metadata that a visitor never sees rendered in the page?",
      "<head>", accept=["head"], hint="The signboard nobody reads once inside.", story="farmhouse-deed", beat=1),
    c("html-void", "HTML", 2, "What do we call elements that appear once and have no closing tag?",
      "void elements", accept=["void", "void element", "self-closing", "empty elements"],
      hint="The lone fish with no partner.", story="farmhouse-deed", beat=2),
    # 4. box model
    c("css-padding", "CSS", 1, "Which layer hugs the content, inside the border?",
      "padding", hint="The tilled soil around the crops.", story="farm-plot", beat=1),
    c("css-border", "CSS", 1, "Which layer sits outside the padding and never lets it escape?",
      "border", hint="Robin's fence.", story="farm-plot", beat=1),
    c("css-margin", "CSS", 1, "Which layer pushes neighbours away, on the outside?",
      "margin", hint="The strip of grass outside the fence.", story="farm-plot", beat=2),
    c("css-shorthand-order", "CSS", 1, "In a four-value shorthand such as margin: a b c d, which side does the first value set?",
      "top", hint="Read the town clock clockwise from twelve.", story="farm-plot", beat=3),
    # 5. justify vs align
    c("css-justify", "CSS", 1, "Which property arranges items along the main axis?",
      "justify-content", accept=["justify"], hint="Robin walks the main hallway.", story="house-of-axes", beat=0),
    c("css-align", "CSS", 1, "Which property arranges items on the cross axis?",
      "align-items", accept=["align"], hint="Demetrius stands across from her.", story="house-of-axes", beat=1),
    c("css-axis-flip", "CSS", 1, "With flex-direction: column, which direction does align-items now control?",
      "horizontal", accept=["the horizontal axis", "left to right", "inline axis", "horizontally", "across"],
      hint="Flip the house and they swap.", story="house-of-axes", beat=2),
    # 6. specificity
    c("css-spec-element", "CSS", 2, "On Harvey's board, what does a plain element selector cost?",
      "1", hint="A routine checkup.", story="harveys-board", beat=0),
    c("css-spec-class", "CSS", 2, "What does a class selector cost?",
      "10", hint="A class-level treatment.", story="harveys-board", beat=1),
    c("css-spec-id", "CSS", 2, "What does an ID selector cost?",
      "100", hint="A specialist consultation.", story="harveys-board", beat=1),
    c("css-spec-inline", "CSS", 2, "What does an inline style attribute cost?",
      "1000", hint="The emergency house-call.", story="harveys-board", beat=1),
    c("css-spec-important", "CSS", 2, "What overrides the entire specificity ladder?",
      "!important", hint="Harvey bills you whatever he likes.", story="harveys-board", beat=2, code=True),
    # 7. == vs ===
    c("js-loose-eq", "JS", 1, "Which operator converts types to force a match?",
      "==", accept=["==", "loose equality"], hint="The loose trader.", story="loose-trades", beat=0, code=True),
    c("js-strict-eq", "JS", 1, "Which operator demands the same type AND the same value?",
      "===", accept=["===", "strict equality"], hint="The honest scale.", story="loose-trades", beat=1, code=True),
    # 8. event loop
    c("js-microtask", "JS", 2, "Which queue drains completely before the next macrotask is allowed to run?",
      "microtask queue", accept=["microtask", "the microtask queue", "microtasks"], hint="The quick nibbles.", story="iridium-rods", beat=0),
    c("js-macrotask", "JS", 2, "A setTimeout callback is which kind of task?",
      "macrotask", accept=["a macrotask", "macrotasks", "macro task"], hint="The slow legendary fish.", story="iridium-rods", beat=1),
    # 9. this binding
    c("js-this-default", "JS", 3, "In a plain function call with no owner, what does this point at?",
      "the global object", accept=["global object", "the global", "window", "global", "the global object (undefined in strict mode)", "undefined in strict mode"],
      hint="The raccoon alone in the woods.", story="who-owns-this", beat=0),
    c("js-this-implicit", "JS", 3, "In obj.method(), what does this point at?",
      "obj", accept=["obj", "the object before the dot", "the object it was called on", "whatever stands before the dot", "the owner before the dot"],
      hint="The owner before the dot.", story="who-owns-this", beat=1),
    c("js-this-explicit", "JS", 3, "Which three methods set this on demand?",
      "call, apply and bind", accept=["call apply bind", "call, apply, bind", "call apply and bind", "bind call apply", "call/apply/bind"],
      hint="Harvey calls you in by name.", story="who-owns-this", beat=2),
    c("js-this-new", "JS", 3, "When you call a function with new, what does this become?",
      "the new object", accept=["the newly created object", "the new object", "a new object", "the freshly created object", "the brand-new object"],
      hint="Robin's brand-new barn.", story="who-owns-this", beat=2),
    c("js-this-arrow", "JS", 3, "Which functions ignore every this rule and take this lexically from where they were defined?",
      "arrow functions", accept=["arrows", "arrow function", "=> functions"], hint="The animals act like home.", story="who-owns-this", beat=3),
]

# --- tier 1: the basics that never needed a story ---------------------------
BASIC_CARDS = [
    # HTML
    c("html-p", "HTML", 1, "Which element marks a paragraph of text?", "<p>", accept=["p", "<p></p>"]),
    c("html-a", "HTML", 1, "Which element creates a hyperlink?", "<a>", accept=["a", "anchor", "<a></a>"]),
    c("html-ol", "HTML", 1, "Which list element numbers its items?", "<ol>", accept=["ol", "ordered list", "ordered"]),
    c("html-ul", "HTML", 1, "Which list element gives bullets?", "<ul>", accept=["ul", "unordered list", "unordered"]),
    c("html-alt", "HTML", 1, "Which image attribute supplies the text shown when the image fails to load?", "alt"),
    c("html-br", "HTML", 1, "Which element forces a line break and has no closing tag?", "<br>", accept=["br", "<br/>", "<br />"]),
    c("html-tr", "HTML", 1, "Which element defines a row in a table?", "<tr>", accept=["tr"]),
    c("html-th", "HTML", 1, "Which table element defines a header cell?", "<th>", accept=["th"]),
    c("html-label-for", "HTML", 1, "Which attribute ties a label to the input it describes?", "for"),
    c("html-form-attrs", "HTML", 1, "Which two attributes does a form need in order to send its data?", "action and method", accept=["action and method", "action, method", "method and action", "action + method"]),
    c("html-meta-charset", "HTML", 1, "Which tag declares the page's character encoding?", '<meta charset="utf-8">', accept=['meta charset', '<meta charset="utf-8">', "meta charset=utf-8", '<meta charset="UTF-8">']),
    c("html-title", "HTML", 1, "Which element sets the text shown on the browser tab?", "<title>", accept=["title"]),
    c("html-link-css", "HTML", 1, "Which tag links an external stylesheet?", '<link rel="stylesheet">', accept=['link rel="stylesheet"', "link", '<link rel="stylesheet" href="...">']),
    c("html-defer", "HTML", 1, "Which script attribute makes the script run only after the HTML has been parsed?", "defer"),
    c("html-nav", "HTML", 1, "Which semantic element marks the primary navigation block?", "<nav>", accept=["nav"]),
    c("html-footer", "HTML", 1, "Which semantic element marks the bottom of a page or section?", "<footer>", accept=["footer"]),
    c("html-main", "HTML", 1, "Which semantic element marks the single main content of the page?", "<main>", accept=["main"]),
    c("html-select", "HTML", 1, "Which element creates a dropdown of choices?", "<select>", accept=["select"]),
    c("html-div-span", "HTML", 1, "What is the difference between div and span?", "div is block-level, span is inline", accept=["div is block and span is inline", "div block span inline", "block vs inline", "block and inline", "div is block, span is inline"]),
    c("html-strong", "HTML", 1, "What is the difference between strong and b?", "strong carries importance, b is only visual", accept=["strong is semantic and b is visual", "strong means importance, b is visual", "semantic vs visual", "strong is important b is bold"]),
    c("html-checkbox", "HTML", 1, "Which input type lets a user tick several options independently?", "checkbox", accept=['type="checkbox"', "checkbox", "checkboxes"]),
    c("html-nesting", "HTML", 1, "Which rule must every nested element follow?", "close in reverse order of opening", accept=["close in reverse order", "proper nesting", "last opened first closed", "close in the reverse order they were opened", "nest correctly"]),
    # CSS
    c("css-class-selector", "CSS", 1, "Which selector targets every element with class note?", ".note", accept=[".note", "dot note", ". (dot)"]),
    c("css-id-selector", "CSS", 1, "Which selector targets the element with id header?", "#header", accept=["#header", "hash header", "# (hash)"]),
    c("css-color", "CSS", 1, "Which property sets the colour of text?", "color"),
    c("css-background", "CSS", 1, "Which property sets a background fill?", "background-color", accept=["background", "background-color"]),
    c("css-em", "CSS", 1, "Which unit is relative to the element's own font size?", "em"),
    c("css-rem", "CSS", 1, "Which unit is relative to the root font size?", "rem"),
    c("css-font-weight", "CSS", 1, "Which property makes text bold?", "font-weight"),
    c("css-text-align", "CSS", 1, "Which property centres text horizontally?", "text-align", accept=["text-align", "text-align: center"]),
    c("css-list-style", "CSS", 1, "Which property removes the bullets from a list?", "list-style", accept=["list-style", "list-style: none", "list-style-type"]),
    c("css-comment", "CSS", 1, "How do you write a CSS comment?", "/* comment */", accept=["/* */", "/**/", "slash star", "/* ... */"], code=True),
    c("css-font-family", "CSS", 1, "Which property chooses the typeface?", "font-family"),
    c("css-display-none", "CSS", 1, "Which display value hides an element AND removes it from the layout?", "display: none", accept=["display none", "none", "display:none"], code=True),
    c("css-visibility", "CSS", 1, "Which property hides an element but keeps the space it occupied?", "visibility", accept=["visibility", "visibility: hidden"]),
    c("css-border-radius", "CSS", 1, "Which property rounds an element's corners?", "border-radius"),
    c("css-hover", "CSS", 1, "Which pseudo-class styles an element while the pointer is over it?", ":hover", accept=[":hover", "hover"]),
    c("css-line-height", "CSS", 1, "Which property controls the spacing between lines of text?", "line-height"),
    c("css-universal", "CSS", 1, "Which selector matches every element on the page?", "*", accept=["*", "asterisk"]),
    c("css-child-combinator", "CSS", 1, "Which combinator targets only direct children?", ">", accept=[">", "the > combinator", "child combinator"]),
    c("css-flex", "CSS", 1, "Which declaration turns an element into a flex container?", "display: flex", accept=["display flex", "display:flex", "flex"], code=True),
    c("css-box-sizing", "CSS", 1, "Which declaration makes width include padding and border?", "box-sizing: border-box", accept=["box-sizing border-box", "border-box", "box-sizing:border-box"], code=True),
    c("css-z-index", "CSS", 1, "Which property controls which overlapping element sits on top?", "z-index"),
    c("css-position", "CSS", 1, "Which position value pins an element relative to the viewport?", "fixed", accept=["position: fixed", "fixed"]),
    # JS
    c("js-const", "JS", 1, "Which keyword declares a value you will not reassign?", "const"),
    c("js-let", "JS", 1, "Which keyword declares a value you will reassign?", "let"),
    c("js-template", "JS", 1, "Which syntax embeds a variable inside a string?", "${}", accept=["${}", "template literal", "backticks", "template string", "${ }"]),
    c("js-typeof-string", "JS", 1, 'What is typeof "5"?', "string", accept=['"string"', "string"]),
    c("js-arrow", "JS", 1, "How do you write a block-bodied arrow function that takes no arguments?", "() => {}", accept=["() => {}", "()=>{}", "const f = () => {}", "() => { }"], code=True),
    c("js-array-literal", "JS", 1, "Which literal creates an array?", "[]", accept=["[]", "square brackets", "brackets"]),
    c("js-object-literal", "JS", 1, "Which literal creates an object?", "{}", accept=["{}", "curly braces", "braces"]),
    c("js-length", "JS", 1, "Which property gives the number of items in an array?", ".length", accept=["length", ".length"]),
    c("js-push", "JS", 1, "Which method adds an item to the END of an array?", "push()", accept=["push", "push()", "array.push"]),
    c("js-pop", "JS", 1, "Which method removes the LAST item of an array?", "pop()", accept=["pop", "pop()"]),
    c("js-queryselector", "JS", 1, "Which method returns the first element matching a CSS selector?", "querySelector()", accept=["querySelector", "queryselector", "document.querySelector()"]),
    c("js-addeventlistener", "JS", 1, "Which method attaches a click handler to an element?", "addEventListener()", accept=["addeventlistener", "addEventListener", "addEventListener('click', fn)", ".onclick"]),
    c("js-console", "JS", 1, "What does console.log() do?", "prints to the developer console", accept=["print to the console", "prints to console", "logs to the console", "writes to the console", "logs a message"]),
    c("js-typeof-null", "JS", 1, "What is typeof null?", '"object"', accept=["object", '"object"', "object (a famous quirk)"]),
    c("js-parseint", "JS", 1, "Which function converts a string into a whole number?", "parseInt()", accept=["parseint", "parseInt", "parseInt()", "Number()"]),
    c("js-forof", "JS", 1, "Which loop visits each item of an array directly, without an index?", "for...of", accept=["for of", "for...of", "for-of", "for of loop"]),
    c("js-map", "JS", 1, "Which array method runs a function on every item and returns a NEW array?", "map()", accept=["map", "map()", ".map"]),
    c("js-filter", "JS", 1, "Which array method keeps only the items that pass a test?", "filter()", accept=["filter", "filter()", ".filter"]),
    c("js-comment", "JS", 1, "How do you write a single-line comment?", "//", accept=["//", "two slashes", "// comment"]),
    c("js-spread", "JS", 1, "Which operator spreads an array out into individual items?", "...", accept=["...", "spread", "the spread operator"]),
    c("js-await", "JS", 1, "Which keyword pauses an async function until a promise settles?", "await"),
    c("js-plus-coerce", "JS", 1, 'What is the result of 1 + "1"?', '"11"', accept=['"11"', "11", "11 (string)", "the string 11"]),
    c("js-falsy", "JS", 1, "Name three falsy values.", "0, '' and null", accept=["0 '' null", "0, empty string, null", "0 '' null undefined NaN false", "false 0 '' null undefined nan", "0, null, undefined", "0, empty string, null, undefined, NaN, false"]),
]

CARDS = BASIC_CARDS + STORY_CARDS

# --- pair / season meta -----------------------------------------------------
PAIR = {
    "members": ["farmerB", "maya"],
    "exam_date": None,          # set from the API or by editing this then re-seeding
    "timezone": "Asia/Kolkata",
    "current_tier": {"HTML": 1, "CSS": 1, "JS": 1},
}
