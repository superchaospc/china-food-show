# The China Food Show

[English](#english) · [简体中文](#简体中文)

## English

A Codex skill for turning a street-food video into an English edition. The burned-in English dialogue and SRT use the words from the final dub and the exact visible frames of the corresponding Chinese subtitle. If the vendor says **“Bag or bowl?”**, those words appear and disappear with the corresponding Chinese line. Translations of written-only signs and captions follow the frames where the original text appears.

**Required before delivery.** Chinese and English subtitles must appear, change and disappear on the same video frames, including one-frame gaps. Keep every quoted price and its USD conversion on the same English line in both the MP4 and SRT, for example `50 yuan (≈ US$7.49) for 250 g`. Apply this to repeated quotes, container fees and totals. A one-frame mismatch, a split price or a conversion shown only in a corner must be fixed before delivery.

### Install and try it

Use Python 3.10 or later and install FFmpeg with ffprobe, libass, and libx264. On macOS, the optional Chinese OCR helper uses Swift and Apple Vision. Clone the release into a **new** Codex skill directory:

```sh
git clone --branch v1.1.1 https://github.com/superchaospc/china-food-show.git ~/.codex/skills/china-food-show
cd ~/.codex/skills/china-food-show
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python examples/smoke_test.py
```

The smoke test creates a two-second synthetic clip, burns two captions, mixes an audio track, and checks the decoded frames. It runs locally without an account or paid API calls. In a new Codex chat, try: **“Use $china-food-show to make an English edition of this food video: [your link].”** Supply an authorized local source or a downloader that can retrieve the link. The episode helper binds and inspects files; Codex coordinates the download and production steps.

### What an episode includes

| Stage | Result |
| --- | --- |
| Picture | Prefer dedicated watermark-removal software when authorized. Check the actual job quote before using paid credits. Inspect moving textures before adding a transparent logo. |
| Captions | Compare every spoken turn against the burned-in dialogue and SRT, including brief replies. Verify the rendered frames separately. Every original price and its USD equivalent must remain together on the same English subtitle line in both MP4 and SRT. |
| Voices and sound | Cast the people who actually speak. Use one voice for a solo host, stable voices for a conversation, or ambience alone for a silent scene. Keep the sound of cooking; lower optional music under speech. |
| Posters | Choose one real frame that shows what makes the episode distinctive. Crop that photograph for both English posters, 1080 × 1440 (3:4) and 1080 × 1920 (9:16). |

Each episode has its own folder under the selected publishing directory. Include a full vertical MP4, an additional 2:59 cut only for episodes longer than 3:00, the two portrait posters, and UTF-8 `Title and Description.txt`. Put the English title on the first line, leave a blank line before the description, and end with `#chinesefood #streetfood #cooking`. Keep the SRT in the workspace.

For the Sichuan episode, the large white-and-yellow **The China Food Show** title sits above two smaller lines: **Every Dish Is $1.80** and **Sichuan, China**. The price applies to each dish. When revising the copy on an approved cover, start with that cover and keep its photograph, crop, title and rules in place. Check focus and food texture at full size in both poster crops. Use US dollars for prices on English covers, titles and descriptions. Verify the exchange rate and portion for each episode. For example, a 250 g serving costing about US$7.49 can use **Worth $7.49?**

**Where to post the full episode.** A public four-minute Facebook Reel can be recommended to new viewers. Originality also affects distribution. On Instagram, use a cut of three minutes or less when the goal is reaching new viewers through recommendations. Existing followers can watch a longer version. [Facebook Reels](https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/) · [Facebook originality guidelines](https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/) · [Instagram Reels](https://help.instagram.com/2720958398006062)

Bring your own footage, authorized voices, music, and optional transparent logo. ElevenLabs is needed only to generate new speech. The script can inspect the plan and cache first; only `--generate` submits uncached turns. Desktop software, third-party services, and account credits are supplied by the operator.

[Caption timing](references/captions.md) · [Dubbing and mixing](references/audio.md) · [Picture finishing](references/finish.md) · [Cover design](references/covers.md)

## 简体中文

这个 Codex 技能把街头美食实拍做成英文版。画面英文对白和英文 SRT 使用最终配音的原词，与对应中文字幕同帧出现、切换和消失，保留每一帧空窗。摊主说 **“Bag or bowl?”**，英文字幕就用这句话。只出现在画面上的菜单或文字，按原文可见的帧翻译。

**强制交付条件。** 中英文字幕必须同帧出现、换句和消失，连一帧空窗也要保持一致。每次报价都在原价后同行括注美元，例如 `50 yuan (≈ US$7.49) for 250 g`。重复报价、碗费和合计都要标注，烧录版和独立 SRT 一致。发现一帧偏差、原价与美元分行，或美元只出现在左上角等独立浮层，必须修正并复验。

### 安装和试跑

准备 Python 3.10 或更高版本，以及带 ffprobe、libass 和 libx264 的 FFmpeg。可选的中文 OCR 使用 macOS 的 Swift 和 Apple Vision。将仓库克隆到**新的** Codex 技能目录，运行上方安装命令。最后一条命令会用两秒合成素材完成混音、烧录和逐帧检查，全程在本地运行，无需登录或付费。

打开新的 Codex 对话，发送 **“用 $china-food-show 把这个美食链接做成英文成片：[视频链接]”**。可以提供有权使用的本地原片，也可让 Codex 调用已配置的下载工具取回视频。

### 每集交付

| 环节 | 处理方式 |
| --- | --- |
| 画面 | 需要去水印时优先用专业软件，付费提交前核对实际报价。先检查菜叶、手和锅沿移动时的修复效果，再按原水印位置叠加自备透明台标。 |
| 字幕 | 将配音定稿逐句对照画面英文对白和 SRT，核对短答、换人、缩句和实际发声时间，再检查成片字幕帧。每次原价后必须在同一行英文字幕内括注美元，烧录版和 SRT 一致。中英文相差一帧或报价缺少同行美元括注，均须修正后再交付。 |
| 声音 | 按实际发言人数选声，支持单人、多人和无对白。保留炒菜和餐具声，可选配乐在说话时自动放轻。 |
| 海报 | 先确定本集最特别的卖点，只选一张能看出份量、场地或做法的实拍主图，用同一帧分别裁切制作 3:4 和 9:16 英文海报。 |

在指定发布目录下每集建一个文件夹，放完整竖屏 MP4、两张竖版海报和一份 UTF-8 的 `Title and Description.txt`。原片超过 3:00 时另交 2:59 精简版，同集两版用文件名区分。TXT 首行写英文标题，空一行写简介，末行为 `#chinesefood #streetfood #cooking`。SRT 留在工程目录。

四川这集沿用第一版封面。白黄大字节目名 **The China Food Show** 下方放两行小字，分别写 **Every Dish Is $1.80** 和 **Sichuan, China**，让观众一眼看懂每道菜的价格和拍摄地点。修改已定稿封面的文案时，沿用原图、裁切、节目名和分隔线。两张海报分别放大检查食物纹理。英文封面、标题和简介统一使用美元，按当集汇率和实际份量换算。例如，250 克一份折合约 7.49 美元，封面可写 **Worth $7.49?**。

**四分钟完整版可以发到哪里？** Facebook 的公开 Reel 即使长四分钟，也有机会被推荐给新观众，原创性同样会影响分发。Instagram 版如果希望通过推荐触达新观众，时长控制在三分钟以内（含三分钟）；已有粉丝可以观看更长的版本。[Facebook 视频说明](https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/) · [Facebook 原创指南](https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/) · [Instagram 时长说明](https://help.instagram.com/2720958398006062)

公开版使用你自己的素材、合法可用的音色、配乐和可选台标。生成新旁白时才需要 ElevenLabs；先查看计划和缓存，显式使用 `--generate` 才会提交未生成的台词。TikTok 的 3:4 是封面素材比例，App 常规发布流程是从视频中选择封面帧。

[字幕与验帧](references/captions.md) · [配音与混音](references/audio.md) · [去水印与导出](references/finish.md) · [两种竖版海报的制作说明](references/covers.md)

[MIT License](LICENSE)
