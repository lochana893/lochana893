# Tuk Tuk Dash

Phone eken gahanna puluwan three-wheeler game ekak. Bus, car, harak saha potholes maga harala coins ekathu karanna.

- **Controls:** screen eka swipe karanna, nathnam left/right side eka tap karanna. Computer eke arrow keys.
- **Thambili** ekak gaththama ek crash ekakin bera wenna puluwan.
- Score = meters + (coins × 10). Best score eka phone eke save wenawa.

Game eka **ekama file ekak**: `game/index.html`. Install karanna deyak naha, browser eke wada karanawa.

---

## 1. Game eka online daanna (free)

**GitHub Pages (lesima widiya):**
1. Me branch eka `main` ekata merge karanna.
2. GitHub repo eke **Settings → Pages** walata yanna.
3. *Source* = `Deploy from a branch`, *Branch* = `main`, folder = `/ (root)` → **Save**.
4. Minute 1–2 kin game eka me link eke thiyenawa:
   `https://lochana893.github.io/lochana893/game/`
5. E link eka phone eken open karala **Add to Home screen** dunnama app ekak wage open wenawa.

**itch.io:** `index.html` eka zip karala itch.io eke "HTML" project ekak widihata upload karannath puluwan.

---

## 2. Salli hoyana widi

Game ekata salli enne **ads** walin. Players la ad balanakota ad company eka oyata salli gewanawa, eka masekata ekathu wela oyage bank ekata enawa.

### A) Game portals (patan ganna hodama widiya)
CrazyGames, GameDistribution, Poki wage sites walata game eka submit karanna puluwan. Eyala game eka hamotama pennala, ads daala, ena aadayamen kotasak oyata denawa. Oyata ads setup karanna one naha.
- Submit karaddi eyala denna kiyana SDK eka (ads code eka) game ekata add karanna one. Game eke `Ads` kiyana kotasa (index.html eke) eka sandaha hadala thiyenne: "Drive again" athara ad ekak, "Keep driving" ekata reward ad ekak.
- Payment method eka (bank transfer / Payoneer) eyalage payout settings walin balala thoranna.

### B) Google AdSense (oyage website eke)
1. Game eka oyage website ekaka (GitHub Pages ho own domain) daanna.
2. adsense.google.com eke account ekak hadala apply karanna. Approve wenna kalayak yanawa.
3. Approve unama `index.html` eke udinma thiyena **ADS** comment eke thiyena code eka uncomment karala, `ca-pub-XXXX` thanata oyage publisher ID eka daanna.
4. **Payments → Payment methods** walin **Wire transfer** add karanna: bank name, account number, SWIFT code (bank eken ahanna), account name (ID eke thiyena nama ma).
5. Balance eka **USD 100** pan unama Google eken bank ekata yawanawa.

### C) Android app ekak (Google Play + AdMob)
Game eka PWABuilder ho Capacitor walin Android app ekak karala Play Store eke daanna puluwan.
- Google Play developer account eka: USD 25 (ek warak).
- Aluth personal accounts walata production release ekata kalin testers 12 dena 14 days test karanna one.
- Ads walata AdMob; payment eka AdSense wage wire transfer walin bank ekata.

### Sri Lanka walin salli ganna
- **Bank wire transfer** (SWIFT) ho **Payoneer** (Payoneer eken passe local bank ekata withdraw karanna) hodai.
- PayPal walin Sri Lanka walata salli receive karanna saamanyayen bahe, e nisa eka thoranna epa.
- Foreign remittance gana oyage bank eken ahala danagannna.

---

## 3. Wadagath dewal

- **Aththa katha:** ads walin ena salli eka play ekakata cents kihipayak witharai. Hodata salli enna nam **godak** players la one. TikTok, Facebook, WhatsApp groups wala game eka share karanna; gameplay clips daanna.
- **Oyage ads oyama click karanna epa**, yaluwanta click karanna kiyannath epa. Google account eka ban wenawa, salli denne naha.
- Players lata "game eka gahala salli hoyanna puluwan" kiyala kiyanna epa. Ehema kiyana eka ad rules walata pitin.
- Bank password, OTP, PIN kisima kenekuta denna epa. Bank details daanna one AdSense / portal eke official site eke witharai.
