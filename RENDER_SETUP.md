# Render Deployment Setup

## Configure Build Command

To enable Playwright browser automation on Render, you need to configure the build command:

1. Go to your Render dashboard
2. Select your web service
3. Go to **Settings**
4. Find the **Build Command** field
5. Set it to: `./build.sh`
6. Click **Save Changes**

## What the Build Script Does

The `build.sh` script:
- Installs Python dependencies from `requirements.txt`
- Installs Playwright Chromium browser with system dependencies
- Prepares the environment for browser automation

## How the Fallback Works

When the HdRezkaApi library is blocked (returning 503 errors):

1. **Primary Method**: Tries HdRezkaApi with browser headers
2. **Fallback Method**: If blocked, launches Playwright browser
3. **Browser Automation**: Navigates to the video page like a real user
4. **Stream Capture**: Intercepts AJAX requests to get stream URLs
5. **Success**: Returns stream data to the client

## Monitoring

Check your Render logs for these indicators:

**Success (API method):**
```
[STREAM] Content type: tv_series
[STREAM] Available translators: ['Translator 1', 'Translator 2']
[SUCCESS] Found 4 quality options
```

**Success (Playwright fallback):**
```
[ERROR] Failed to initialize HdRezkaApi: ...
[FALLBACK] Trying Playwright for blocked initialization...
[PLAYWRIGHT] Navigating to https://rezka.ag/...
[PLAYWRIGHT] Successfully captured 4 quality options
[FALLBACK] Success! Found 4 quality options
```

**Failure:**
```
[FALLBACK] Failed: Browser automation timeout
```

## Performance Notes

- Playwright fallback adds 3-10 seconds to response time
- Uses more memory than API calls
- Only activates when API method is blocked
- Consider upgrading Render plan if using fallback frequently

## Troubleshooting

If Playwright fails:
- Ensure build command is set to `./build.sh`
- Check that `playwright==1.41.0` is in requirements.txt
- Verify sufficient memory (recommend 512MB minimum)
- Check logs for Chromium installation errors

## Alternative: Render Environment Variables

If you prefer not to use the build script, you can manually configure:

**Build Command:**
```bash
pip install -r requirements.txt && playwright install --with-deps chromium
```

**Start Command:**
```bash
python run.py
```
