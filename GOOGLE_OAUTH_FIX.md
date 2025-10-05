# Fix Google OAuth redirect_uri_mismatch Error

## Problem
You're getting "Error 400: redirect_uri_mismatch" when trying to sign in with Google.

## Root Cause
The redirect URI configured in Google Cloud Console doesn't match the one your app is using.

## Solution - Update Google Cloud Console

### Step 1: Go to Google Cloud Console
1. Visit https://console.cloud.google.com/
2. Select your Orthogonal project
3. Go to **APIs & Services** → **Credentials**

### Step 2: Update OAuth Client ID
1. Find your OAuth 2.0 Client ID (it should be for "Web application")
2. Click on it to edit

### Step 3: Add the Correct Redirect URIs
Under **Authorized redirect URIs**, add BOTH of these URLs:

```
https://empxwjsdjszlvbplmtts.supabase.co/auth/v1/callback
http://localhost:8787/auth/callback.html
```

**Important Notes:**
- The first URL is Supabase's OAuth callback (REQUIRED for Supabase OAuth to work)
- The second URL is where users will be redirected after authentication
- Include both `http://` and `https://` versions if needed
- NO trailing slashes
- URLs must match EXACTLY (including protocol)

### Step 4: Add Authorized JavaScript Origins
Under **Authorized JavaScript origins**, add:

```
http://localhost:8787
http://localhost:8788
```

### Step 5: Save and Wait
1. Click **Save**
2. Wait 5-10 minutes for changes to propagate (Google's OAuth system needs time to update)

## Step 6: Verify Supabase Configuration

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/empxwjsdjszlvbplmtts
2. Go to **Authentication** → **Providers**
3. Find **Google** and make sure it's ENABLED
4. Enter your Google OAuth credentials:
   - Client ID: (from Google Cloud Console)
   - Client Secret: (from Google Cloud Console)
5. Under **Authentication** → **URL Configuration**, add:
   - Redirect URLs: `http://localhost:8787/auth/callback.html`
6. Save

## Testing

After configuration:

1. Wait 5-10 minutes for changes to propagate
2. Clear your browser cache or use incognito mode
3. Try signing in again

## If It Still Doesn't Work

Check the exact redirect URI being used:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Click "Sign in with Google"
4. Look at the OAuth request URL
5. Check the `redirect_uri` parameter
6. Make sure that EXACT URL is in your Google Cloud Console

## Common Mistakes

❌ **Don't include trailing slashes** unless your code uses them
❌ **Don't mix http and https** - they must match exactly
❌ **Don't forget the Supabase callback URL** - this is required for Supabase OAuth

✅ **Do wait 5-10 minutes** after saving changes
✅ **Do test in incognito mode** to avoid cache issues
✅ **Do check both Google Console AND Supabase dashboard** are configured correctly

## Need Help?

If you're still getting errors, provide:
1. The exact error message
2. The redirect URI from your DevTools Network tab
3. Screenshot of your Google Cloud Console redirect URIs

