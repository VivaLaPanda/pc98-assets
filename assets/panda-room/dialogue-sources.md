# Panda's Room dialogue sources

Every line in `vivalapanda.moe/js/room-data.js`, where it came from. The user asked for real VN lines instead of
Claude-written ones (2026-10-04), so lines are borrowed verbatim where possible, with the smallest change otherwise
(a noun swapped so it refers to the right thing). Lines with no source are short functional lines in the same plain style.

Pool: VNDB's quote database (all 9,695 quotes via the kana API), the Katawa Shoujo script (CC BY-NC-ND, English .rpy
files), the Doki Doki Literature Club! story scripts, and the Ace Attorney wiki transcripts. One short line per
borrowing, spread across many works. Lines were checked against the layout-B art: each one refers only to
things drawn in the scene (no clouds in the night sky, empty-space lines don't name a surface). Choice labels ("→ Visit Twitter", "→ Look at something else"...) are UI and unchanged.

**PC-98-era lines (2026-10-04, round 2).** The user asked for more lines from PC-98-era games and pointed out they could
be translated from the Japanese. Eight lines (marked "translated") come from Japanese originals, translated for this
page: six from Tokimeki Memorial (released on PC Engine in 1994; PC-98-era rather than a PC-98 game) and two from EVE
burst error (PC-98, 1995). Candidates that turned out to be fan-art captions, a 1997 spin-off minigame, or an OVA
(not the game) were dropped. Doukyuusei, YU-NO and Policenauts lines couldn't be sourced in Japanese, so none are used.
The bookshelf hover is now from the owner's side (Panda offering her shelf), not a visitor finding books.

**Round 3 (2026-10-04): interpolation.** The user: "dialogue should interpolate VN dialogue and stuff that actually
makes sense here", and disliked the memes line. So lines are no longer verbatim-only: a real line is kept where it fits
this room and this object as-is, adapted or **interpolated** (a real line reshaped to say something true about the
object, its source kept) where it nearly fits, and replaced with an **original** line in the same plain, reactive
register where no real line made sense. Every line was re-read for who is speaking (Panda, the owner, to a guest), about
what, in this night room.

| slot | final line | kind | original (if changed) | work / character | source |
|---|---|---|---|---|---|
| greeting 1 | Welcome, traveler, to my room of mysteries. | verbatim |  | Rewrite / Senri Akane | https://vndb.org/v751 (VNDB quote q2761) |
| greeting 2 | Don't be shy now, come on in. | verbatim |  | Katawa Shoujo / Sae | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a3-rin.rpy#L3906 |
| greeting 3 | Poke around all you like! Lost? Press LOOK. | original (plain; teaches hover/click and LOOK) |  | - | - |
| window hover | E-everything looks so p-pretty at night... | verbatim | E-everything looks so p-pretty at night… (ellipsis as three dots) | Katawa Shoujo / Hanako Ikezawa | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a3-hanako.rpy#L5341 |
| window click 1 | The town, the people... we're all family. | adapted (dropped leading "Yes.") | Yes. The town, the people... we're all family. | CLANNAD / Furukawa Nagisa | https://vndb.org/v4 (VNDB quote q1990) |
| window click 2 | I tweet about it way too much. Mostly zoning. | original (plain) |  | - | - |
| window repeat | Pleeease... take me somewhere~ | translated (from Japanese) | 夕子「お願～い。どっか連れてって～」 | Tokimeki Memorial (1994) / Asahina Yuko | https://dic.pixiv.net/a/%E6%9C%9D%E6%97%A5%E5%A5%88%E5%A4%95%E5%AD%90 |
| phone hover | Eh? My phone's buzzing... is that you? | original (VN register; replaces the memes line the user disliked) |  | - | - |
| phone click 1 | On Discord, you can call me vivalapanda. | interpolated (Discord added so the line says where) | You can call me Rin. | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-wednesday.rpy#L2836 |
| phone click 2 | Secrets go on Signal. They're safe with me. | interpolated (made to say what Signal is for) | Don't worry, your secret's safe with me. | Katawa Shoujo / Misha | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-emi.rpy#L1080 |
| phone repeat | If friends gossip about us... how embarrassing. | translated + adapted (dropped "if we walk home together" to fit the box) | 藤崎詩織「一緒に帰って、友達に噂とかされると、恥ずかしいし…。」 | Tokimeki Memorial (1994) / Fujisaki Shiori | https://futaman.futabanet.jp/articles/-/126479 ; https://dic.pixiv.net/a/%E8%97%A4%E5%B4%8E%E8%A9%A9%E7%B9%94 |
| pc hover | I keep falling asleep at that computer... | interpolated (owner talking about her own PC, not waking at it) | Oh crap... fell asleep at the computer again. | Fission Frontier / Rashomon Nao | https://vndb.org/v55716 (VNDB quote q4788) |
| pc click 1 | My true love has always been my computer. | adapted (dropped the dangling "But") | But my lover has always been my computer. | SWAN SONG / Kuwagata Takuma | https://vndb.org/v914 (VNDB quote q5626) |
| pc click 2 | Everything I make ends up on GitHub. | original (plain) |  | - | - |
| pc repeat | Back again? It's an infinitely repeating game. | interpolated (now about you coming back) | This is... An Infinitely Repeating Game. | Subarashiki Hibi ~Furenzoku Sonzai~ | https://vndb.org/v3144 (VNDB quote q3379) |
| newspaper hover | Heh. Who knew my essays could be interesting? | adapted (paper bags → my essays: the paper is her own Substack) | Heh. Who knew paper bags could be interesting? | Famicom Tantei Club: Emio / Protagonist | https://vndb.org/v51838 (VNDB quote q3429) |
| newspaper click 1 | I write about cities on my Substack. | original (plain) |  | - | - |
| newspaper click 2 | Well, you can read it at your own pace. | verbatim |  | Doki Doki Literature Club! / Yuri | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch1.rpy#L118 |
| newspaper repeat | Are you ready to continue reading? | verbatim |  | Doki Doki Literature Club! / Yuri | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch23.rpy#L46 |
| bookshelf hover | If it's books you want, leave it to me. | translated + adapted (女の子の情報 "info on girls" → books; dropped the opening "Nah, don't mention it!") | 早乙女好雄「なーにいいってことよ！女の子の情報なら、俺に任せてくれよ。」 | Tokimeki Memorial (1994) / Saotome Yoshio (the game's opening exchange) | https://dic.pixiv.net/a/%E8%97%A4%E5%B4%8E%E8%A9%A9%E7%B9%94 |
| bookshelf click 1 | My reading list isn't ready yet. Soon! | original (plain) |  | - | - |
| bookshelf click 2 | I barely got to do any reading today, so... | verbatim |  | Doki Doki Literature Club! / Natsuki | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch3.rpy#L916 |
| bookshelf repeat | Still not ready! Reading takes time, okay? | original (replaces a top-shelf line that didn't fit) |  | - | - |
| butterfly hover | I love butterflies. They are the best animal. | verbatim |  | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-rin.rpy#L7126 |
| butterfly click 1 | That one's my Bluesky. I'm there sometimes. | original (plain) |  | - | - |
| butterfly click 2 | It wouldn't be so bad to be the sky. | verbatim |  | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-rin.rpy#L6436 |
| butterfly repeat | Why would it be a bird? It's a butterfly! | interpolated (a nod to the bird in the window: Twitter vs Bluesky) | Chicken? Why would I be a bird? | Tsukihime -A piece of blue glass moon- | https://vndb.org/v17909 (VNDB quote q578) |
| tv hover | You've found the television, then. | verbatim |  | Katawa Shoujo / Lilly Satou | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a3-lilly.rpy#L2234 |
| tv click 1 | Every movie I watch goes on my Letterboxd. | original (plain; the TV isn't where she logs) |  | - | - |
| tv click 2 | Let's go watch! | verbatim |  | Katawa Shoujo / Yuuko Shirakawa | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-hanako.rpy#L635 |
| tv repeat | It's pro wrestling! Woo! Woo! | translated (from Japanese) | 早乙女優美「プロレスだー。ウォーウォー。」 | Tokimeki Memorial (1994) / Saotome Yumi | https://dic.pixiv.net/a/%E6%97%A9%E4%B9%99%E5%A5%B3%E5%84%AA%E7%BE%8E |
| plush hover | The panda says, 'Gao, gao!' | adapted (stegosaurus → panda) | The stegosaurus says, 'Gao, gao!' | AIR / Kamio Misuzu | https://vndb.org/v36 (VNDB quote q5552) |
| plush line 1 | He's the original Panda. I'm the sequel. | original (replaces a line that made no sense here) |  | - | - |
| plush line 2 | Sorry, I was born cute. | verbatim |  | G-senjou no Maou | https://vndb.org/v211 (VNDB quote q446) |
| idle 1 | It's nice and quiet in here, isn't it? | verbatim |  | Katawa Shoujo / Lilly Satou | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-sunday.rpy#L3709 |
| idle 2 | Do... would you like some tea? | verbatim | Do… would you like some tea? (ellipsis as three dots) | Katawa Shoujo / Hanako Ikezawa | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-sunday.rpy#L4271 |
| idle 3 | Luck comes to those who smile. So, smile! | translated (from Japanese; the end of a longer line) | 法条まりな「…笑う門には福来る、よ。さっ、笑って。」 | EVE burst error (1995, PC-98) / Houjou Marina | https://pro-botti.com/marina-famous_lines/ |
| idle 4 | Hear that? The last train's heading home. | original (night, urbanist) |  | - | - |
| empty 1 | Hm? Are you talking to moi? | verbatim |  | AI: The Somnium Files | https://vndb.org/v26532 (VNDB quote q9402) |
| empty 2 | If you need something, just say it! | translated (from Japanese) | 清川望「用があるならはっきり言えよ」 | Tokimeki Memorial (Sega Saturn version, 1996) / Kiyokawa Nozomi | https://futaman.futabanet.jp/articles/-/126479?page=2 |
| empty 3 | Hey, don't make that face. | translated (from Japanese; a clause from a longer line) | 法条まりな「…そんな顔しないの。…」 | EVE burst error (1995, PC-98) / Houjou Marina | https://pro-botti.com/marina-famous_lines/ |
| empty 4 | Uguu... | adapted (first word only) | Uguu... Ayu Ayu's not my name... | Kanon / Tsukimiya Ayu | https://vndb.org/v33 (VNDB quote q7722) |
| LOOK prompt | What do you want to look at? | original (plain) |  | - | - |
| leaving | It's not good bye, it's see you again. | verbatim |  | Muv-Luv / Shirogane Takeru | https://vndb.org/v93 (VNDB quote q1863) |
| copied | Copied! It's vivalapanda. | original (plain, functional) |  | - | - |
| copy failed | Huh? It didn't copy... it's vivalapanda! | original (plain, functional) |  | - | - |
| back to room | Okkei! | verbatim |  | CHAOS;CHILD / Onoe Serika | https://vndb.org/v14018 (VNDB quote q4339) |
| all seen | Congratulations! You found everything~! | adapted ("Congratulations!" + plain) | Congratulations! | Katawa Shoujo / Misha | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-thursday.rpy#L2656 |

**New objects (2026-10-04, round 3; in the room with art v2).** All original lines in the same register, except where
noted. The room is only for places elsewhere on the web, so the stereo (/radio.html) and recipe binder (/recipes.html)
were dropped before they reached the page (the sidenav has the site's own pages); their lines are kept below, struck
through, in case they're wanted elsewhere. The console's id in room-data.js is `controller` (the art's hotspot name).
LessWrong (the navy-and-gold tome on the bed) and LinkedIn (the blazer and red tie on the chair back) came with art v2.

| slot | final line | kind | original (if changed) | work / character | source |
|---|---|---|---|---|---|
| letter hover | I wrote to my parents last week. | verbatim (the letter on her desk is one she wrote) |  | Katawa Shoujo / Hisao Nakai | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a4-shizune.rpy#L2281 |
| letter click 1 | You can write to me too! I'm at me@panda.moe. | original (plain, functional) |  | - | - |
| letter click 2 | Everything that you write is a treasure to me. | verbatim |  | Doki Doki Literature Club! / Yuri | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-poemresponses2.rpy#L500 |
| letter repeat | Write to me, okay? I'll write back. | original |  | - | - |
| ~~stereo hover~~ | My stereo! It's always playing something. | dropped (site page, not external) |  | - | - |
| ~~stereo click 1~~ | That's my radio station. It runs all night. | dropped (site page, not external) |  | - | - |
| ~~stereo click 2~~ | Wanna listen together? | dropped (site page, not external) |  | - | - |
| ~~stereo repeat~~ | Turn it up! ...Not too loud. The neighbors. | dropped (site page, not external) |  | - | - |
| ~~recipes hover~~ | My recipe binder. It's... a little stained. | dropped (site page, not external) |  | - | - |
| ~~recipes click 1~~ | I'm not a great cook. But these all work! | dropped (site page, not external) |  | - | - |
| ~~recipes click 2~~ | Want to try one? The pancakes are easy. | dropped (site page, not external) |  | - | - |
| ~~recipes repeat~~ | Hungry? Me too. Let's cook something. | dropped (site page, not external) |  | - | - |
| console hover | Eh? Just playing some Cities: Skylines. | adapted (the game swapped for a city builder) | Eh? Just playing some Civilization Universalis IV. | Tokyo Babel / Raziel | https://vndb.org/v13664 (VNDB quote q4302) |
| console click 1 | I play games rarely. ...Very rarely. | interpolated (Panda's own Steam bio) | I play games rarely. | Panda's Steam profile summary | https://steamcommunity.com/id/vivalapanda |
| console click 2 | Hey, what's your favorite game? | verbatim |  | Doki Doki Literature Club! / Monika | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch30.rpy#L1300 |
| console repeat | Fancy another game? | verbatim |  | Katawa Shoujo / Hisao Nakai | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a3-hanako.rpy#L42 |
| poster hover | Cuteness wins in the end. Cuteness is justice! | verbatim |  | Kin'iro Loveriche -Golden Time- / Kisaki Reina | https://vndb.org/v19073 (VNDB quote q8856) |
| poster line 1 | That's my favorite magical girl! | original |  | - | - |
| poster line 2 | Abracadabra! Welcome to life as a magical girl! | adapted (dropped "baby") | Abracadabra, baby! Welcome to life as a magical girl! | BLAZBLUE CONTINUUM SHIFT | https://vndb.org/v4569 (VNDB quote q1038) |
| lesswrong hover | Ah, now I started thinking again. This is bad. | verbatim |  | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-saturday.rpy#L1263 |
| lesswrong click 1 | My nerdier essays go up on LessWrong. | original (plain, functional) |  | - | - |
| lesswrong click 2 | I could go on, but I think you get the point... | verbatim (a joke on long posts) |  | Doki Doki Literature Club! / Monika | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch30.rpy#L1263 |
| lesswrong repeat | As rational as ever, I see. | verbatim (said to you, back at the tome) |  | Katawa Shoujo / Hisao Nakai | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-hanako.rpy#L3902 |
| linkedin hover | Is it hard, being an adult? | verbatim |  | Katawa Shoujo / Hisao Nakai | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a4-shizune.rpy#L111 |
| linkedin click 1 | I wear it to interviews. And on LinkedIn. | original (plain) |  | - | - |
| linkedin click 2 | Need me for work stuff? LinkedIn's the place. | original (plain, functional) |  | - | - |
| linkedin repeat | Thank you for your hard work today. | verbatim (an otsukaresama, the office sign-off) |  | Automatic Medicine Injector | https://vndb.org (VNDB quote q9487) |

Totals after round 4 (79 lines, art v3): see the end of the round-4 note.

**Art v2 audit (2026-10-04).** Every line re-read against the v2 art (moonlit night, butterfly on the left curtain, TV
and console on the floor, phone and tome on the bed, blazer on the chair). None contradicts it; one draft LessWrong
line about a broken spine was replaced, since the tome is drawn intact.

**Round 4 (2026-10-06): the LessWrong lines, an audit, three new objects.** The user: "The lesswrong voice lines are
bad". All four were Claude-written ("It changed how I think. Really.", "Change my mind! Really. Bring evidence.") and
are replaced, rows above. The same batch (letter, console, poster, LinkedIn) had the same problem: mostly original
quips, aphorisms ("Letters are a lost art"), stock jokes ("Business casual is a lie"). Those were rewritten too,
keeping Panda's Steam bio line and the plain functional lines that say where each link goes. Pool this round: VNDB's
quote database (9,720 quotes), the English Katawa Shoujo scripts, the DDLC story scripts. Plush, poster line 1 and the
round-3 objects (window, phone, PC, newspaper, bookshelf, butterfly, TV, letter repeat) were re-read and kept.

New objects with art v3 (Kitsu: anime tapes by the TV; Stack Overflow: a rubber duck by the keyboard; Bump: a city map
pinned to the wall). The Kitsu numbers are from the API (newest list entry 2022-07-10, 544 entries; 134,017 minutes, ~93 days). Kitsu is
more current than the user's MyAnimeList (newest list update 2018-05-17, 466 entries), so the tapes link to Kitsu.

| slot | final line | kind | original (if changed) | work / character | source |
|---|---|---|---|---|---|
| kitsu hover | Gaze upon my anime tapes and despair! | adapted (figures → tapes) | Gaze upon my anime figures and despair! | Scarlet Hollow / Kaneeka Forsyth | https://vndb.org (VNDB quote q8144) |
| kitsu click 1 | Kitsu says I've watched 93 days of anime. | original (plain; the profile's own number) |  | - | https://kitsu.io/users/VivaLaPanda |
| kitsu click 2 | ...And I stopped logging in 2022. Oops. | original (plain; last list entry 2022-07-10) |  | - | https://kitsu.io/users/VivaLaPanda |
| kitsu repeat | Holy moly! Anime is so extreme these days | verbatim |  | Hitotsu Yane no, Tsubasa no Shita de / Hirosawa Hikari | https://vndb.org (VNDB quote q7579) |
| stackoverflow hover | You think rubber ducks are creepy? | verbatim |  | Katawa Shoujo / Hisao Nakai | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-rin.rpy#L3846 |
| stackoverflow click 1 | I asked the duck for an answer. It was no use. | interpolated (God → the duck: rubber-duck debugging) | I've asked God for an answer. It was no use. | Eiyuu * Senki | https://vndb.org (VNDB quote q1011) |
| stackoverflow click 2 | So I took my question to Stack Overflow. | original (plain, functional) |  | - | - |
| stackoverflow repeat | That's a good question. ...Closed as duplicate. | interpolated (the punishment → Stack Overflow's) | That's a good question. Now go stand in the corridor. | Daitoshokan no Hitsujikai | https://vndb.org (VNDB quote q298) |
| bump hover | I'm not lost. I just don't know where I am. | verbatim |  | Hatsuru Koto Naki Mirai Yori / Mimori Ichirou | https://vndb.org (VNDB quote q6469) |
| bump click 1 | On Bump, my friends are pins on a map. | original (plain; says what Bump is) |  | - | - |
| bump click 2 | I can tell where you went without a GPS. | verbatim |  | Nameless / Tei | https://vndb.org (VNDB quote q9945) |
| bump repeat | I've got to go meet up with a friend of mine. | verbatim |  | Katawa Shoujo / Meiko Ibarazaki (Emi's mother) | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-emi.rpy#L3360 |

Totals (79 lines on the page): 24 original, 31 verbatim, 7 translated, 9 adapted, 8 interpolated.

**The contact page (2026-10-07).** /contact.html became a VN choice menu ("How do you want to reach me?") with the same
rules; its lines live in vivalapanda.moe/js/contact.js.

| slot | final line | kind | original (if changed) | work / character | source |
|---|---|---|---|---|---|
| contact prompt | How do you want to reach me? | original (plain; the approved menu question) |  | - | - |
| contact twitter | Don't be shy, I'd love to hear from you. | interpolated (what you wrote → hearing from you) | Don't be shy, I'd love to see what you wrote. | Doki Doki Literature Club! / Monika | https://github.com/Monika-After-Story/DDLCModTemplate/tree/master/original_story_scripts |
| contact signal | Don't worry, your secret's safe with me. | verbatim |  | Katawa Shoujo / Misha | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-emi.rpy#L1080 |
| contact discord | Copied! You can call me vivalapanda. | interpolated (as the room's phone line) | You can call me Rin. | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-wednesday.rpy#L2836 |
| contact discord (copy failed) | Huh? It didn't copy... it's vivalapanda! | original (plain, functional; same as the room) |  | - | - |
| contact letter | Write to me@panda.moe, okay? I'll write back. | original (the room's letter repeat line, with the address) |  | - | - |
