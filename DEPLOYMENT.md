# How to Deploy "Skill Gap AI" for Free

This guide will show you how to deploy your Streamlit application to **Streamlit Community Cloud**, which is free and the easiest way to host this app.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account. If you don't have one, sign up at [github.com](https://github.com/).
2.  **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/) using your GitHub account.

---

## Step 1: Upload Your Code to GitHub

1.  **Create a New Repository** on GitHub (e.g., named `skill-gap-ai`).
2.  **Upload Files**: Upload all the files from your project folder (`c:\Users\karthik\OneDrive\Desktop\Skill Gap AI`) to this repository.
    *   **Crucial Files**: Ensure `main.py`, `requirements.txt`, and all `milestone*.py`, `components.py`, `charts.py` files are included.
    *   *Note: Do not upload the `.streamlit` folder if it contains secrets, but do upload `.streamlit/config.toml` if you have custom theme settings.*
    *   *Note: I have already updated your `requirements.txt` to work compatible with the cloud.*

## Step 2: Deploy on Streamlit Community Cloud

1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  **Repository**: Select the GitHub repository you just created (`skill-gap-ai`).
4.  **Branch**: Usually `main` or `master`.
5.  **Main file path**: Enter `main.py`.
6.  Click **"Deploy!"**.

## Step 3: Wait for Building

*   Streamlit Cloud will now install the libraries listed in your `requirements.txt`.
*   This might take **3-5 minutes** because it needs to install heavy AI models (`sentence-transformers` and `spacy`).
*   **Success**: Once done, your app will open automatically in a new tab.

## Troubleshooting

*   **"Model not found" error**: If you see an error about `en_core_web_sm`, ensure your `requirements.txt` contains the direct URL link I added (starts with `https://github.com/explosion...`).
*   **Memory Issues**: The free tier has resource limits. The app uses `sentence-transformers`, which is memory intensive. usage is optimized, but if it crashes, it might be due to memory limits. The current optimization updates (lazy loading) should help significantly.

## Your App is Live!
You can now share the URL (e.g., `https://skill-gap-ai.streamlit.app`) with anyone.
