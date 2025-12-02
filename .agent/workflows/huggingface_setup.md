---
description: How to get a Hugging Face API Key
---

1.  **Go to Hugging Face**: Open [huggingface.co](https://huggingface.co/) in your browser.
2.  **Sign Up / Log In**: If you don't have an account, create one. Otherwise, log in.
3.  **Go to Settings**: Click on your profile picture in the top right corner and select **Settings**.
4.  **Access Tokens**: In the left sidebar, click on **Access Tokens**.
5.  **Create New Token**:
    -   Click the **Create new token** button.
    -   Give it a name (e.g., "Personal AI").
    -   Select **Read** permissions (this is sufficient for using inference models).
    -   Click **Create token**.
6.  **Copy Token**: Click the copy icon next to your new token starting with `hf_`.
7.  **Configure Environment**:
    -   Open your backend `.env` file.
    -   Add or update the line: `HUGGINGFACE_API_KEY=your_copied_token_here`
