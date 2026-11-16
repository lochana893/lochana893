# Tuk Tuk Dash

Phone eken gahanna puluwan three-wheeler game ekak. Bus, car, harak saha potholes maga harala coins ekathu karanna.

- **Controls:** screen eka swipe karanna, nathnam left/right side eka tap karanna. Computer eke arrow keys.
- **Thambili** ekak gaththama ek crash ekakin bera wenna puluwan.
- Ekathu karana coins **wallet** ekata save wenawa. **Garage** eken ewa walin tuk-tuk ekata aluth paint ganna puluwan.
- Crash unama: **Keep driving** (ad ekak balala digatama yanna) saha **Double coins** (ad ekak balala coins deguna karanna).

Game eka **ekama file ekak**: `game/index.html`.

---

## Wadagathma deya: game coins ≠ dollars

Game eke coins **points witharai**. Ewa dollars walata maru karanna ho bank ekata yawanna **kisima game ekakata bahe**. Ehema puluwan kiyana "play and earn" apps godak welawata **scams**.

Aththa dollars enne **ads walin**:

```
Player game eka gahanawa → ad ekak balanawa → Google (advertiser) salli gewanawa
→ masekata ekathu wenawa → USD 100 pan unama → oyage bank ekata (USD)
```

Game eke ads pennana thaan 3k thiyenawa: "Drive again" athara, "Keep driving" saha "Double coins". Players la godak gahanna gahanna ad walin ena salli wadi wenawa.

---

## Step 1: Game eka online daanna (free)

1. Me branch eka `main` ekata merge karanna.
2. GitHub repo eke **Settings → Pages** → *Branch* = `main`, folder = `/ (root)` → **Save**.
3. Game eka: `https://lochana893.github.io/lochana893/game/`

AdSense walata **own domain** ekak (udaharanayak: `tuktukdash.com`, avurudda USD 10 witara) thiyenawa nam approve wenna lesi. Domain eka GitHub Pages ekata connect karanna puluwan (Settings → Pages → Custom domain).

## Step 2: Google AdSense account eka

1. https://adsense.google.com eke oyage Google account eken sign up wenna. Site eka widihata game eke link eka denna.
2. Approve wenakam inna (davas kihipayak ho sathi kihipayak). H5 Games Ads (game ads) walata wenama apply karanna one wenna puluwan.
3. **Account → Account information** eke thiyena **Publisher ID** eka copy karanna (`ca-pub-` walin patan ganna number eka).

## Step 3: Game ekata ID eka daanna (code danna one naha)

`game/index.html` file eka open karala udinma thiyena **YOUR SETTINGS** kotasa wenas karanna:

```js
window.TUK_CONFIG = {
  adsenseClient: 'ca-pub-1234567890123456',  // ← oyage ID eka
  adsTestMode: true,                          // test karala iwara unama false karanna
  supportUrl: ''                              // optional: oyage payment link eka
};
```

- `adsTestMode: true` → Google test ads pennanawa, salli enne naha. Wada karanawada balanna.
- `adsTestMode: false` → aththa ads, **aththa salli**.
- Save karala GitHub ekata aye upload karanna. Itapasse ads automatically wada karanawa.

## Step 4: Dollars bank ekata ganna

1. Oyage bank eke **USD account** ekak (foreign currency account, udaharanayak PFCA) open karanna. Ethakota salli dollars walinma thiyenawa; LKR walata convert wenne naha.
2. Bank eken **SWIFT code** eka saha account details ganna.
3. AdSense eke **Payments → Payment info → Add payment method → Wire transfer**: bank name, SWIFT code, account number, account name (ID eke nama ma).
4. Mulin balance eka USD 10 pan unama Google eken gedara address ekata **PIN letter** ekak ewanawa. Eka AdSense eke type karanna one.
5. Balance eka **USD 100** pan una masaye 21–26 wage dawaswala Google eken salli bank ekata wire karanawa.

**Withdraw button ekak naha.** Salli yawanne Google eken automatically. Game eke code eke bank details daanna epa. Bank details daanna one AdSense eke witharai.

## Optional: "Support the game" button

Players lata kemathi nam oyata kelinma salli denna puluwan. `supportUrl` ekata oyage payment page link eka (https://) daanna, ethakota menu eke **Support the game** button ekak penawa. Sri Lanka walin wada karana payment service ekak (udaharanayak: local payment gateway ekaka payment link ekak) thoraganna. PayPal walin Sri Lanka walata salli receive karanna saamanyayen bahe.

## Wena widi
- **Game portals** (CrazyGames, GameDistribution, Poki): website ekak nathuwa game eka submit karanna puluwan. Eyala ads daala aadayamen kotasak denawa. Eyalage SDK eka add karanna one.
- **Android app** (Google Play + AdMob): Play developer account eka USD 25 (ek warak). Aluth accounts walata testers 12 dena 14 days test karanna one.

---

## Rules (meka kadoth account eka ban wenawa)
- Oyage ads oyama click karanna **epa**. Yaluwanta click karanna kiyannath **epa**. Google eka allanawa, salli denne naha.
- Players lata "game eka gahala salli hoyanna puluwan" kiyala **kiyanna epa**.
- Bank password, OTP, PIN **kisima kenekuta denna epa**.

## Aththa katha
Ad walin ena salli eka play ekakata cents kihipayak witharai. Masekata dollars 100 ganna nam dawasakata players dahas gananak one wenna puluwan. TikTok, Facebook, WhatsApp groups wala gameplay clips share karanna.
