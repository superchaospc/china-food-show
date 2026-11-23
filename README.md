# The China Food Show

[English](#english) · [简体中文](#简体中文)

## English

A Codex skill for turning a street-food video into an English edition. English subtitles appear and disappear on the same frames as the Chinese captions in the picture. The host and vendors can take turns speaking without forcing each subtitle to split when a voice changes.

### Install and try it

Use Python 3.10 or later and install FFmpeg with ffprobe, libass, and libx264. On macOS, the optional Chinese OCR helper uses Swift and Apple Vision. Clone the release into a **new** Codex skill directory:

```sh
git clone --branch v1.0.1 https://github.com/superchaospc/china-food-show.git ~/.codex/skills/china-food-show
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
| Captions | Short spoken English, prices in the original currency plus approximate USD, and an editable SRT. The final MP4 is checked for early, late, and missing captions. |
| Voices and sound | Cast the people who actually speak. Use one voice for a solo host, stable voices for a conversation, or ambience alone for a silent scene. Keep the sound of cooking; lower optional music under speech. |
| Covers | Two separate English-only compositions based on the episode: a 16:9 YouTube thumbnail and a 3:4 portrait cover asset for TikTok. Select frames with no visible Chinese captions or signs. |

For the Sichuan episode, the large white-and-yellow **The China Food Show** title sits above two smaller lines: **Every Dish Is $1.80** and **Sichuan, China**. The price applies to each dish. When revising the copy on an approved cover, start with that cover and keep its photograph, crop, title and rules in place. Check the price against the footage for each new episode.

**Where to post the full episode.** A public four-minute Facebook Reel can be recommended to new viewers. Originality also affects distribution. On Instagram, use a cut of three minutes or less when the goal is reaching new viewers through recommendations. Existing followers can watch a longer version. [Facebook Reels](https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/) · [Facebook originality guidelines](https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/) · [Instagram Reels](https://help.instagram.com/2720958398006062)

Bring your own footage, authorized voices, music, and optional transparent logo. ElevenLabs is needed only to generate new speech. The script can inspect the plan and cache first; only `--generate` submits uncached turns. Desktop software, third-party services, and account credits are supplied by the operator.

[Caption timing](references/captions.md) · [Dubbing and mixing](references/audio.md) · [Picture finishing](references/finish.md) · [Cover design](references/covers.md)

## 简体中文

这个 Codex 技能把街头美食实拍做成英文版。英文字幕跟随原片中文字逐帧出现、换句和消失。遇到摊主和拍摄者一问一答，配音按人分开；如果原画中文始终是同一条，对应的英文也同时显示。

### 安装和试跑

准备 Python 3.10 或更高版本，以及带 ffprobe、libass 和 libx264 的 FFmpeg。可选的中文 OCR 使用 macOS 的 Swift 和 Apple Vision。将仓库克隆到**新的** Codex 技能目录，运行上方安装命令。最后一条命令会用两秒合成素材完成混音、烧录和逐帧检查，全程在本地运行，无需登录或付费。

打开新的 Codex 对话，发送 **“用 $china-food-show 把这个美食链接做成英文成片：[视频链接]”**。可以提供有权使用的本地原片，也可让 Codex 调用已配置的下载工具取回视频。

### 每集交付

| 环节 | 处理方式 |
| --- | --- |
| 画面 | 需要去水印时优先用专业软件，付费提交前核对实际报价。先检查菜叶、手和锅沿移动时的修复效果，再按原水印位置叠加自备透明台标。 |
| 字幕 | 翻译成容易听懂的口语英语，报价保留原币并补充约合美元。交付 MP4 和英文 SRT，按解码后的画面检查字幕切换。 |
| 声音 | 按实际发言人数选声，支持单人、多人和无对白。保留炒菜和餐具声，可选配乐在说话时自动放轻。 |
| 封面 | 按本集菜品、地点和人物动作，分别排版 YouTube 横版 16:9 和 TikTok 竖版 3:4。封面只用英文，也要检查背景里的中文字幕和招牌。 |

四川这集沿用第一版封面。白黄大字节目名 **The China Food Show** 下方放两行小字，分别写 **Every Dish Is $1.80** 和 **Sichuan, China**，让观众一眼看懂每道菜的价格和拍摄地点。修改已定稿封面的文案时，沿用原图、裁切、节目名和分隔线。后续每集的价格以当集实拍为准。

**四分钟完整版可以发到哪里？** Facebook 的公开 Reel 即使长四分钟，也有机会被推荐给新观众，原创性同样会影响分发。Instagram 版如果希望通过推荐触达新观众，时长控制在三分钟以内（含三分钟）；已有粉丝可以观看更长的版本。[Facebook 视频说明](https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/) · [Facebook 原创指南](https://about.fb.com/news/2026/03/rewarding-original-creators-on-facebook/) · [Instagram 时长说明](https://help.instagram.com/2720958398006062)

公开版使用你自己的素材、合法可用的音色、配乐和可选台标。生成新旁白时才需要 ElevenLabs；先查看计划和缓存，显式使用 `--generate` 才会提交未生成的台词。TikTok 的 3:4 是封面素材比例，App 常规发布流程是从视频中选择封面帧。

[字幕与验帧](references/captions.md) · [配音与混音](references/audio.md) · [去水印与导出](references/finish.md) · [两种封面的制作说明](references/covers.md)

[MIT License](LICENSE)
