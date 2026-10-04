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

| slot | final line | kind | original (if changed) | work / character | source |
|---|---|---|---|---|---|
| greeting 1 | Welcome, traveler, to my room of mysteries. | verbatim |  | Rewrite / Senri Akane | https://vndb.org/v751 (VNDB quote q2761) |
| greeting 2 | Sorryyy! The train was totally packed... | translated (from Japanese) | 朝日奈夕子「ごっめ～ん！電車がモロ混みで……」 | Tokimeki Memorial (1994) / Asahina Yuko | https://dic.pixiv.net/a/%E6%9C%9D%E6%97%A5%E5%A5%88%E5%A4%95%E5%AD%90 ; her famous lateness line 「電車がモロ混みで遅刻しちゃった」, discussed by her voice actress: https://futaman.futabanet.jp/articles/-/67820 |
| greeting 3 | If you get lost, press LOOK, okay? | original (plain) |  | - | - |
| window hover | E-everything looks so p-pretty at night... | verbatim | E-everything looks so p-pretty at night… (ellipsis as three dots) | Katawa Shoujo / Hanako Ikezawa | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a3-hanako.rpy#L5341 |
| window click 1 | The town, the people... we're all family. | adapted (dropped leading "Yes.") | Yes. The town, the people... we're all family. | CLANNAD / Furukawa Nagisa | https://vndb.org/v4 (VNDB quote q1990) |
| window click 2 | I talk about it on Twitter. A lot. | original (plain) |  | - | - |
| window repeat | Pleeease... take me somewhere~ | translated (from Japanese) | 夕子「お願～い。どっか連れてって～」 | Tokimeki Memorial (1994) / Asahina Yuko | https://dic.pixiv.net/a/%E6%9C%9D%E6%97%A5%E5%A5%88%E5%A4%95%E5%AD%90 |
| phone hover | I'm so gonna text you weird memes. | adapted (him → you) | "I'm so gonna text him weird memes." | Doki Doki Switcheroo! | https://vndb.org/v24173 (VNDB quote q7506) |
| phone click 1 | You can call me vivalapanda. | adapted (Rin → vivalapanda) | You can call me Rin. | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-wednesday.rpy#L2836 |
| phone click 2 | Don't worry, your secret's safe with me. | verbatim |  | Katawa Shoujo / Misha | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-emi.rpy#L1080 |
| phone repeat | If friends gossip about us... how embarrassing. | translated + adapted (dropped "if we walk home together" to fit the box) | 藤崎詩織「一緒に帰って、友達に噂とかされると、恥ずかしいし…。」 | Tokimeki Memorial (1994) / Fujisaki Shiori | https://futaman.futabanet.jp/articles/-/126479 ; https://dic.pixiv.net/a/%E8%97%A4%E5%B4%8E%E8%A9%A9%E7%B9%94 |
| pc hover | Oh crap... fell asleep at the computer again. | verbatim |  | Fission Frontier / Rashomon Nao | https://vndb.org/v55716 (VNDB quote q4788) |
| pc click 1 | But my lover has always been my computer. | verbatim |  | SWAN SONG / Kuwagata Takuma | https://vndb.org/v914 (VNDB quote q5626) |
| pc click 2 | Everything I make ends up on GitHub. | original (plain) |  | - | - |
| pc repeat | This is... An Infinitely Repeating Game. | verbatim |  | Subarashiki Hibi ~Furenzoku Sonzai~ | https://vndb.org/v3144 (VNDB quote q3379) |
| newspaper hover | Heh. Who knew newspapers could be interesting? | adapted (paper bags → newspapers) | Heh. Who knew paper bags could be interesting? | Famicom Tantei Club: Emio / Protagonist | https://vndb.org/v51838 (VNDB quote q3429) |
| newspaper click 1 | I write about cities on my Substack. | original (plain) |  | - | - |
| newspaper click 2 | Well, you can read it at your own pace. | verbatim |  | Doki Doki Literature Club! / Yuri | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch1.rpy#L118 |
| newspaper repeat | Are you ready to continue reading? | verbatim |  | Doki Doki Literature Club! / Yuri | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch23.rpy#L46 |
| bookshelf hover | If it's books you want, leave it to me. | translated + adapted (女の子の情報 "info on girls" → books; dropped the opening "Nah, don't mention it!") | 早乙女好雄「なーにいいってことよ！女の子の情報なら、俺に任せてくれよ。」 | Tokimeki Memorial (1994) / Saotome Yoshio (the game's opening exchange) | https://dic.pixiv.net/a/%E8%97%A4%E5%B4%8E%E8%A9%A9%E7%B9%94 |
| bookshelf click 1 | My reading list isn't ready yet. Soon! | original (plain) |  | - | - |
| bookshelf click 2 | I barely got to do any reading today, so... | verbatim |  | Doki Doki Literature Club! / Natsuki | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-ch3.rpy#L916 |
| bookshelf repeat | Why would you waste that on the top shelf? | verbatim |  | Doki Doki Literature Club! / Natsuki | https://github.com/Monika-After-Story/DDLCModTemplate/blob/master/original_story_scripts/script-exclusives-natsuki.rpy#L332 |
| butterfly hover | I love butterflies. They are the best animal. | verbatim |  | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-rin.rpy#L7126 |
| butterfly click 1 | That one's my Bluesky. I'm there sometimes. | original (plain) |  | - | - |
| butterfly click 2 | It wouldn't be so bad to be the sky. | verbatim |  | Katawa Shoujo / Rin Tezuka | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-rin.rpy#L6436 |
| butterfly repeat | Chicken? Why would I be a bird? | verbatim |  | Tsukihime -A piece of blue glass moon- | https://vndb.org/v17909 (VNDB quote q578) |
| tv hover | You've found the television, then. | verbatim |  | Katawa Shoujo / Lilly Satou | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a3-lilly.rpy#L2234 |
| tv click 1 | That's where I log all the movies I watch. | original (plain) |  | - | - |
| tv click 2 | Let's go watch! | verbatim |  | Katawa Shoujo / Yuuko Shirakawa | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a2-hanako.rpy#L635 |
| tv repeat | It's pro wrestling! Woo! Woo! | translated (from Japanese) | 早乙女優美「プロレスだー。ウォーウォー。」 | Tokimeki Memorial (1994) / Saotome Yumi | https://dic.pixiv.net/a/%E6%97%A9%E4%B9%99%E5%A5%B3%E5%84%AA%E7%BE%8E |
| plush hover | The panda says, 'Gao, gao!' | adapted (stegosaurus → panda) | The stegosaurus says, 'Gao, gao!' | AIR / Kamio Misuzu | https://vndb.org/v36 (VNDB quote q5552) |
| plush line 1 | Of course the panda can't win. It's a panda. | verbatim |  | Toushin Toshi II (PC-98, 1990) | https://vndb.org/v889 (VNDB quote q3077) |
| plush line 2 | Sorry, I was born cute. | verbatim |  | G-senjou no Maou | https://vndb.org/v211 (VNDB quote q446) |
| idle 1 | It's nice and quiet in here, isn't it? | verbatim |  | Katawa Shoujo / Lilly Satou | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-sunday.rpy#L3709 |
| idle 2 | Do... would you like some tea? | verbatim | Do… would you like some tea? (ellipsis as three dots) | Katawa Shoujo / Hanako Ikezawa | https://github.com/gcammisa/KatawaShoujo-RenPy8/blob/4d7852e/game/script-a1-sunday.rpy#L4271 |
| idle 3 | Luck comes to those who smile. So, smile! | translated (from Japanese; the end of a longer line) | 法条まりな「…笑う門には福来る、よ。さっ、笑って。」 | EVE burst error (1995, PC-98) / Houjou Marina | https://pro-botti.com/marina-famous_lines/ |
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

Totals: 47 lines: 29 verbatim, 8 adapted, 10 original plain lines.
