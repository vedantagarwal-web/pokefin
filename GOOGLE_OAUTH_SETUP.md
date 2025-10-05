# Google OAuth Setup Guide for Orthogonal

This guide will help you configure Google OAuth sign-in for your Orthogonal application.

## Prerequisites

- A Google Cloud Console account
- Access to your Supabase project dashboard
- Your Orthogonal application running locally

## Step 1: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google Identity API

## Step 2: Configure OAuth Consent Screen

1. In the Google Cloud Console, go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type (unless you're using Google Workspace)
3. Fill in the required fields:
   - **App name**: `Orthogonal`
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Add these scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
5. Add your domain to **Authorized domains**:
   - `localhost` (for development)
   - `empxwjsdjszlvbplmtts.supabase.co` (your Supabase project domain)

## Step 3: Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Web application**
4. Add these URLs:

   **Authorized JavaScript origins:**
   - `http://localhost:8787` (your frontend)
   - `http://localhost:8788` (your backend for development)

   **Authorized redirect URIs:**
   - `https://empxwjsdjszlvbplmtts.supabase.co/auth/v1/callback` (Supabase callback)
   - `http://localhost:8787/auth/callback.html` (your app callback)

5. Save and copy your **Client ID** and **Client Secret**

## Step 4: Configure Supabase

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard/project/empxwjsdjszlvbplmtts)
2. Navigate to **Authentication** > **Providers**
3. Find **Google** in the list
4. **Enable the Google provider** (this is crucial!)
5. Enter your credentials:
   - **Client ID**: (from Step 3)
   - **Client Secret**: (from Step 3)
6. **Add redirect URLs** in Supabase:
   - Go to **Authentication** > **URL Configuration**
   - Add `http://localhost:8787/auth/callback.html` to **Redirect URLs**
7. Save the configuration

**Important**: The Google provider must be enabled in Supabase for OAuth to work. If it's not enabled, you'll get errors when trying to sign in.

## Step 5: Test the Integration

1. Start your Orthogonal application:
   ```bash
   ./start-full-system.sh
   ```

2. Go to `http://localhost:8787`

3. Click **Sign In** or **Sign Up**

4. Click **Continue with Google**

5. You should be redirected to Google's OAuth consent screen

6. After authorizing, you should be redirected back to your app

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI" error**
   - Make sure all redirect URIs are exactly as specified in Step 3
   - Check that there are no trailing slashes

2. **"Access blocked" error**
   - Ensure your app is in "Testing" mode on the OAuth consent screen
   - Add test users if needed

3. **"Client ID not found" error**
   - Verify the Client ID is correctly entered in Supabase
   - Make sure the Google provider is enabled

4. **Localhost issues**
   - Ensure `http://localhost:8787` is in authorized origins
   - Check that your backend is running on port 8788

### Development vs Production

For production deployment, you'll need to:
- Update authorized origins and redirect URIs with your production domain
- Submit your app for verification if you need more than 100 users
- Update the Supabase redirect URL to your production domain

## Security Notes

- Never commit your Client Secret to version control
- Use environment variables for sensitive configuration
- Regularly rotate your OAuth credentials
- Monitor OAuth usage in Google Cloud Console

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google Cloud Console](https://console.cloud.google.com/)

## Next Steps

After setting up Google OAuth:

1. Test the complete authentication flow
2. Set up 2FA for additional security
3. Configure user profile management
4. Implement proper error handling for OAuth failures
