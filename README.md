# Social Media Metrics — OpenClaw Skill

An OpenClaw skill for fetching follower counts across 11+ social media platforms including YouTube, TikTok, Bilibili, Douyin, Kuaishou, Instagram, and more.

## Supported Platforms

| Platform | Method | URL Input | Nickname Input |
|----------|--------|-----------|----------------|
| Bilibili (哔哩哔哩) | API | Yes | Yes |
| YouTube | API / Browser | Yes | Yes |
| Douyin (抖音) | Browser | Yes | Yes |
| Kuaishou (快手) | Browser | Yes | Yes |
| Xiaohongshu (小红书) | Browser | Yes | Yes |
| TikTok | Browser | Yes | Yes |
| Instagram | Browser | Yes | Yes |
| WeChat Video (视频号) | Browser | No | No |
| Toutiao (头条号) | Browser | Yes | Yes |
| Baijiahao (百家号) | Browser | Yes | Yes |
| iQiyi (爱奇艺) | Browser | Yes | Yes |

## Installation

### As an OpenClaw Skill

```bash
clawhub install social-metrics
```

### Manual Setup

```bash
git clone https://github.com/user/openclaw-social-metrics.git
cd openclaw-social-metrics
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Via OpenClaw

Once installed, simply ask your AI assistant:

- "帮我查一下影视飓风在B站的粉丝数"
- "How many followers does MrBeast have on YouTube?"
- "查询 https://space.bilibili.com/946974 的粉丝数据"

### Via Command Line

**Fetch by URL:**

```bash
python scripts/main.py --url "https://space.bilibili.com/946974"
```

**Fetch by nickname:**

```bash
python scripts/main.py --nickname "影视飓风" --platform bilibili
```

### Output Format

```json
{
  "platform": "bilibili",
  "username": "影视飓风",
  "uid": "946974",
  "url": "https://space.bilibili.com/946974",
  "metrics": {
    "followers": 12345678
  },
  "fetched_at": "2026-03-13T12:00:00+00:00",
  "success": true,
  "error": null
}
```

## Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `YOUTUBE_API_KEY` | No | YouTube Data API v3 key. Falls back to browser scraping if not set. |

## How It Works

- **API-first**: Platforms with public APIs (Bilibili, YouTube) are queried via HTTP requests for speed and reliability.
- **Browser fallback**: All other platforms use Playwright (headless Chromium) to render profile pages and extract follower counts.
- **Smart input resolution**: Accepts both profile URLs and account nicknames. URLs are parsed to detect the platform and extract user IDs automatically.

## License

MIT
