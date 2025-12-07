# Cloudflare Worker Setup - Complete Walkthrough

## Step 1: Create Cloudflare Account (FREE - No Credit Card)

1. Open your browser and go to: **https://dash.cloudflare.com/sign-up**

2. Fill in:
   - Email: your email
   - Password: choose a password
   - Click "Create Account"

3. Verify your email (check inbox for Cloudflare email)

4. You'll land on the Cloudflare Dashboard

**✅ You should see**: A dashboard with options on the left sidebar

---

## Step 2: Create Your First Worker (1 minute)

1. In the **left sidebar**, click: **"Workers & Pages"**
   - If you don't see it, look for a hamburger menu (☰) to expand the sidebar

2. Click the **blue "Create application" button** (top right)

3. Click **"Create Worker"** (first option, has a lightning bolt icon)

4. **Name your worker**:
   - Default name appears (like `my-worker`)
   - Change it to: **`rezka-proxy`**
   - Click **"Deploy"** button

**✅ You should see**: "Your worker is live!" message

---

## Step 3: Add the Proxy Code (2 minutes)

1. You should see a page with your worker URL at the top:
   - Looks like: `https://rezka-proxy.YOUR-NAME.workers.dev`
   - **COPY THIS URL** - you'll need it later!

2. Click **"Edit code"** button (top right)

3. You'll see a code editor with sample code. **DELETE ALL OF IT**

4. Open the file `cloudflare-worker-proxy.js` from your project

5. **Copy the ENTIRE contents** of that file

6. **Paste it** into the Cloudflare code editor (replacing everything)

7. Click **"Save and deploy"** button (top right)

8. You'll see "Deployed successfully!" message

**✅ You should see**: Your worker code in the editor, with "export default" at the top

---

## Step 4: Test the Worker (Optional but Recommended)

1. Go back to the Workers & Pages list

2. Click on your **"rezka-proxy"** worker

3. Click the **"Logs"** tab

4. Open a new terminal and test:
   ```bash
   curl -X POST https://rezka-proxy.YOUR-NAME.workers.dev \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://rezka.ag/ajax/get_cdn_series/",
       "data": {"id": "80524", "translator_id": "238", "action": "get_movie"},
       "headers": {"User-Agent": "Mozilla/5.0"}
     }'
   ```

5. Replace `YOUR-NAME` with your actual subdomain

6. You should see a JSON response with stream URLs

**✅ If working**: You'll see `{"success":true,"url":"[720]https://..."}` with actual URLs

---

## Step 5: Configure Render (1 minute)

1. Go to **https://dashboard.render.com**

2. Click on your **web service** (your app)

3. Click **"Environment"** tab in the left menu

4. Click **"Add Environment Variable"** button

5. Fill in:
   - **Key**: `CLOUDFLARE_WORKER_URL`
   - **Value**: `https://rezka-proxy.YOUR-NAME.workers.dev`
     (the URL you copied in Step 3)

6. Click **"Save Changes"**

7. Render will automatically redeploy (takes 1-2 minutes)

**✅ You should see**: "Deploying..." status, then "Live" when done

---

## Step 6: Verify It's Working

1. After Render finishes deploying, check the **Logs** tab

2. Look for these messages:
   ```
   [INIT] Using custom HdRezkaApi v11.1.0
   [CLOUDFLARE_PROXY] Routing request through: https://rezka-proxy...
   [CLOUDFLARE_PROXY] Response received: success=True, has_url=True
   ```

3. Try accessing a video on your app

4. Check if it plays!

**✅ Success indicators**:
- Logs show `[CLOUDFLARE_PROXY]` messages
- Logs show `has_url=True` (not False!)
- Videos actually play

**❌ If still failing**:
- Check logs for errors
- Verify CLOUDFLARE_WORKER_URL is set correctly
- Check Cloudflare Worker logs for incoming requests

---

## Troubleshooting

### Worker not receiving requests:
1. Check Cloudflare Worker → Logs tab
2. Should see incoming POST requests
3. If empty, env var might be wrong

### Worker receiving requests but returning false:
1. rezka.ag might be blocking Cloudflare too (unlikely)
2. Try the paid proxy options (see ANTI_BLOCKING_TRICKS.md)

### Environment variable not taking effect:
1. Make sure you clicked "Save Changes"
2. Wait for redeploy to finish
3. Check Render Logs for the new variable

---

## Summary

**What you just did**:
1. ✅ Created free Cloudflare account
2. ✅ Deployed a Worker (proxy server)
3. ✅ Connected your Render app to use it
4. ✅ Now requests go: Render → Cloudflare → rezka.ag

**Cost**: $0 (100,000 requests/day free)

**Expected success rate**: 60-80%

**Next steps if it works**:
- Nothing! Just enjoy your working app 🎉

**Next steps if it doesn't work**:
- See ANTI_BLOCKING_TRICKS.md for paid proxy options (~$30/month)
- Try alternative hosting (Railway, Fly.io)

---

## Quick Reference

**Your Worker URL**: `https://rezka-proxy.YOUR-NAME.workers.dev`

**Render Env Var**:
- Key: `CLOUDFLARE_WORKER_URL`
- Value: (your worker URL)

**Check if working**:
```bash
# See Render logs for:
[CLOUDFLARE_PROXY] has_url=True  # ✅ Good!
[CLOUDFLARE_PROXY] has_url=False # ❌ Still blocked
```

Good luck! 🚀
