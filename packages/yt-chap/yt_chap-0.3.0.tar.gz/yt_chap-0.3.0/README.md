# YT-CHAP

**yt-chap** is a clean and efficient command-line tool written in Python to fetch and display video chapters from **any URL supported by yt-dlp** — including YouTube, BiliBili, and Vimeo.

[![GitHub Stars](https://img.shields.io/github/stars/mallikmusaddiq1/yt-chap?style=social)](https://github.com/mallikmusaddiq1/yt-chap)
[![PyPI](https://img.shields.io/pypi/v/yt-chap)](https://pypi.org/project/yt-chap/)
[![Downloads](https://img.shields.io/badge/Downloads-N%2FA-lightgrey)](https://pypi.org/project/yt-chap/)
[![License](https://img.shields.io/github/license/mallikmusaddiq1/yt-chap)](https://github.com/mallikmusaddiq1/yt-chap/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)

---

## 🚀 Features

* **Multi-Format Output:** Three exclusive formats available — specify one:

  1. **Human-Readable Table** (`-t`, `--table`)
  2. **JSON** (`-j`, `--json`) for automation or integration.
  3. **FFmpeg Metadata** (`-f`, `--ffmpeg-metadata`) for embedding chapters into videos.
* Extracts video chapter metadata using `yt-dlp`.
* Precise timestamp formatting: `HH:MM:SS.mmm`.
* Graceful fallback if no chapters exist — creates a single *Full Video* entry.
* Checks for `yt-dlp` installation automatically and provides clear setup guidance.
* Quiet mode (`-q`) to suppress informational logs.

---

## 📦 Installation

`yt-chap` depends on **Python 3.6+** and **yt-dlp**.

### 1️⃣ Install yt-dlp

Ensure `yt-dlp` is installed and accessible via PATH.

```bash
pip install yt-dlp
```

*For alternative methods, visit the [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp#installation).*

### 2️⃣ Install yt-chap (From Source)

```bash
git clone https://github.com/mallikmusaddiq1/yt-chap.git
cd yt-chap
pip install .
```

---

## ⚙️ Usage

`yt-chap` requires a valid video URL and **one** format flag (`-t`, `-j`, or `-f`).

### 🧾 Table Output

```bash
yt-chap -t <VIDEO_URL>
```

**Example:**

```
[info] Chapters from: https://www.youtube.com/watch?v=xyz

No.  | Start         | End           | Duration      | Title
---------------------------------------------------------------
1    | 00:00:00.000  | 00:00:30.500  | 00:00:30.500  | Opening Scene
2    | 00:00:30.500  | 00:01:15.000  | 00:00:44.500  | Main Theme
3    | 00:01:15.000  | 00:02:00.000  | 00:00:45.000  | Bridge
4    | 00:02:00.000  | 00:03:30.000  | 00:01:30.000  | Conclusion
```

### 💡 JSON Output

```bash
yt-chap -j <VIDEO_URL>
```

Perfect for integration with scripts, web tools, or APIs.

### 🎬 FFmpeg Metadata Output

```bash
yt-chap -f <VIDEO_URL> > metadata.txt
```

Use `metadata.txt` with FFmpeg to embed chapter data into a video.

### 🧰 Options

| Flag | Long Form   | Description                             |
| ---- | ----------- | --------------------------------------- |
| `-q` | `--quiet`   | Suppress info messages and logs         |
| `-v` | `--version` | Show version and author info (`v0.3.0`) |

---

## 🔧 Requirements

* Python 3.6+
* yt-dlp

---

## 👤 Author

**Name:** Mallik Mohammad Musaddiq

**Email:** [mallikmusaddiq1@gmail.com](mailto:mallikmusaddiq1@gmail.com)

**GitHub:** [mallikmusaddiq1/yt-chap](https://github.com/mallikmusaddiq1/yt-chap)

---

## 📜 License

Licensed under the **MIT License**.
See the [LICENSE](https://github.com/mallikmusaddiq1/yt-chap/blob/master/LICENSE) file for details.