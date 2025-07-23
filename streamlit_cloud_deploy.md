# Deploy to Streamlit Cloud

## Quick Steps:

1. **Visit**: https://streamlit.io/cloud
2. **Sign in** with your GitHub account
3. **New App** → Connect repository: `ishabanya/llm_benchmark_dashboard`
4. **Configure**:
   - Main file path: `web_ui/app.py`
   - Python version: 3.10
   - Advanced settings → Environment variables:
     ```
     PYTHONPATH = src
     ```
5. **Deploy** - Your app will be live at: `https://[app-name].streamlit.app`

## Benefits:
- ✅ Free hosting for public repos
- ✅ Automatic HTTPS
- ✅ Built for Streamlit
- ✅ Easy updates from GitHub
- ✅ No server management needed 