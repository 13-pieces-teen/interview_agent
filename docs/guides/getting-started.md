# 🚀 Getting Started with Interview Agent

Welcome! This guide will get you up and running in **5 minutes**.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **npm** installed (`npm --version`)
- [ ] **uv** installed (`pip install uv` or check uv docs)
- [ ] **SiliconFlow API key** (sign up at https://siliconflow.cn/)

---

## ⚡ 5-Minute Quick Start

### Step 1: Install Dependencies (2 mins)

```bash
# Backend dependencies
uv sync

# Frontend dependencies  
cd frontend
npm install
cd ..
```

### Step 2: Configure API Key (30 seconds)

```bash
# Copy example file
cp .env.example .env

# Edit and add your API key
# Windows: notepad .env
# Mac/Linux: nano .env
```

Add this line:
```
SILICONFLOW_API_KEY=your_actual_key_here
```

### Step 3: Start Application (30 seconds)

```bash
# Windows
start_dev.bat

# Mac/Linux
chmod +x start_dev.sh
./start_dev.sh
```

### Step 4: Open Browser (10 seconds)

Navigate to: **http://localhost:5173**

🎉 **You're ready to go!**

---

## 🎯 First Steps

### Try Text Processing

1. Click **"Text Input"** tab
2. Paste this example:
   ```
   公司：字节跳动
   职位：Python后端工程师
   阶段：一面

   问题1：讲一下Python的GIL
   答：全局解释器锁，用于保护多线程访问...

   问题2：Redis和MySQL的区别
   答：Redis是内存数据库，MySQL是关系型数据库...
   ```
3. Click **"Process Interview Experience"**
4. View results and download exports!

### Try Image Processing

1. Take a screenshot of interview questions
2. Click **"Image Upload"** tab
3. Drag and drop your screenshot
4. Wait for OCR and processing
5. View extracted and structured data!

---

## 📚 Next Steps

Now that you're running, explore:

1. **[README.md](README.md)** - Full project overview
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands
3. **[API Docs](http://localhost:8000/docs)** - Interactive API testing
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - How it all works

---

## 🆘 Need Help?

### Common Issues

**"Port already in use"**
- Kill the process using that port (see QUICK_REFERENCE.md)

**"Module not found"**
- Reinstall dependencies: `uv sync && cd frontend && npm install`

**"API key error"**
- Check `.env` file has correct key
- Restart the backend server

**"Can't connect to backend"**
- Ensure backend is running on port 8000
- Check http://localhost:8000/health

### Get Support

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed troubleshooting
- Check terminal output for error messages
- Review API logs in backend terminal

---

## 💡 Pro Tips

- Use **F12** in browser to see console logs
- Visit **/docs** endpoint to test API directly
- Both servers support **hot reload** - changes appear instantly!
- Generated files are saved to `output/` directory

---

**Happy interviewing! 🎉**
