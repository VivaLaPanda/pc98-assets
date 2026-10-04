# Panda's Room: research notes (2026-10-03)

Scope: web research for the "Panda's Room" page on vivalapanda.moe. Covers how PC-98-era adventure games
signalled hotspots, VN dialogue conventions, and draft dialogue. No site files were modified.
Quotes are kept under ~15 words. Everything else is paraphrased.

---------------------------------------------------------------------------------------------------
## 0. Objects mapped to Panda's real services (per the user's mid-task message)

The user said the objects should map to their *real* services and pointed at smithdev.io.
smithdev.io now 301-redirects to panda.moe, which redirects to vivalapanda.moe. The 2020 Wayback snapshot
(Angular bundle `main.e914494afd9817b87a5d.bundle.js`) shows it was Panda's previous personal site, with:

- an accounts list: GitHub (VivaLaPanda), Stack Overflow, Twitter (@_vivalapanda, the old handle),
  LinkedIn, Kitsu (Anime List), LessWrong 2.0, Steam, email, and Good Judgment Open (forecasting);
- a `/read` **Reading List** of cards (title, author, genre, blurb, a pull quote). Fiction: The Wind-Up Bird
  Chronicle, Mort (Discworld), A Practical Guide to Evil, HPMOR, Overgeared, I Shall Seal the Heavens
  (the blurb mentions "over 1600 chapters"). Non-fiction: **Seeing Like a State**, How Asia Works, Open Borders,
  Rationality: A-Z, Surely You're Joking Mr. Feynman. Blogs: Slate Star Codex, Shtetl-Optimized;
- a "Blog" nav link to Medium (now replaced by Substack).

Current links on vivalapanda.moe (from contact.html and others): email me@panda.moe, Twitter/X @vivalapanda,
Signal (a signal.me link), Discord handle `vivalapanda` (a handle, not a link), Substack vlpanda.substack.com,
GitHub VivaLaPanda (pc98-assets, uta-stream, microtemplate), and the site's own radio page (radio.html,
"Panda's Chamber of Vibes", which runs on UtaStream, Panda's Go radio backend).

Live checks (2026-10-03):
- **Bluesky @vivalapanda.moe**: exists and is active (display name "Panda", ~1.1k posts, ~700 followers, bio uses the
  Substack tagline). This is the main candidate for the window.
- **Letterboxd**: `letterboxd.com/vivalapanda/rss/` and `/films/` return 404, so there is **no Letterboxd account
  under that name** (it may exist under a different name, so ask the user).
- Kitsu (VivaLaPanda): exists, last updated 2021-09 (stale). AniList: exists with 1 anime (basically empty).
  Steam (VivaLaPanda): exists. LessWrong: exists. Goodreads: none found (the user plans to make one).

Proposed mapping (core five and extras):

| Object | Service | Status |
|---|---|---|
| PC on desk (CRT glow) | GitHub `VivaLaPanda` | real, active |
| Bookshelf | Reading list (revive smithdev.io's list; Goodreads, BookWyrm or Open Library later) | list exists in the archive; a new service is planned |
| Window with city lights | Bluesky `@vivalapanda.moe` (second choice in the menu: Twitter/X `@vivalapanda`) | real, active |
| Phone on the bed | Discord `vivalapanda` (copy the handle) and Signal (link) | real |
| TV | **Letterboxd not found.** Options: Steam (TV plus console), or an anime/watch list (Kitsu is stale), or Letterboxd if the user has or makes one | needs a decision |
| *extra:* newspaper on the desk | Substack, "Panda's Portentous Portal" | real (the blog nav already uses a PC-98 newspaper icon) |
| *extra:* stereo / boombox | /radio.html (on-site) | real, internal link |
| *optional:* envelope | email me@panda.moe | real |
| *optional (old site):* Magic 8-ball = Good Judgment Open; suit in the closet = LinkedIn; console = Steam | | old accounts, so check whether they are still wanted |

Reading-list backends, if the user doesn't want Goodreads:
- **BookWyrm**: open-source, federated over ActivityPub, with to-read, reading and read shelves plus lists. It
  federates with Mastodon. It does not federate with Bluesky. [BookWyrm README](https://github.com/joachimesque/bookwyrm)
- **Open Library** reading log: Want to Read, Currently Reading and Already Read. Logs for new accounts have been
  public by default since May 2020, and an API can fetch a public user's shelves, so the bookshelf could show
  what's actually on it. [OL blog](https://blog.openlibrary.org/2020/05/26/reading-logs-going-public-helping-book-lovers-share/)
- Or self-host: re-create smithdev.io's /read cards as a PC-98 page. The data already exists in the archived bundle.

---------------------------------------------------------------------------------------------------
## 1. How PC-98-era adventure games signalled interactive objects

### 1a. The lineage: verb menus, then cursors
- **Command-selection menus** came from *Hokkaido Rensa Satsujin* (1984), which replaced the text parser with
  selectable verbs. *Portopia*'s Famicom port popularised them, and parsers had largely gone from Japanese
  adventures within about a year. [LP Archive, Portopia interlude](https://lparchive.org/The-Portopia-Serial-Murder-Case/Update%2004/);
  [HG101 Hokkaido](https://www.hardcoregaming101.net/hokkaido-rensa-satsujin-ohotsuku-ni-kiyu/)
- PC-98 games such as *De Ja* show the typical verb bar (Examine, Talk, Take, Use, Move, plus context verbs).
  "Examine" lets you point at specific spots in the picture. [MacVenture/De Ja on Wikipedia](https://en.wikipedia.org/wiki/MacVenture);
  [Giant Bomb](https://www.giantbomb.com/games/3030-28876/)
- **Hardware reason for static, menu-driven scenes:** the PC-98 had no hardware sprites and drew 640x400 in 16 colours
  (from a 4096-colour palette), so redraws were slow. Menus and still pictures suited it, and dithering faked
  extra colours. [VOGONS thread](https://www.vogons.org/viewtopic.php?p=1234288); [TV Tropes: PC-98](https://www.tvtropes.org/pmwiki/pmwiki.php/Platform/PC98)

### 1b. Game by game
| Game | How interactive things were signalled | Takeaway for Panda's Room |
|---|---|---|
| **Snatcher** (PC-88 1988, Sega CD 1994) | Menu of verbs (Look, Investigate, Talk, Ask, Move, Use Metal Gear) with the object as a sub-choice ("LOOK > POSTER"). No cursor for investigating. You repeat Look/Investigate until something new happens, and new context verbs then appear. Repeat examines yield new jokes, and Metal Gear plays *tsukkomi* (the straight man) to Gillian. The Outer Heaven bar hides Konami easter eggs in examine text. NB: the 3x3, 9-sector grid in the Sega CD version is the *shooting* mode, not investigation. | Escalating lines on repeat clicks reward curiosity, and Panda can be her own tsukkomi. An object-list menu is a native PC-98 idiom. [HG101](https://www.hardcoregaming101.net/snatcher/), [ja.wikipedia SNATCHER](https://ja.wikipedia.org/wiki/SNATCHER), [classic-games.net](https://www.classic-games.net/genesis/snatcher), [Racketboy (grid)](https://racketboy.com/retro/meta-review-snatcher-sega-cd), [LP Archive](https://lparchive.org/Snatcher/Update%202/) |
| **Policenauts** (PC-98, 1994) | A free cursor: click anything in the scene and a list of possible actions pops up, with a menu button available at any time. The opening is Jonathan's own apartment, and examining his things tells you his backstory: the ex-wife's photo, his partner's photo, his gun, old case papers, an answering machine with a wrong number ("Thank you for wasting my time."). | **This is the template.** A host's room where each object reveals a bit of who they are, voiced dryly. [LP Archive Update 01](https://lparchive.org/Policenauts/Update%2001), [Sega-16 review](https://www.sega-16.com/?p=30395) |
| **Doukyuusei** (Elf, PC-98, 1992) | Point-and-click with context icons. ja.wikipedia says the clickable **icons change shape according to the situation and purpose**, and Doukyuusei popularised clicking different parts of a scene or character for different text. Kakyuusei (1995) is described as *dropping* the icon-cursor observation system. | A cursor that changes over a hotspot is authentic PC-98 Elf UI. [ja.wikipedia 同級生](https://ja.wikipedia.org/wiki/同級生_(ゲーム)), [Baidu Baike (EN)](https://baike.baidu.com/en/item/D%C5%8Dky%C5%ABsei/1530519), [ja.wikipedia 下級生](https://ja.wikipedia.org/wiki/下級生_(ゲーム)), [en.wikipedia](https://en.wikipedia.org/wiki/D%C5%8Dky%C5%ABsei_(video_game)) |
| **YU-NO** (PC-98, 1996) | Original: you clicked around scenes, and finding the next trigger often meant clicking every hotspot repeatedly (reviewers call this a chore). The Reflector Device on screen **blinks** when a branch point is near. The 2017 remake added icons that appear as the cursor nears a hotspot, and **greys out** icons with nothing new. | Use proximity reveal and a "seen" state, and avoid making visitors hunt for pixels. [en.wikipedia](https://en.wikipedia.org/wiki/YU-NO:_A_Girl_Who_Chants_Love_at_the_Bound_of_this_World), [ja.wikipedia](https://ja.wikipedia.org/wiki/この世の果てで恋を唄う少女YU-NO), [HG101](https://www.hardcoregaming101.net/yu-no/) |
| **EVE burst error** (PC-98, 1995) | Command selection where you brute-force the commands to raise flags. The Saturn port added sound and icon cues telling you when to switch protagonists. | A cue when something new is available beats making players exhaust every option. [ja.wikipedia](https://ja.wikipedia.org/wiki/EVE_burst_error) |
| **Rance** (PC-98, 1989 onwards) | A verb menu ("Examine", "Talk", ...) on every screen. | It's the standard PC-98 command bar. [Wikipedia](https://en.wikipedia.org/wiki/Rance_(series)) |
| **Tokimeki Memorial** (PC Engine, 1994) | Your bedroom is the hub. A **phone** command calls your friend for gossip or calls girls to set up dates. | The phone in your room as the social and contact object has precedent. [StrategyWiki](https://strategywiki.org/wiki/Tokimeki_Memorial:_forever_with_you) |
| **2064: Read Only Memories** (2015, PC-98-styled) | Point-and-click where you pick look, take or talk on objects. It's billed as Snatcher's spiritual successor. | A modern PC-98 pastiche keeps a small verb set. [Automaton](https://automaton-media.com/articles/newsjp/20170119-38556/) |

The classic Japanese ADV response to examining an empty spot is a flat "nothing special here"
(特に変わったところはない, roughly "nothing out of the ordinary"). I couldn't find a citable source for the exact phrase.
It is a well-known convention, so use a funny version of it for clicks on empty space.

### 1c. Modern point-and-click, VN and web practice (discoverable without being ugly)
- **The cursor changes colour or shape over a hotspot.** In *Professor Layton* the magnifier turns orange over
  something interactive, and orange plus sparkles marks a hidden hint coin. [StrategyWiki Curious Village](https://strategywiki.org/wiki/Professor_Layton_and_the_Curious_Village/Gameplay)
- **Checkmarks on examined spots.** In *Ace Attorney* investigation the cursor highlights examinable items, and
  examined ones get a check so you don't repeat them. [StrategyWiki AA](https://strategywiki.org/wiki/Phoenix_Wright:_Ace_Attorney/Gameplay), [StrategyWiki TGAA](https://strategywiki.org/wiki/The_Great_Ace_Attorney:_Adventures/Gameplay)
- **A "reveal all hotspots" button** is the standard fix for pixel-hunting. *Broken Sword 5* has a hotspot
  highlighter, and Thimbleweed Park lets you keep pixel-hunting if you want. [Giant Bomb: Hotspot Highlighting](https://giantbomb.com/wiki/Concepts/Hotspot_Highlighting), [Broken Sword 5 listing](https://lebottinlinux.vps.a-lec.org/Bottin_0-C_files/Broken_Sword_5__The_Serpent_s_Curse-10184.html)
- **Hints that stay in the fiction.** *Return to Monkey Island*'s in-game hint book knows where you are. Items are
  placed openly so players don't "hunt pixels". [GoNintendo](https://www.gonintendo.com/contents/8953-return-to-monkey-island-includes-an-in-game-hint-book-to-guide-players), [Can I Play That](https://caniplaythat.com/2023/05/15/editors-choice-return-to-monkey-island/)
- **The host reacts once per visit.** In *Animal Crossing: New Horizons*, touching an item in a villager's house makes the villager comment, depending on the item and their personality. It happens once per visit, and in New Leaf opening a drawer brings a remark about clutter. [Nookipedia](https://nookipedia.com/wiki/Villager_house)
- **The home-screen character speaks on entry, on tap, and when idle.** Arknights' assistant talks when you arrive,
  when you tap them, and when you go idle. Idle lines are small in-character actions, e.g. Click: "Let me sneak a quick pic." [Arknights wiki](https://arknights.wiki.gg/wiki/Home_Screen)
- **Accessibility guidance.** Make interactive things visibly distinct through consistent style, contrast, a mouseover
  effect, a glow or an icon. [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/give-a-clear-indication-that-interactive-elements-are-interactive/)
- **Image-map guidance (MDN).** The image itself must show where hotspots begin and end. Touch targets should be at
  least 72x72 CSS px with generous gaps, and a text list of the links is preferable. [MDN](https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Add_a_hit_map_on_top_of_an_image)
- **WCAG 1.4.13 (content on hover or focus):** it must be dismissible, hoverable and persistent, i.e. it must not vanish on a timer.
  It applies to hover text in the dialog box, so focus should trigger the same line as hover. [W3C](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus)
- **Colour cycling** is authentic to the era and cheap: animate by rotating palette entries, as in Mark Ferrari's art. A
  canvas engine exists (Canvas Cycle). It's good for twinkling city lights and for a slow pulse on a hotspot. [80.lv](https://80.lv/articles/color-cycling-from-the-90s-returns-with-html5), [Wikipedia](https://wikipedia.com/wiki/Color_cycling)

### 1d. Recommended affordance stack for Panda's Room (most to least important)
1. **Lighting as affordance (art direction).** It's a night room, so make *every hotspot a light source*: CRT glow,
   TV glow, the phone screen on the bed, city lights through the window, a lamp over the bookshelf. Leave everything
   else in dithered shadow. The eye goes to what's lit, and nothing needs an outline at rest.
2. **Greeting teaches the mechanic in Panda's voice** ("Poke at anything you like. I'll narrate."). This is the
   Monkey Island in-fiction-hint idea.
3. **Hover or focus: the object brightens** (swap to a "lit" variant, or a 1px outline in a reserved palette colour such as
   the speaker-name pink #ef0060), **the cursor changes** to a small PC-98 pixel hand or magnifier, as in Doukyuusei's
   icon cursor and Layton's orange magnifier, and **Panda's hover line appears in the dialog box** (no typewriter
   effect, or a very fast one, so it feels instant). Keep the last line up after the pointer leaves (WCAG
   persistence). Don't snap back to the greeting.
4. **Click: dialog plus a choice menu**, as in Policenauts' click-then-action-menu: 1 to 3 short click lines with ▼
   between them, ending in a choice list. Never navigate straight from the first click, because it makes touch and
   hover-less use safe.
5. **Idle glint.** Every ~8–12 s one *unvisited* object gets a 2–3-frame sparkle or palette-cycle shimmer, one object at a time
   (Layton sparkles). Stop it under `prefers-reduced-motion`.
6. **A "見る LOOK" button in the sidebar, the Tab key and an object list.** The button flashes all hotspot outlines for ~1.5 s
   (the hotspot-highlighter pattern) and opens a PC-98 command-style list ("→ PC / → Bookshelf / → Window ..."). That list is
   also the touch, screen-reader and no-JS fallback (MDN's text-list advice).
7. **Seen state.** Visited objects lose their glint and show a tiny dot or tick (Ace Attorney checkmarks, YU-NO remake
   grey icons). Optionally store this in localStorage as a per-viewer convenience.
8. **Empty-space clicks get a deadpan line** (the "nothing special" convention), so clicking around is rewarded rather
   than silent. Repeat clicks on one object can escalate (Snatcher).
9. **Implementation details:** absolutely-positioned `<a>`/`<button>` elements over the art, not `<map>`. Hit areas ≥72px.
   `aria-label` on each ("GitHub (PC)"), `aria-live="polite"` on the dialog text, and focus handled the same as hover.

---------------------------------------------------------------------------------------------------
## 2. VN dialogue conventions and natural voice

### 2a. Box size: measured for this site
- Ace Attorney Investigations (DS) used a **30 characters x 3 lines** box limit, according to localiser Janet Hsu. The
  16:9 remasters allowed more. [Noisy Pixel](https://noisypixel.net/ace-attorney-investigations-collection-localization-director-discusses-how-technological-growth/)
- **vivalapanda.moe:** `#text-box` is 762px wide and `p` uses the `pc-98` font at 30px. In `pc-9800.ttf` every ASCII glyph
  is **15px** wide and full-width glyphs (→ ▼ 「 … ◆) are **30px**. After the margins that leaves **~48 ASCII
  characters per line.** The drafts below are kept to ≤48 so each line fits on one row. The box is about 4–5 lines tall (estimate).
- **Glyph coverage in pc-9800.ttf:** it has ▼ ▲ ▽ → ⇒ ＞ ◆ ◇ ● ○ ★ ☆ 「」『』 … ‥ ♪ ♥ ～ ？ ！. It does **not** have ▶, ▸, ►, ▷, ☞, ♡ or ✓.
  So the "▸ Visit GitHub" in the brief would fall back to another font. Use **→** or **◆**, or (more PC-98) highlight the
  selected choice as an inverted bar. radio.html already has a bouncing `#text-arrow` image, which can serve as the ▼ continue mark.

### 2b. Mechanics
- **Click-to-continue (▼):** shown once the box has fully typed out, to say "click for more". Ren'Py calls it `ctc` and has separate
  markers for mid-line pauses. [Ren'Py docs](https://doc.renpy.cn/zh-TW/screen_special.html), [ja: ▼ convention](https://forest.watch.impress.co.jp/article/2005/08/09/novelviewer.html)
  The convention: the first click finishes the typewriter, the next click advances. On the last box, show the choices instead of ▼.
- **One idea per box.** That means one *idea*, not one sentence. Don't start two consecutive boxes with the same word, and
  read lines aloud. [nomnomnami, "tips for game writers"](https://nomnomnami.com/blog/posts/2023-04-18-tips-for-game-writers.html)
- **Ellipses:** they're everywhere in JRPGs and VNs because they're common in Japanese (one fan counted 6,970 in Xenogears).
  Ration them to one per box at most, used for a real pause. [Kotaku](https://kotaku.com/guy-counts-every-ellipses-you-have-to-see-to-finish-xen-1830910221)
- **Beat splits:** put the setup in one box and the punchline after ▼. Panda's own Pandopolis lines already do this:
  "I uhh, promise this place is definitely legal..." ▼ "probably." (js/explore-locations.js)
- **Speaker names:** the nameplate goes above the text (pink "Ｐａｎｄａ" already). Japanese VNs wrap spoken lines in 「」; the
  current site doesn't, so stay unbracketed for consistency. If wanted, （…） can mark a muttered aside.
- **Choices:** short imperative verb phrases, 2–3 options, and the cancel option always last. PC-98 menus used bare verbs
  (見る/調べる/話す/移動 = look/examine/talk/move), and "never mind" corresponds to やめる (quit/stop). Snatcher's "LOOK > POSTER" is the two-level form.

### 2c. Host and examine voice: real examples (short quotes or paraphrases)
- **Policenauts**, Jonathan's apartment: examining his things gives terse backstory. His ex-wife's photo gets a quick self-correction
  ("My wife. No, that was a long time ago."). A wrong-number message gets "Thank you for wasting my time." [LP Archive](https://lparchive.org/Policenauts/Update%2001)
  *Pattern: an object becomes one dry line about the owner.*
- **Undertale**, Toriel's home: deadpan with one twist. Her chair: "Its name is Chairiel." Her cactus: "the most tsundere of plants."
  [Undertale wiki](https://undertale.wiki/w/Toriel's_Home). *Pattern: a plain statement, then one unexpected word.*
- **Undertale**, Papyrus greeting you: "YOU'RE IN MY HOUSE. GOOD CHOICE!" [Undertale wiki](https://undertale.wiki/w/Papyrus_and_Sans's_House)
  *Pattern: an enthusiastic host who treats your visit as a compliment.*
- **Snatcher:** Metal Gear needles Gillian as the straight man, and examining things twice gets a second, sillier line. [classic-games.net](https://www.classic-games.net/genesis/snatcher), [ja.wikipedia](https://ja.wikipedia.org/wiki/SNATCHER)
  *Pattern: the host can be her own straight man ("...Okay, some.").*
- **Animal Crossing:** the host comments on whatever you touched, and New Leaf's remarks are often about clutter in their drawers. [Nookipedia](https://nookipedia.com/wiki/Villager_house)
  *Pattern: self-deprecation about one's own stuff reads as warm.*
- **Arknights idle lines:** small present-tense actions. Click: "Let me sneak a quick pic. Yeah, just one shot." [Arknights wiki](https://arknights.wiki.gg/wiki/Click/Dialogue)
  *Pattern: idle lines describe what the host is doing and don't nag the visitor.*
- **Panda's existing voice** (this site): "frens", "anon", the occasional ^_^, "*something*", and the beat-split "probably."

### 2d. Style rules derived for Panda
1. Keep each box to ≤48 characters per line and one idea. Hover lines are a single line.
2. Each object line says something about *Panda*, not about the service ("my code is never done", not "GitHub hosts code").
3. Use dry statements with one twist, and keep jokes to one per box.
4. Self-deprecating, never self-loathing: aim for "medium expectations", not "I'm terrible".
5. Urbanist flavour comes through nouns (zoning, density, last train, lit windows, walking to school), not lectures.
6. Use at most one ellipsis per box, and use it as a real pause or for a split beat.
7. Name the service only on the click line or in the choice, so the hover line stays in the fiction.
8. Idle lines are small actions or gentle remarks. No "Hello?? Are you there??", no guilt, and at most three per visit.
9. Choices are verb plus service, and "Look at something else" or "Never mind" always comes last.
10. Avoid uwu, stacked emoticons, and explaining the joke.

---------------------------------------------------------------------------------------------------
## 3. Draft dialogue (2 alternates each; every line ≤48 chars and fits one row)

Format: **hover** = one line on hover or focus. **click** = boxes separated by ▼, then the choice menu.

### Entering the room (greeting)
- A: Oh, you made it! Come in, mind the cables. ▼ Poke at anything you like. I'll narrate.
- B: Welcome to my room! It's small, but it's dense. ▼ Look around. Everything here goes somewhere.

### PC → GitHub (VivaLaPanda)
- hover A: My PC! Code goes here when it's done. So, never.
- hover B: The battlestation. Forty tabs, two of them code.
- click A: Radio servers, PC-98 filters, this very site... ▼ Most of it works! Some of it on purpose.
- click B: Want to see my GitHub? Lower your expectations. ▼ ...Actually, medium expectations. It's fine.
- choices: → Visit GitHub / → Look at something else
- repeat click: Same PC. Still not done. Never will be.

### Bookshelf → reading list
- hover A: Bookshelf. Seeing Like a State is load-bearing.
- hover B: Half urbanism, half web novels. No regrets.
- click A: These are the books I'd actually hand you. ▼ Starting with Seeing Like a State, obviously.
- click B: Cities, economics, Discworld... ▼ ...and one 1,600-chapter cultivation novel.
- choices: → Browse the reading list / → Look at something else
- repeat click: Yes, I've read them all. Mostly. Okay, some.

### Window and city lights → Bluesky (plus Twitter/X)
- hover A: The city at night. Someone's always awake.
- hover B: Look at all those lights. Nobody's asleep.
- click A: I talk cities out there. Mostly on Bluesky. ▼ And trains. And then cities again.
- click B: Every lit window is somebody's whole world. ▼ I yell about zoning at a few of them on Bluesky.
  (This quietly echoes the Substack tagline about carrying a new world.)
- choices: → Bluesky / → Twitter / → Never mind
- optional pigeon on the sill = Twitter, **only if Twitter is the quieter account**: A pigeon. That's my Twitter. It naps a lot.

### Phone on the bed → Discord and Signal
- hover A: My phone. It's buzzing. It's always buzzing.
- hover B: Phone's face-down on the bed. That's self-care.
- click A: Want to talk? I'm vivalapanda on Discord. ▼ Honestly, I mostly live there.
- click B: Message me! I'll answer. Eventually. ▼ Discord's quickest. Signal if it's secret-ish.
- choices: → Copy my Discord handle / → Message on Signal / → Never mind
  (Discord is a handle, not a profile link, so copy it and confirm with a small "Copied!" line.)

### TV → (decide: Steam, watch/anime list, or Letterboxd if one exists)
- Steam version (TV plus console):
  - hover: The TV, the console, and the backlog.
  - click: My Steam library. Games I'll play someday. ▼ Someday is doing a lot of work there.
  - choices: → Steam profile / → Look at something else
- Watch-list version (Letterboxd or anime list):
  - hover: TV's on standby. So is my watchlist.
  - click: My anime list! Last updated... a while ago. ▼ In my defence, I was outside.
  - choices: → See what I've watched / → Look at something else

### Extra: newspaper on the desk → Substack ("Panda's Portentous Portal")
- hover A: Today's paper. I wrote it, so it's biased.
- hover B: My newsletter. Cities, kids, and Dubai, mostly.
- click A: The Portentous Portal! Long posts about cities. ▼ Grab some tea first. They run long.
- click B: I write about making cities feel like home. ▼ And about letting kids walk to school alone.
- choices: → Read the Portal / → Look at something else

### Extra: stereo → /radio.html
- hover A: The stereo. My friends pick the songs. Brace.
- hover B: Stereo's on. It's always on.
- click: My little radio station. I wrote the server! ▼ My friends queue the songs. No promises.
- choices: → Tune in / → Look at something else

### Optional: envelope → email
- hover: A letter? Email works too, if you're fancy.
- click: me@panda.moe. I read everything. ▼ Replying is a separate skill. I'm working on it.

### Idle lines (first after ~30 s of no input, then every ~45 s, three at most per visit)
1. A: No rush. The city's not going anywhere. / B: Still there? No pressure. I like the company.
2. A: Want some tea? I'll put the kettle on. / B: *yawn* Sorry. Nights are when I get stuff done.
3. A: Hear that? Last train heading home. / B: Sorry about the mess. It's curated mess.

### Clicking empty space (rotate through these)
- That's a wall. A very good wall, though.
- Nothing there. Just vibes.
- That's the floor. Mind the cables. (calls back to greeting A)
- That one's just a plant. It's doing its best. (if a non-link plant is drawn)

### After every object has been seen (optional)
- Okay, you've found everything. I'm impressed.

---------------------------------------------------------------------------------------------------
## 4. Brief art notes (only where they bear on affordance)
- Use the existing pipeline (github.com/VivaLaPanda/pc98-assets and its PC98_STYLE_GUIDE): a 16-colour palette, dithering, 640x400 feel.
- Draw the base room plus a separate "lit" layer for each hotspot object, so hover can swap or brighten one object.
  (Real PC-98 games had no sprites; this is a modern cheat that keeps the look.)
- Reserve 2–3 palette slots: city-light twinkle (colour cycling), hotspot highlight, and phone/CRT glow. Cycling those
  slots animates lights cheaply and in period style.
- Composition: give each hotspot a strong silhouette with clear space between them, so hit areas don't overlap (MDN 72px).
  The window should be big, since the city is a theme. Keep the bed and phone near the bottom edge, where thumbs reach on mobile.
- Leave non-interactive clutter (plant, posters, fox plushie) in shadow. It's flavour for the empty-space lines.

---------------------------------------------------------------------------------------------------
## Caveats
- I couldn't fetch a primary script for Snatcher's examine lines (the LPs are screenshots), so the Snatcher patterns rest on
  reviews and ja.wikipedia. The "Konami logo" repeat-examine joke surfaced only in a search summary and is unverified, so it's left out above.
- Doukyuusei's exact cursor shapes (eye, mouth, hand?) aren't confirmed. Sources only say the icons change shape by situation and purpose.
- Letterboxd 404 is for the username "vivalapanda" only.
- Box height in lines is estimated. Width per line is measured from the font metrics.

## Sources (main)
- HG101 Snatcher: https://www.hardcoregaming101.net/snatcher/
- ja.wikipedia SNATCHER: https://ja.wikipedia.org/wiki/SNATCHER
- classic-games.net Snatcher: https://www.classic-games.net/genesis/snatcher
- Racketboy Snatcher meta-review: https://racketboy.com/retro/meta-review-snatcher-sega-cd
- LP Archive Policenauts 01: https://lparchive.org/Policenauts/Update%2001
- Sega-16 Policenauts: https://www.sega-16.com/?p=30395
- ja.wikipedia 同級生: https://ja.wikipedia.org/wiki/同級生_(ゲーム) ; 下級生: https://ja.wikipedia.org/wiki/下級生_(ゲーム)
- Baidu Baike Dōkyūsei: https://baike.baidu.com/en/item/D%C5%8Dky%C5%ABsei/1530519
- en/ja.wikipedia YU-NO: https://en.wikipedia.org/wiki/YU-NO:_A_Girl_Who_Chants_Love_at_the_Bound_of_this_World
- ja.wikipedia EVE burst error: https://ja.wikipedia.org/wiki/EVE_burst_error
- Rance series: https://en.wikipedia.org/wiki/Rance_(series)
- Portopia LP interlude: https://lparchive.org/The-Portopia-Serial-Murder-Case/Update%2004/
- Tokimeki Memorial: https://strategywiki.org/wiki/Tokimeki_Memorial:_forever_with_you
- Read Only Memories (Automaton): https://automaton-media.com/articles/newsjp/20170119-38556/
- Layton: https://strategywiki.org/wiki/Professor_Layton_and_the_Curious_Village/Gameplay
- Ace Attorney: https://strategywiki.org/wiki/Phoenix_Wright:_Ace_Attorney/Gameplay
- Hotspot highlighting: https://giantbomb.com/wiki/Concepts/Hotspot_Highlighting
- Return to Monkey Island: https://www.gonintendo.com/contents/8953-return-to-monkey-island-includes-an-in-game-hint-book-to-guide-players ; https://caniplaythat.com/2023/05/15/editors-choice-return-to-monkey-island/
- Nookipedia villager house: https://nookipedia.com/wiki/Villager_house
- Arknights home screen / Click dialogue: https://arknights.wiki.gg/wiki/Home_Screen ; https://arknights.wiki.gg/wiki/Click/Dialogue
- Game Accessibility Guidelines: https://gameaccessibilityguidelines.com/give-a-clear-indication-that-interactive-elements-are-interactive/
- MDN hit map: https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Add_a_hit_map_on_top_of_an_image
- WCAG 1.4.13: https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus
- Colour cycling: https://80.lv/articles/color-cycling-from-the-90s-returns-with-html5
- Ren'Py ctc: https://doc.renpy.cn/zh-TW/screen_special.html
- Janet Hsu 30x3: https://noisypixel.net/ace-attorney-investigations-collection-localization-director-discusses-how-technological-growth/
- nomnomnami writing tips: https://nomnomnami.com/blog/posts/2023-04-18-tips-for-game-writers.html
- Kotaku Xenogears ellipses: https://kotaku.com/guy-counts-every-ellipses-you-have-to-see-to-finish-xen-1830910221
- Undertale wiki: https://undertale.wiki/w/Toriel's_Home ; https://undertale.wiki/w/Papyrus_and_Sans's_House
- BookWyrm: https://github.com/joachimesque/bookwyrm ; Open Library reading log: https://blog.openlibrary.org/2020/05/26/reading-logs-going-public-helping-book-lovers-share/
- smithdev.io archive: http://web.archive.org/web/20200304135202id_/https://smithdev.io/main.e914494afd9817b87a5d.bundle.js
