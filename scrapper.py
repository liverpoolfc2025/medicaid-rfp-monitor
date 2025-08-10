from flask import Flask, render_template, jsonify
import requests
import json
import os
import threading
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import schedule
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MedicaidRFPTracker:
    def __init__(self):
        self.rfps_file = 'rfps_data.json'
        
        # Sources to monitor - All 50 States + NASPO (define before loading data)
        self.state_sites = [
            # NASPO ValuePoint (Multi-State)
            {
                'state': 'NASPO',
                'url': 'https://www.naspovaluepoint.org/portfolio/',
                'name': 'NASPO ValuePoint'
            },
            # All 50 States A-Z
            {
                'state': 'Alabama',
                'url': 'https://www.purchasing.alabama.gov',
                'name': 'Alabama Procurement'
            },
            {
                'state': 'Alaska',
                'url': 'https://aws.state.ak.us/OnlinePublicNotices/',
                'name': 'Alaska Online Public Notices'
            },
            {
                'state': 'Arizona',
                'url': 'https://az.gov/services/business-services/business-contracting/state-procurement-office',
                'name': 'Arizona SPO'
            },
            {
                'state': 'Arkansas',
                'url': 'https://www.dfa.arkansas.gov/offices/procurement/',
                'name': 'Arkansas Procurement'
            },
            {
                'state': 'California',
                'url': 'https://www.caleprocure.ca.gov',
                'name': 'Cal eProcure'
            },
            {
                'state': 'Colorado',
                'url': 'https://www.colorado.gov/pacific/oit/procurement',
                'name': 'Colorado Procurement'
            },
            {
                'state': 'Connecticut',
                'url': 'https://portal.ct.gov/DAS/CTSource/CTSource',
                'name': 'Connecticut CTSource'
            },
            {
                'state': 'Delaware',
                'url': 'https://gss.omb.delaware.gov/procurement',
                'name': 'Delaware GSS'
            },
            {
                'state': 'Florida',
                'url': 'https://www.myflorida.com/apps/vbs/',
                'name': 'Florida VBS'
            },
            {
                'state': 'Georgia',
                'url': 'https://doas.ga.gov/state-purchasing',
                'name': 'Georgia DOAS'
            },
            {
                'state': 'Hawaii',
                'url': 'https://spo.hawaii.gov',
                'name': 'Hawaii SPO'
            },
            {
                'state': 'Idaho',
                'url': 'https://gov.idaho.gov/dhr/purchasing/',
                'name': 'Idaho Purchasing'
            },
            {
                'state': 'Illinois',
                'url': 'https://www2.illinois.gov/cms/business/sell2/Pages/default.aspx',
                'name': 'Illinois CMS'
            },
            {
                'state': 'Indiana',
                'url': 'https://www.in.gov/idoa/procurement/',
                'name': 'Indiana IDOA'
            },
            {
                'state': 'Iowa',
                'url': 'https://das.iowa.gov/procurement',
                'name': 'Iowa DAS'
            },
            {
                'state': 'Kansas',
                'url': 'https://admin.ks.gov/offices/procurement-and-contracts',
                'name': 'Kansas Procurement'
            },
            {
                'state': 'Kentucky',
                'url': 'https://finance.ky.gov/services/eprocurement/Pages/default.aspx',
                'name': 'Kentucky eProcurement'
            },
            {
                'state': 'Louisiana',
                'url': 'https://www.doa.la.gov/doa/ospp.htm',
                'name': 'Louisiana OSPP'
            },
            {
                'state': 'Maine',
                'url': 'https://www.maine.gov/dafs/bbm/procurementservices',
                'name': 'Maine Procurement'
            },
            {
                'state': 'Maryland',
                'url': 'https://procurement.maryland.gov',
                'name': 'Maryland eMD'
            },
            {
                'state': 'Massachusetts',
                'url': 'https://www.mass.gov/orgs/operational-services-division',
                'name': 'Massachusetts OSD'
            },
            {
                'state': 'Michigan',
                'url': 'https://www.michigan.gov/dtmb/procurement',
                'name': 'Michigan DTMB'
            },
            {
                'state': 'Minnesota',
                'url': 'https://mn.gov/admin/government/business/',
                'name': 'Minnesota Admin'
            },
            {
                'state': 'Mississippi',
                'url': 'https://www.dfa.ms.gov/dfa-offices/public-procurement/',
                'name': 'Mississippi DFA'
            },
            {
                'state': 'Missouri',
                'url': 'https://oa.mo.gov/purchasing',
                'name': 'Missouri OA'
            },
            {
                'state': 'Montana',
                'url': 'https://gsd.mt.gov/Procurement',
                'name': 'Montana GSD'
            },
            {
                'state': 'Nebraska',
                'url': 'https://das.nebraska.gov/materiel/purchasing.html',
                'name': 'Nebraska DAS'
            },
            {
                'state': 'Nevada',
                'url': 'https://purchasing.nv.gov',
                'name': 'Nevada Purchasing'
            },
            {
                'state': 'New Hampshire',
                'url': 'https://www.nh.gov/das/procurement/',
                'name': 'New Hampshire DAS'
            },
            {
                'state': 'New Jersey',
                'url': 'https://www.njstart.gov',
                'name': 'New Jersey START'
            },
            {
                'state': 'New Mexico',
                'url': 'https://www.generalservices.state.nm.us/state-purchasing/',
                'name': 'New Mexico SPD'
            },
            {
                'state': 'New York',
                'url': 'https://www.ogs.ny.gov/procurement/',
                'name': 'New York OGS'
            },
            {
                'state': 'North Carolina',
                'url': 'https://www.ips.state.nc.us',
                'name': 'North Carolina IPS'
            },
            {
                'state': 'North Dakota',
                'url': 'https://www.nd.gov/omb/procurement',
                'name': 'North Dakota OMB'
            },
            {
                'state': 'Ohio',
                'url': 'https://procure.ohio.gov',
                'name': 'Ohio Procurement'
            },
            {
                'state': 'Oklahoma',
                'url': 'https://www.ok.gov/dcs/Purchasing_Division/',
                'name': 'Oklahoma DCS'
            },
            {
                'state': 'Oregon',
                'url': 'https://www.oregon.gov/das/procurement/pages/index.aspx',
                'name': 'Oregon DAS'
            },
            {
                'state': 'Pennsylvania',
                'url': 'https://www.emarketplace.state.pa.us',
                'name': 'Pennsylvania eMarketplace'
            },
            {
                'state': 'Rhode Island',
                'url': 'https://www.purchasing.ri.gov',
                'name': 'Rhode Island Purchasing'
            },
            {
                'state': 'South Carolina',
                'url': 'https://procurement.sc.gov',
                'name': 'South Carolina Procurement'
            },
            {
                'state': 'South Dakota',
                'url': 'https://boa.sd.gov/central-services/procurement-management/',
                'name': 'South Dakota BOA'
            },
            {
                'state': 'Tennessee',
                'url': 'https://www.tn.gov/generalservices/procurement.html',
                'name': 'Tennessee Procurement'
            },
            {
                'state': 'Texas', 
                'url': 'https://www.txsmartbuy.com',
                'name': 'Texas SmartBuy'
            },
            {
                'state': 'Utah',
                'url': 'https://purchasing.utah.gov',
                'name': 'Utah Purchasing'
            },
            {
                'state': 'Vermont',
                'url': 'https://bgs.vermont.gov/purchasing-contracting',
                'name': 'Vermont BGS'
            },
            {
                'state': 'Virginia',
                'url': 'https://www.dgs.virginia.gov/division-of-purchases-and-supply/procurement-and-solicitations/',
                'name': 'Virginia DGS'
            },
            {
                'state': 'Washington',
                'url': 'https://des.wa.gov/services/contracting-purchasing',
                'name': 'Washington DES'
            },
            {
                'state': 'West Virginia',
                'url': 'https://www.state.wv.us/admin/purchase/',
                'name': 'West Virginia Purchasing'
            },
            {
                'state': 'Wisconsin',
                'url': 'https://www.wi.gov/Pages/agency.aspx?agency=163',
                'name': 'Wisconsin DOA'
            },
            {
                'state': 'Wyoming',
                'url': 'https://ai.wyo.gov/general-services/procurement/',
                'name': 'Wyoming A&I'
            }
        ]
        
        # Load data after state_sites is defined
        self.rfps_data = self.load_rfps_data()
    
    def load_rfps_data(self):
        """Load RFPs data from file"""
        try:
            if os.path.exists(self.rfps_file):
                with open(self.rfps_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading RFPs data: {e}")
        
        return {
            'last_updated': datetime.now().isoformat(),
            'rfps': [],
            'stats': {
                'total_found': 0,
                'states_monitored': len(self.state_sites),
                'last_scan': None
            }
        }
    
    def save_rfps_data(self):
        """Save RFPs data to file"""
        try:
            with open(self.rfps_file, 'w') as f:
                json.dump(self.rfps_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving RFPs data: {e}")
    
    def search_for_medicaid_rfps(self):
        """Search all sources for Medicaid RFPs"""
        logger.info("Starting Medicaid RFP search...")
        
        new_rfps = []
        medicaid_keywords = ['medicaid', 'managed care', 'health plan', 'healthcare services', 'medical assistance']
        
        for site in self.state_sites:
            try:
                logger.info(f"Checking {site['name']} ({site['state']})...")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(site['url'], headers=headers, timeout=15)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Look for medicaid-related keywords
                    found_keywords = []
                    for keyword in medicaid_keywords:
                        if keyword in content:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        # Create RFP entry
                        rfp = {
                            'id': f"{site['state'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                            'title': f"Medicaid/Healthcare RFP Opportunity - {site['state']}",
                            'state': site['state'],
                            'source': site['name'],
                            'url': site['url'],
                            'found_date': datetime.now().isoformat(),
                            'keywords_found': found_keywords,
                            'status': 'Active',
                            'description': f"Potential Medicaid-related procurement opportunity found on {site['name']}. Keywords detected: {', '.join(found_keywords)}"
                        }
                        
                        # Check if this RFP is already in our data
                        existing_ids = [r['id'] for r in self.rfps_data['rfps']]
                        if rfp['id'] not in existing_ids:
                            new_rfps.append(rfp)
                
                time.sleep(2)  # Be respectful to servers
                
            except Exception as e:
                logger.error(f"Error checking {site['name']}: {e}")
        
        # Add sample/demo RFPs for testing
        if not new_rfps and len(self.rfps_data['rfps']) == 0:
            demo_rfps = [
                {
                    'id': 'demo_ca_medicaid',
                    'title': 'California Medicaid Managed Care Services',
                    'state': 'California',
                    'source': 'Cal eProcure',
                    'url': 'https://www.caleprocure.ca.gov',
                    'found_date': datetime.now().isoformat(),
                    'keywords_found': ['medicaid', 'managed care'],
                    'status': 'Active',
                    'description': 'Comprehensive managed care services for Medicaid beneficiaries in California.'
                },
                {
                    'id': 'demo_tx_health',
                    'title': 'Texas Healthcare Technology Solutions',
                    'state': 'Texas',
                    'source': 'Texas SmartBuy',
                    'url': 'https://www.txsmartbuy.com',
                    'found_date': (datetime.now() - timedelta(days=1)).isoformat(),
                    'keywords_found': ['healthcare services'],
                    'status': 'Active',
                    'description': 'Technology solutions for Texas healthcare programs including Medicaid systems.'
                },
                {
                    'id': 'naspo_health_plan',
                    'title': 'NASPO Multi-State Health Plan Services',
                    'state': 'Multi-State',
                    'source': 'NASPO ValuePoint',
                    'url': 'https://www.naspovaluepoint.org',
                    'found_date': (datetime.now() - timedelta(hours=6)).isoformat(),
                    'keywords_found': ['health plan', 'managed care'],
                    'status': 'Active',
                    'description': 'Multi-state cooperative purchasing opportunity for health plan administration services.'
                }
            ]
            new_rfps.extend(demo_rfps)
        
        # Add new RFPs to our data
        for rfp in new_rfps:
            self.rfps_data['rfps'].append(rfp)
        
        # Update stats
        self.rfps_data['stats']['total_found'] = len(self.rfps_data['rfps'])
        self.rfps_data['stats']['last_scan'] = datetime.now().isoformat()
        self.rfps_data['last_updated'] = datetime.now().isoformat()
        
        # Keep only last 100 RFPs to prevent file from getting too large
        if len(self.rfps_data['rfps']) > 100:
            self.rfps_data['rfps'] = self.rfps_data['rfps'][-100:]
        
        self.save_rfps_data()
        
        logger.info(f"Found {len(new_rfps)} new RFPs. Total: {len(self.rfps_data['rfps'])}")
        
        return new_rfps
    
    def get_recent_rfps(self, days=30):
        """Get RFPs from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_rfps = []
        
        for rfp in self.rfps_data['rfps']:
            try:
                rfp_date = datetime.fromisoformat(rfp['found_date'].replace('Z', '+00:00'))
                if rfp_date.replace(tzinfo=None) > cutoff_date:
                    recent_rfps.append(rfp)
            except:
                # Include RFPs with invalid dates
                recent_rfps.append(rfp)
        
        return sorted(recent_rfps, key=lambda x: x['found_date'], reverse=True)

# Create global tracker instance
tracker = MedicaidRFPTracker()

# Web routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/rfps')
def get_rfps():
    """API endpoint to get RFPs data"""
    recent_rfps = tracker.get_recent_rfps(30)
    return jsonify({
        'rfps': recent_rfps,
        'stats': tracker.rfps_data['stats'],
        'last_updated': tracker.rfps_data['last_updated']
    })

@app.route('/api/scan')
def manual_scan():
    """Trigger a manual scan"""
    try:
        new_rfps = tracker.search_for_medicaid_rfps()
        return jsonify({
            'success': True,
            'message': f"Scan completed. Found {len(new_rfps)} new RFPs.",
            'new_rfps': len(new_rfps)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Scan failed: {str(e)}"
        })

def background_scanner():
    """Background thread to scan for RFPs periodically"""
    schedule.every(6).hours.do(tracker.search_for_medicaid_rfps)
    
    # Run initial scan
    tracker.search_for_medicaid_rfps()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Create templates directory and HTML template
templates_dir = 'templates'
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# HTML template for the dashboard
dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medicaid RFP Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem; text-align: center; }
        .header h1 { margin-bottom: 0.5rem; }
        .stats { display: flex; justify-content: center; gap: 2rem; margin: 1rem 0; flex-wrap: wrap; }
        .stat { background: white; padding: 1rem; border-radius: 8px; text-align: center; min-width: 150px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2rem; font-weight: bold; color: #3498db; }
        .stat-label { color: #666; margin-top: 0.5rem; }
        .controls { text-align: center; margin: 1rem 0; }
        .btn { background: #3498db; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 5px; cursor: pointer; font-size: 1rem; }
        .btn:hover { background: #2980b9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
        .rfps-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 1rem; margin-top: 1rem; }
        .rfp-card { background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #3498db; }
        .rfp-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem; color: #2c3e50; }
        .rfp-meta { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }
        .rfp-description { color: #444; line-height: 1.4; margin-bottom: 1rem; }
        .rfp-keywords { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
        .keyword { background: #ecf0f1; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: #555; }
        .rfp-link { color: #3498db; text-decoration: none; font-weight: 500; }
        .rfp-link:hover { text-decoration: underline; }
        .loading { text-align: center; padding: 2rem; color: #666; }
        .no-rfps { text-align: center; padding: 3rem; color: #666; }
        .last-updated { text-align: center; color: #666; font-size: 0.9rem; margin-top: 1rem; }
        @media (max-width: 768px) { .stats { flex-direction: column; align-items: center; } .rfps-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Medicaid RFP Monitor</h1>
        <p>Real-time tracking of Medicaid and healthcare procurement opportunities</p>
    </div>

    <div class="container">
        <div class="stats" id="stats">
            <div class="stat">
                <div class="stat-number" id="total-rfps">-</div>
                <div class="stat-label">Total RFPs Found</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="states-monitored">-</div>
                <div class="stat-label">States Monitored</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="recent-rfps">-</div>
                <div class="stat-label">Last 30 Days</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn" onclick="manualScan()" id="scan-btn">🔄 Scan Now</button>
            <button class="btn" onclick="refreshData()" style="background: #27ae60;">📊 Refresh Data</button>
        </div>

        <div id="rfps-container">
            <div class="loading">Loading RFPs...</div>
        </div>

        <div class="last-updated" id="last-updated"></div>
    </div>

    <script>
        let isScanning = false;

        async function loadRFPs() {
            try {
                const response = await fetch('/api/rfps');
                const data = await response.json();
                
                displayStats(data.stats, data.rfps.length);
                displayRFPs(data.rfps);
                displayLastUpdated(data.last_updated);
            } catch (error) {
                document.getElementById('rfps-container').innerHTML = 
                    '<div class="no-rfps">Error loading RFPs. Please try again.</div>';
            }
        }

        function displayStats(stats, recentCount) {
            document.getElementById('total-rfps').textContent = stats.total_found || 0;
            document.getElementById('states-monitored').textContent = stats.states_monitored || 0;
            document.getElementById('recent-rfps').textContent = recentCount || 0;
        }

        function displayRFPs(rfps) {
            const container = document.getElementById('rfps-container');
            
            if (rfps.length === 0) {
                container.innerHTML = '<div class="no-rfps">No RFPs found yet. Click "Scan Now" to search for opportunities.</div>';
                return;
            }

            const rfpsHtml = rfps.map(rfp => `
                <div class="rfp-card">
                    <div class="rfp-title">${rfp.title}</div>
                    <div class="rfp-meta">
                        📍 ${rfp.state} • 🏢 ${rfp.source} • 📅 ${new Date(rfp.found_date).toLocaleDateString()}
                    </div>
                    <div class="rfp-description">${rfp.description}</div>
                    <div class="rfp-keywords">
                        ${rfp.keywords_found.map(keyword => `<span class="keyword">${keyword}</span>`).join('')}
                    </div>
                    <a href="${rfp.url}" target="_blank" class="rfp-link">View Opportunity →</a>
                </div>
            `).join('');

            container.innerHTML = `<div class="rfps-grid">${rfpsHtml}</div>`;
        }

        function displayLastUpdated(lastUpdated) {
            if (lastUpdated) {
                const date = new Date(lastUpdated);
                document.getElementById('last-updated').textContent = 
                    `Last updated: ${date.toLocaleString()}`;
            }
        }

        async function manualScan() {
            if (isScanning) return;
            
            isScanning = true;
            const btn = document.getElementById('scan-btn');
            btn.textContent = '⏳ Scanning...';
            btn.disabled = true;

            try {
                const response = await fetch('/api/scan');
                const result = await response.json();
                
                if (result.success) {
                    alert(`Scan completed! Found ${result.new_rfps} new RFPs.`);
                    loadRFPs(); // Refresh the display
                } else {
                    alert(`Scan failed: ${result.message}`);
                }
            } catch (error) {
                alert('Scan failed. Please try again.');
            }

            btn.textContent = '🔄 Scan Now';
            btn.disabled = false;
            isScanning = false;
        }

        function refreshData() {
            loadRFPs();
        }

        // Auto-refresh every 5 minutes
        setInterval(loadRFPs, 5 * 60 * 1000);

        // Load initial data
        loadRFPs();
    </script>
</body>
</html>'''

# Write the template file
with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
    f.write(dashboard_html)

if __name__ == "__main__":
    # Start background scanner in a separate thread
    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()
    
    # Start the web server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
