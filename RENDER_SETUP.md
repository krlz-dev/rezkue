# Render Deployment Setup

## Quick Start

HD-RZKA is ready to deploy on Render with minimal configuration.

## Render Configuration

### 1. Build Command

**Option 1 (Recommended):**
```bash
chmod +x build.sh && ./build.sh
```

**Option 2 (Alternative):**
```bash
bash build.sh
```

**Option 3 (Direct):**
```bash
pip install -r requirements.txt
```

### 2. Start Command
```bash
gunicorn run:app --bind 0.0.0.0:$PORT
```

### 3. Environment Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 5001 |
| `FLASK_ENV` | Environment mode | production |
| `DEBUG` | Debug mode | False |

## What Gets Installed

The build process installs:
- Flask 3.0.0 (web framework)
- Gunicorn 21.2.0 (production WSGI server)
- HdRezkaApi 7.1.0 (video API library)
- BeautifulSoup4 4.12.3 (HTML parsing)
- Flask-CORS 4.0.0 (CORS support)
- Requests 2.31.0 (HTTP library)

## How It Works

1. **API Requests**: Uses proper headers (Origin, Referer) to bypass blocking
2. **No Browser Automation**: Simple HTTP requests - fast and lightweight
3. **Low Resource Usage**: No headless browsers, minimal memory footprint

## Monitoring

Check your Render logs for these indicators:

**Success:**
```
[STREAM] Content type: tv_series
[STREAM] Available translators: ['HDrezka Studio', 'Дубляж']
[SUCCESS] Found 4 quality options
```

**API Blocked (check headers):**
```
[ERROR] API returned unexpected data type: 'bool' object has no attribute 'replace'
[ERROR] The server may be blocking API requests
```

## Performance

- **Response Time**: 1-3 seconds for stream requests
- **Memory Usage**: ~150-200MB
- **Recommended Plan**: Render Free tier works fine

## Troubleshooting

### Build Fails
- Ensure `build.sh` has execute permissions: `chmod +x build.sh`
- Check Python version (should be 3.8+)

### Stream Requests Fail
- Check if HdRezkaApi is blocked (error logs will show)
- Verify headers are being sent correctly
- Test locally: `DEBUG=true python3 run.py`

### Server Won't Start
- Ensure Gunicorn is in requirements.txt
- Verify start command uses correct port binding
- Check Render logs for startup errors

## Alternative Configuration

If you prefer not to use the build script:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command (Development):**
```bash
python run.py
```

**Start Command (Production):**
```bash
gunicorn run:app --bind 0.0.0.0:$PORT --workers 2
```

## Resource Requirements

- **CPU**: Minimal (0.1 CPU)
- **Memory**: 256MB minimum, 512MB recommended
- **Disk**: <100MB

## Notes

- No browser automation needed (removed Playwright dependency)
- Uses simple HTTP requests with proper headers
- Fast, lightweight, and cost-effective
- Works on Render's free tier
