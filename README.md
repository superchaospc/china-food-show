# The China Food Show

[English](#english) · [简体中文](#简体中文)

## English

A Codex skill for turning a street-food video into an English edition. The burned-in English dialogue and SRT use the words from the final dub and the exact visible frames of the corresponding Chinese subtitle. If the vendor says **“Bag or bowl?”**, those words appear and disappear with the corresponding Chinese line. Translations of written-only signs and captions follow the frames where the original text appears.

**Required before delivery.** Chinese and English subtitles must appear, change and disappear on the same video frames, including one-frame gaps. Keep every quoted price and its USD conversion on the same English line in both the MP4 and SRT, for example `50 yuan (≈ US$7.49) for 250 g`. Apply this to repeated quotes, container fees and totals. A one-frame mismatch, a split price or a conversion shown only in a corner must be fixed before delivery.

### Install and try it

Use Python 3.10 or later and install FFmpeg with ffprobe, libass, and libx264. On macOS, the optional Chinese OCR helper uses Swift and Apple Vision. Clone the release into a **new** Codex skill directory:

```sh
git clone --branch v1.2.0 https://github.com/superchaospc/china-food-show.git ~/.codex/skills/china-food-show
cd ~/.codex/skills/china-food-show
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python examples/smoke_test.py
```

The smoke test creates a two-second synthetic clip, burns two captions, mixes an audio track, and checks the decoded frames. It runs locally without an account or paid API calls. In a new Codex chat, try: **“Use $china-food-show to make an English edition of this food video: [your link].”** Supply an authorized local source or a downloader that can retrieve the link. The episode helper binds and inspects files; Codex coordinates the download and production steps.

### The four publishing files

| File | What the viewer sees |
| --- | --- |
| 4:3 MP4 | A fixed center crop. For 1920×1080 footage, trim 240 pixels on each side to retain 1440×1080. |
| 9:16 MP4 | The same 4:3 picture centered edge to edge, with pure black above and below. A 1440×2560 canvas adds exactly 740 rows on each end. |
| `Poster-3x4.jpg` | 1080×1440, based on the approved portrait. |
| `Poster-9x16.jpg` | 1080×1920, with the same portrait and headline. |

For a source over 3:00, cut the story to 2:59 first. Shorter sources and sources exactly 3:00 retain their runtime. Cut the isolated voices, ambience and captions to the locked picture, then lay a continuous score over the finished edit. Both MP4s share the same frame timing, captions, upper-right badge and final AAC audio. Preserve the existing subtitle treatment, with English directly above Chinese.

Both posters use the existing Wayne’s Price Tag portrait in the creator’s setup. Other installations can provide their own approved square portrait. The headline states the whole-dollar price, quantity and food on one baseline. For ¥35 per slice, verified at US$5.22, the headline reads **$5 FOR ONE SLICE OF PORK**. The location reads **chengdu, sichuan, china** and ¥35 appears in smaller type. Poster prices round half up to whole dollars. Dialogue subtitles preserve the precise USD conversion.

```sh
python scripts/profile_posters.py --profile portrait.png \
  --location 'chengdu, sichuan, china' --usd 5.22 \
  --unit 'FOR ONE SLICE OF PORK' --original '¥35' --output-dir posters
```

Keep working files, the SRT, posting copy and earlier cuts in the episode workspace. Supply your own portrait, opaque badge, footage, music and authorized voices. The poster renderer uses macOS system fonts or DejaVu fonts on other platforms. The optional ElevenLabs services require an account when generating new voices or music. The offline smoke test uses synthetic inputs.

[Caption timing](references/captions.md) · [Dubbing and mixing](references/audio.md) · [Badge and export](references/finish.md) · [Video geometry](references/vertical.md) · [Poster layout](references/covers.md)

## 简体中文

这个 Codex 技能把街头美食实拍做成英文版。画面英文对白和英文 SRT 使用最终配音的原词，与对应中文字幕同帧出现、切换和消失，保留每一帧空窗。摊主说 **“Bag or bowl?”**，英文字幕就用这句话。只出现在画面上的菜单或文字，按原文可见的帧翻译。

**强制交付条件。** 中英文字幕必须同帧出现、换句和消失，连一帧空窗也要保持一致。每次报价都在原价后同行括注美元，例如 `50 yuan (≈ US$7.49) for 250 g`。重复报价、碗费和合计都要标注，烧录版和独立 SRT 一致。发现一帧偏差、原价与美元分行，或美元只出现在左上角等独立浮层，必须修正并复验。

### 安装和试跑

准备 Python 3.10 或更高版本，以及带 ffprobe、libass 和 libx264 的 FFmpeg。可选的中文 OCR 使用 macOS 的 Swift 和 Apple Vision。将仓库克隆到**新的** Codex 技能目录，运行上方安装命令。最后一条命令会用两秒合成素材完成混音、烧录和逐帧检查，全程在本地运行，无需登录或付费。

打开新的 Codex 对话，发送 **“用 $china-food-show 把这个美食链接做成英文成片：[视频链接]”**。可以提供有权使用的本地原片，也可让 Codex 调用已配置的下载工具取回视频。

### 每集四件交付

| 文件 | 成品规格 |
| --- | --- |
| 4:3 视频 | 左右等量、固定居中裁切。1920×1080 原片左右各裁 240 像素，得到 1440×1080。 |
| 9:16 视频 | 完整保留同一幅 4:3 画面。1440×2560 的竖屏上下各加 740 像素纯黑，两侧贴边。 |
| `Poster-3x4.jpg` | 1080×1440，以已确认的人像为底。 |
| `Poster-9x16.jpg` | 1080×1920，沿用同一张人像和本集标题。 |

原片超过 3 分钟时先剪至 2:59，等于或短于 3 分钟时保留原时长。先锁定剪点，按同一时间轴剪独立人声、现场声和字幕，再连续铺 ElevenLabs 或其他已获授权的配乐。两版视频共用同一条最终 AAC。沿用原字幕样式，英文在中文上方；黑金角标贴在 4:3 内容区右上角。

海报只在定稿人像上加字。主标题写清**多少钱、买多少、买什么**。例如 35 元一片猪肉折合 5.22 美元，两张海报均写 **$5 FOR ONE SLICE OF PORK**。美元按四舍五入取整数，金额和英文说明共用字体基线。地点行沿用用户给定的大小写，例如 **chengdu, sichuan, china**。原价 ¥35 可作小字，底部省去主标题中已有的菜名。视频字幕保留精确美元括注。

上方命令会同时生成两张海报。每集交付目录只放表中的四个文件，SRT、发布文案、历史版本和其他工程材料保存在工作区。公开版使用自己的授权人像、角标、配乐和音色。

[字幕与验帧](references/captions.md) · [配音与混音](references/audio.md) · [角标与导出](references/finish.md) · [视频画幅](references/vertical.md) · [人像海报](references/covers.md)

[MIT License](LICENSE)
