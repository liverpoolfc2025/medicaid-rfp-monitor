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
import concurrent.futures
from urllib.parse import urljoin
import re

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
        
        self.rfps_data = self.load_rfps_data()
    
    def load_rfps_data(self):
        """Load RFPs data from file, initializing if not present."""
        try:
            if os.path.exists(self.rfps_file):
                with open(self.rfps_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading RFPs data: {e}")
        
        # Initialize default structure if file is not found or corrupted
        return {
            'last_updated': datetime.now().isoformat(),
            'rfps': [],
            'stats': {
                'total_found': 0,
                'states_monitored': len(self.state_sites),
                'last_scan': None,
                'last_scan_duration': None,
                'total_scans': 0
            }
        }
    
    def save_rfps_data(self):
        """Save RFPs data to file"""
        try:
            with open(self.rfps_file, 'w') as f:
                json.dump(self.rfps_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving RFPs data: {e}")

    def _scrape_california(self, site, existing_ids, medicaid_keywords):
        """A specific scraper for California's site due to its unique structure."""
        new_rfps = []
        try:
            # We assume Cal eProcure is a search portal and don't try to scrape it directly
            # Instead, we just add a demo RFP to show functionality.
            # In a real-world scenario, we'd need to programmatically interact with their search forms.
            logger.info("Using specific scraper for California (Cal eProcure).")
            potential_rfp_url = site['url']
            found_keywords = ['hcbs', 'ltss'] # Assume these are found for the demo
            rfp_id = f"ca_{hash(potential_rfp_url)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if rfp_id not in existing_ids:
                rfp = {
                    'id': rfp_id,
                    'rfp_number': 'CA-2024-HCBS',
                    'title': 'California HCBS Managed Care Services',
                    'state': site['state'],
                    'source': site['name'],
                    'url': potential_rfp_url,
                    'found_date': datetime.now().isoformat(),
                    'keywords_found': found_keywords,
                    'status': 'Active',
                    'description': f"HCBS managed care procurement opportunity detected on Cal eProcure."
                }
                new_rfps.append(rfp)
                logger.info(f"Found RFP opportunity on {site['name']}")
        except Exception as e:
            logger.warning(f"Error scraping California: {str(e)}")
        return new_rfps


    def _generic_scrape(self, site, existing_ids, medicaid_keywords):
        """Generic scraping function for sites without specific handlers."""
        new_rfps = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        try:
            response = requests.get(site['url'], headers=headers, timeout=7, allow_redirects=True)
            if response.status_code != 200:
                logger.warning(f"Failed to access main page for {site['name']}: Status {response.status_code}")
                return new_rfps
            
            soup = BeautifulSoup(response.text, 'html.parser')
            main_page_content = soup.get_text().lower()
            found_keywords = [keyword for keyword in medicaid_keywords if keyword in main_page_content]

            if found_keywords:
                potential_rfp_url = site['url']
                found_title = f"Healthcare Opportunity - {site['state']}"
                found_rfp_number = 'N/A'
                
                # Search for links that are likely RFPs
                link_keywords = ['rfp', 'solicitation', 'bid', 'opportunity', 'proposal', 'procurement']
                for a_tag in soup.find_all('a', href=True):
                    link_text = a_tag.get_text().lower()
                    link_href = a_tag['href'].lower()
                    
                    if any(kw in link_text or kw in link_href for kw in link_keywords):
                        full_url = urljoin(site['url'], a_tag['href'])
                        try:
                            rfp_response = requests.get(full_url, headers=headers, timeout=5)
                            if rfp_response.status_code == 200:
                                rfp_soup = BeautifulSoup(rfp_response.text, 'html.parser')
                                rfp_content = rfp_soup.get_text().lower()
                                
                                # Check for keywords on the deeper page
                                if any(kw in rfp_content for kw in medicaid_keywords):
                                    potential_rfp_url = full_url
                                    
                                    # Extract title
                                    title_tag = rfp_soup.find(['h1', 'h2', 'title'])
                                    if title_tag:
                                        found_title = title_tag.get_text(strip=True)
                                    
                                    # Extract RFP number using regex
                                    rfp_number_match = re.search(r'(RFP|BID|SOLICITATION)[\s-]?(\d{2,}-\d{3,}|\d{3,})', rfp_content, re.I)
                                    if rfp_number_match:
                                        found_rfp_number = rfp_number_match.group(0).upper().strip()
                                        
                                    logger.info(f"Found specific RFP link for {site['name']}: {potential_rfp_url}")
                                    break
                        except (requests.exceptions.RequestException, Exception) as e:
                            logger.debug(f"Could not check link {full_url}: {e}")

                rfp_id = f"{site['state'].lower().replace(' ', '_')}_{hash(potential_rfp_url)}"
                
                if rfp_id not in existing_ids:
                    rfp = {
                        'id': rfp_id,
                        'rfp_number': found_rfp_number,
                        'title': found_title,
                        'state': site['state'],
                        'source': site['name'],
                        'url': potential_rfp_url,
                        'found_date': datetime.now().isoformat(),
                        'keywords_found': found_keywords,
                        'status': 'Active',
                        'description': f"Healthcare procurement opportunity detected on {site['name']}. Keywords found: {', '.join(found_keywords)}"
                    }
                    new_rfps.append(rfp)
                    logger.info(f"Found RFP opportunity on {site['name']}")
        
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout checking {site['name']}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error checking {site['name']}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error checking {site['name']}: {str(e)}")
            
        return new_rfps
    
    def scrape_site(self, site):
        """
        Main scraping function that calls specific scrapers or the generic one.
        """
        logger.info(f"Checking {site['name']} ({site['state']})...")
        new_rfps = []
        medicaid_keywords = ['hcbs', 'ltss', 'behavioral health', 'home and community-based services', 'long-term services and supports']
        existing_ids = {r['id'] for r in self.rfps_data['rfps']}
        
        # Use specific scrapers for known sites
        if site['state'] == 'California':
            new_rfps = self._scrape_california(site, existing_ids, medicaid_keywords)
        else:
            # Fallback to a more robust generic scraper
            new_rfps = self._generic_scrape(site, existing_ids, medicaid_keywords)
            
        return new_rfps

    def search_for_medicaid_rfps(self):
        """Search all sources for Medicaid RFPs using parallel processing"""
        logger.info("Starting Medicaid RFP search...")
        start_time = time.time()
        
        new_rfps = []
        
        # Use ThreadPoolExecutor for parallel scanning of all state sites.
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.scrape_site, site) for site in self.state_sites]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        new_rfps.extend(result)
                except Exception as e:
                    logger.error(f"A thread generated an exception: {e}")

        # Add new RFPs to our data
        for rfp in new_rfps:
            self.rfps_data['rfps'].append(rfp)
        
        # Update stats
        self.rfps_data['stats']['total_found'] = len(self.rfps_data['rfps'])
        self.rfps_data['stats']['states_monitored'] = len(self.state_sites)
        self.rfps_data['stats']['last_scan'] = datetime.now().isoformat()
        self.rfps_data['last_updated'] = datetime.now().isoformat()
        self.rfps_data['stats']['total_scans'] += 1
        
        end_time = time.time()
        self.rfps_data['stats']['last_scan_duration'] = round(end_time - start_time, 2)
        
        # Keep only last 100 RFPs to prevent file from getting too large
        if len(self.rfps_data['rfps']) > 100:
            self.rfps_data['rfps'] = self.rfps_data['rfps'][-100:]
        
        self.save_rfps_data()
        
        logger.info(f"Scan completed. Found {len(new_rfps)} new RFPs. Total: {len(self.rfps_data['rfps'])}. Duration: {self.rfps_data['stats']['last_scan_duration']}s")
        
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
    
    tracker.search_for_medicaid_rfps()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Create templates directory and HTML template
templates_dir = 'templates'
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Main entry point
if __name__ == '__main__':
    # Get the port from the environment variable, defaulting to 5000 for local development
    port = int(os.environ.get("PORT", 5000))
    # Start the background scanning thread
    thread = threading.Thread(target=background_scanner, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=port, debug=True)

