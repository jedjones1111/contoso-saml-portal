# SAML Portal - Configuration Checklist

## Step 1 - Create Azure App Service
1. portal.azure.com > App Services > Create
2. Runtime: Python 3.11
3. OS: Linux
4. Plan: Free F1 (sufficient for demo)
5. Name: contoso-saml-portal (or your choice)
6. Note the URL: https://YOUR-APP-NAME.azurewebsites.net

## Step 2 - Create New Entra Enterprise App (SAML)
1. Entra ID > Enterprise Applications > New Application > Create your own
2. Name: Contoso Document Portal (SAML)
3. Select: Integrate any other application you don't find in the gallery
4. Click Create

## Step 3 - Configure SAML SSO
1. In the new enterprise app > Single sign-on > SAML
2. Set these values:

   Identifier (Entity ID):
   https://YOUR-APP-NAME.azurewebsites.net/saml/metadata

   Reply URL (ACS URL):
   https://YOUR-APP-NAME.azurewebsites.net/saml/acs

   Sign on URL:
   https://YOUR-APP-NAME.azurewebsites.net/

3. Save

## Step 4 - Download Federation Metadata XML
1. In the SAML config page, under SAML Signing Certificate
2. Click Download next to Federation Metadata XML
3. Save the file

## Step 5 - Get the certificate for settings.json
1. In the SAML Signing Certificate section
2. Copy the Certificate (Base64) value
3. Open saml/settings.json
4. Replace PASTE-ENTRA-CERTIFICATE-HERE with the certificate value (no line breaks)
5. Replace YOUR-TENANT-ID with your tenant ID: aa3331fc-1d02-4b13-b495-1a9e2429d98d
6. Replace YOUR-APP-SERVICE-NAME with your App Service name in all three SP fields

## Step 6 - Assign Users
1. Enterprise app > Users and groups > Add user
2. Add the demo account(s)

## Step 7 - Deploy to App Service
1. Create a new GitHub repo: contoso-saml-portal
2. Copy all files from this folder into it
3. Copy the 8 document files into static/files/
4. Push to GitHub
5. In App Service > Deployment Center > GitHub > select the repo
6. Set startup command to: gunicorn --bind=0.0.0.0:8000 app:app
7. Deploy

## Step 8 - Onboard into MDCA
1. security.microsoft.com > Settings > Cloud Apps > Connected apps > Conditional Access App Control apps
2. Click + Add
3. Search for Contoso Document Portal (SAML)
4. Follow the wizard - upload the Federation Metadata XML from Step 4
5. Complete onboarding

## Step 9 - Update CA Policy
1. Update the existing CA policy to target Contoso Document Portal (SAML) instead of the old OIDC app
2. Session control: Use Conditional Access App Control > Use custom policy
3. Enable

## Step 10 - Test
1. Open the App Service URL in InPrivate browser
2. You should be redirected to Microsoft login (SAML)
3. After login the URL should show .mcas.ms suffix
4. Click Download on any document
5. File should land on desktop with sensitivity label applied
