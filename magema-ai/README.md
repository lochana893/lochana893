# 🎬 Magema AI

Prompt එකක් දෙන්න (photo එකකුත් දාන්න පුළුවන්) → **original quality** video එකක් ගන්න.
Watermark නැහැ, filters නැහැ, edit කරන්නේ නැහැ — **100% free, open-source**.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lochana893/lochana893/blob/main/magema-ai/Magema_AI_Colab.ipynb)

## ⏱️ තත්පර කීයක් උපරිම හදන්න පුළුවන්ද?

| Model | 1 generation (1 clip) | Auto-extend එක්ක (clips එකට join කරලා) | Quality |
|---|---|---|---|
| ⚡ **Fast** — LTX-Video 0.9.5 (2B) | **තත්පර ~10** (257 frames @ 24fps) | **තත්පර 60** | හොඳයි, ඉක්මනයි, free Colab T4 එකේ යනවා |
| 💎 **HQ** — Wan 2.2 TI2V-5B | **තත්පර ~5** (121 frames @ 24fps, 720p) | **තත්පර 60** | හොඳම quality, 24GB+ GPU එකක් හොඳයි |

- එක model call එකකින් හැදෙන්නේ ඉහත "1 clip" දිග විතරයි — ඒ model වලට train කරලා තියෙන උපරිමය ඒක.
- ඊට වඩා දිග video ඉල්ලුවොත් Magema **auto-extend** කරනවා: කලින් clip එකේ අන්තිම frames වලින් ඊළඟ clip එක පටන් ගන්නවා, ඊට පස්සේ ඔක්කොම **එක MP4 එකකට** join කරනවා.
- Extend කරන හැම වතාවකම quality ටිකක් drift වෙන්න පුළුවන්, ඒ නිසා **තත්පර 5–20** අතර හොඳම result එක.

## 🚀 Free විදිහට use කරන්නේ කොහොමද (Google Colab)

1. උඩ තියෙන **Open in Colab** button එක ඔබන්න.
2. **Runtime → Change runtime type → T4 GPU** → Save.
3. **Runtime → Run all**.
4. අන්තිමට එන `https://xxxx.gradio.live` link එක open කරන්න (phone එකෙනුත් පුළුවන්).
5. Prompt එක type කරන්න, ඕනේ නම් photo එකක් දාන්න, තත්පර ගණන තෝරලා **🎬 Generate Video** ඔබන්න.
6. **⬇️ Original MP4 download** එකෙන් video එක save කරගන්න.

> Colab free එකේ දවසට GPU පැය කිහිපයක් ලැබෙනවා. Idle වුණොත් disconnect වෙනවා — එතකොට ආයේ **Run all**.
> Kaggle Notebooks (සතියට GPU පැය 30 free) එකෙත් මේ විදිහටම run කරන්න පුළුවන්.

### ඔයාගේම PC එකේ (NVIDIA GPU, 16GB+ VRAM)

```bash
cd magema-ai
pip install -r requirements.txt   # Windows: CUDA torch එක pytorch.org එකෙන් install කරන්න
python app.py                      # http://localhost:7860
python app.py --share              # public link එකකුත් ඕනේ නම්
```

## 🖼️ "Original" කියන්නේ මොකක්ද

- Model එකෙන් එන frames **කෙලින්ම** MP4 එකට ලියනවා — upscale, filter, watermark, crop-to-template කිසිවක් නැහැ.
- Encode කරන්නේ **එක වතාවයි** (H.264, CRF 12 — ඇහැට lossless, phone එකේ play වෙනවා).
- Photo එකක් දැම්මොත් video size එක photo එකේ shape එකටම හදනවා; photo එක stretch කරන්නේ නැහැ (center crop විතරයි).

## ✍️ හොඳ prompt එකක් ලියන්නේ කොහොමද

- **English** වලින් ලියන්න — models වලට සිංහල අකුරු හොඳට තේරෙන්නේ නැහැ.
- කවුද/මොකක්ද + කරන දේ + තැන + camera එක + light එක:
  `A young man doing a rainbow flick on a sandy football court at sunset, camera tracking him at ground level, slow motion`
- **✨ Magic prompt** on කරලා තිබ්බොත් camera / light / quality details auto එකතු කරනවා.
- **Style** එකෙන් Realistic, Cinematic, Anime, 3D Cartoon, Drone, Product Ad වගේ look එකක් තෝරන්න.

## ⚠️ ඇත්ත කතාව — Dola එක්ක සසඳද්දී

Dola වගේ apps පාවිච්චි කරන්නේ ByteDance එකේ **Seedance** වගේ closed models, ලොකු data-center GPU වල.
Magema පාවිච්චි කරන්නේ ලෝකේ හොඳම **free open-source** models (LTX-Video, Wan 2.2) — quality එක ගොඩක් හොඳයි,
හැබැයි හැම prompt එකකටම Dola එකට සමාන වෙයි කියලා guarantee කරන්න බැහැ. Free T4 GPU එකේ HQ model එක slow;
හොඳම quality එකට Colab Pro (L4/A100) වගේ 24GB+ GPU එකක් පාවිච්චි කරන්න.

## 🛠️ Problems

| Problem | විසඳුම |
|---|---|
| `GPU memory මදි` / out of memory | **Fast draft** quality තෝරන්න, නැත්නම් තත්පර අඩු කරන්න |
| `GPU එකක් හම්බුනේ නැහැ` | Colab: Runtime → Change runtime type → T4 GPU |
| පළමු video එකට ගොඩක් වෙලා යනවා | පළමු වතාවට model එක (GB 15–25) download වෙනවා; ඊළඟ ඒවා ඉක්මනයි |
| HQ model එක T4 එකේ ගොඩක් slow | Fast model එක හෝ Fast draft පාවිච්චි කරන්න |

## 📁 Files

```
magema-ai/
├── app.py                  # Gradio web app (UI)
├── Magema_AI_Colab.ipynb   # 1-click free Colab notebook
├── magema/
│   ├── config.py           # models, තත්පර / frame / size ගණනය
│   ├── engine.py           # model load + video generate + auto-extend
│   ├── prompts.py          # Magic prompt + styles
│   └── video.py            # original-quality MP4 writer (ffmpeg)
└── tests/test_core.py      # CPU tests (python -m pytest tests)
```

Models: [LTX-Video 0.9.5](https://huggingface.co/Lightricks/LTX-Video-0.9.5) (Lightricks) ·
[Wan 2.2 TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers) (Apache-2.0).
Commercial use කරන්න කලින් එක එක model එකේ license එක Hugging Face එකේ බලන්න.
