# Test if Environment Variable is Working

## On Render Dashboard:

1. Go to your service
2. Click **"Shell"** tab (in left sidebar)
3. Run this command:
   ```bash
   echo $CLOUDFLARE_WORKER_URL
   ```

4. **Expected output:**
   ```
   https://muddy-wildflower-354b.inf-carlos89.workers.dev
   ```

5. **If you see nothing or empty:**
   - The env var is NOT set correctly
   - Go back to Environment tab and add it again
   - Make sure to click "Save Changes"

## Alternative: Check in Logs

Look for this line when the app starts:
```
[INIT] Using custom HdRezkaApi v11.1.0
```

Right after that, add a print statement to show the env var value.
