Medicaid RFP Monitor - Public Web Dashboard
A public web dashboard that automatically tracks and displays Medicaid RFPs from multiple states and NASPO. Anyone with the URL can view current opportunities.

🌐 What You Get
Public web dashboard accessible to anyone with the URL
Real-time RFP tracking from 10+ states plus NASPO
Automatic scanning every 6 hours
Clean, mobile-friendly interface
No login required - completely open access
🚀 Quick Deploy Guide (5 minutes)
Option 1: Railway (Recommended)
Sign up at railway.app
Create a new project from GitHub
Upload these files to your GitHub repo
Railway will automatically detect and deploy
Your dashboard will be live at: yourapp.railway.app
Option 2: Render
Sign up at render.com
Connect your GitHub repository
Choose "Web Service"
Use these settings:
Build Command: pip install -r requirements.txt
Start Command: gunicorn medicaid_rfp_monitor:app
Option 3: Heroku
Sign up at heroku.com
Create new app from GitHub
The Procfile will handle deployment automatically
📊 Dashboard Features
Live Stats Display
Total RFPs found
States monitored (10+)
Recent opportunities (last 30 days)
RFP Cards Show:
Title & State
Source website
Date found
Keywords detected (medicaid, managed care, etc.)
Direct link to opportunity
Interactive Features
"Scan Now" button for immediate search
Auto-refresh every 5 minutes
Mobile responsive design
Real-time updates as new RFPs are found
🎯 What It Monitors
States Covered:
California (Cal eProcure)
Texas (SmartBuy)
New York (OGS)
Florida (VBS)
Illinois, Pennsylvania, Ohio
Georgia, North Carolina, Michigan
Keywords Searched:
"medicaid"
"managed care"
"health plan"
"healthcare services"
"medical assistance"
💰 Hosting Costs
Railway: Free tier (500 hours/month)
Render: Free tier available
Heroku: $5-7/month basic plan
Domain: Optional (~$12/year)
🔧 How It Works
Background scanner runs every 6 hours
Searches state procurement sites for Medicaid keywords
Stores new opportunities in JSON file
Web dashboard displays results in real-time
Anyone can access via the public URL
📱 Mobile Friendly
The dashboard works perfectly on:

Desktop computers
Tablets
Mobile phones
All modern browsers
🚀 Going Live Steps
Upload files to GitHub (all 5 files I created)
Deploy to Railway/Render (connects automatically)
Share the URL with anyone who needs access
RFPs appear automatically as they're found
🔄 Monitoring & Updates
Automatic scanning every 6 hours
Data persists between app restarts
Logs available in hosting platform dashboard
Manual scan button for immediate updates
🎨 Customization Options
Want to modify it? Easy changes:

Add more states in the state_sites list
Change keywords in medicaid_keywords
Adjust scan frequency in the schedule
Modify the design in the HTML template
📈 Usage Analytics
Most hosting platforms provide:

Visitor counts
Traffic analytics
Performance monitoring
Uptime tracking
Perfect for sharing with:

Business development teams
Procurement professionals
Healthcare consultants
Government contractors
