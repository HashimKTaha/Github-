# PrintJo seller ad: "Got a 3D printer? Put it to work."

`PrintJo_Sellers_Ad.mp4`: 56 s, 1080×1920 (9:16), 30 fps, H.264 + AAC, loudness −14 LUFS.
Made for Instagram Reels, Stories, TikTok and Meta ads. Arabic (Jordanian) on screen, English underneath.
Designed to work with the sound off, and every sound effect lines up with what happens on screen.

## Scenes
| Time | Scene |
| --- | --- |
| 0–4 s | Hook: an idle printer with cobwebs, "0.00 JOD this month" |
| 4–8 s | The problem: chasing buyers in DMs, guessing prices, a printer that runs 2 days a month |
| 8–12 s | The PrintJo logo printed layer by layer: "Jordan's 3D printing marketplace" |
| 12–34 s | 4 steps in the app: open your shop → requests from your city → set your price (instant estimate) → print, deliver, get paid (cash or CliQ) |
| 34–45 s | 0% commission in early access · why sell on PrintJo · cities from Irbid to Aqaba |
| 45–49 s | Proof: 1,000 medals for the Ministry of Youth |
| 49–56 s | Call to action: printjo.jo/join, "Join as a seller, it's free" |

## Caption (paste with the boost)
عندك طابعة 3D؟ خلّيها تشتغل.
PrintJo بيجيبلك طلبات طباعة من زباين بمدينتك. إنت بتختار الشغلة وبتحدد سعرك، وبتقبض كاش أو كليك.
وبدون أي عمولة بفترة الانطلاق.
سجّل ببلاش: printjo.jo/join

Got a 3D printer? Put it to work. Get paid print jobs from buyers in your city, at your price, with 0% commission during early access.

## Boost settings (from docs/content/growth-playbook.md)
- Objective: traffic to `printjo.jo/join?utm_source=instagram&utm_medium=paid&utm_campaign=sellers`
- Location: Jordan · Ages 18–45 · Interests: 3D printing, Bambu Lab, Creality, Prusa, maker, Thingiverse
- Stop rule: pause above 1.5 JOD per link click after 3 days

## Re-render
`source/index.html` holds the animation (`render(t)` for any second). `source/render.js` saves the frames and `source/audio.py` builds the soundtrack (numpy + scipy).
