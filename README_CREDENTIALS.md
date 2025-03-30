# Secure API Key Storage

## Overview

This project now supports storing your OpenAI API key in your system's secure credential store instead of in plain text in the `.env` file. This provides better security for your API key as it's protected by your system's security mechanisms.

## How It Works

1. The application will first try to retrieve the API key from your system's credential store.
2. If the key is not found in the credential store, it will fall back to reading from the `.env` file.
3. When using the `.env` file, you'll see a recommendation in the logs to migrate to the secure credential store.

## Setting Up Secure Credentials

A setup script is provided to help you migrate your API key to the secure credential store:

```bash
python scripts/setup_credentials.py
```

This script will:
1. Check if an API key exists in your `.env` file
2. If found, ask if you want to store it in the credential store
3. Optionally remove the key from the `.env` file for added security
4. If no key is found, prompt you to enter your API key

## Benefits of Secure Storage

- Your API key is not stored in plain text in any file
- The key is protected by your operating system's security mechanisms
- Only this application can access the stored key
- Reduces the risk of accidentally exposing your API key when sharing code

## Manual Key Management

If you prefer to manage your API key manually:

### Windows
The Windows Credential Manager stores your API key securely.

### macOS
The macOS Keychain securely stores your API key.

### Linux
Depending on your distribution, your key will be stored in the Secret Service API, KWallet, or a similar secure storage mechanism.

## Troubleshooting

If you encounter issues with the credential store:

1. Run the setup script again to update your stored key
2. You can always fall back to using the `.env` file by adding your API key there
3. Check the application logs for any specific error messages

## Security Best Practices

- Never commit your API key to version control
- Regularly rotate your API keys
- Use the secure credential store whenever possible
- If you must use the `.env` file, ensure it's added to your `.gitignore`