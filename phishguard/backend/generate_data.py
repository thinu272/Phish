"""Synthetic phishing dataset generator for the PhishGuard dashboard.

Writes 9 CSV tables into ./data (dimension + fact tables).
Run:  python generate_data.py [seed] [n_emails]
"""
import numpy as np, pandas as pd, os, math, random, sys
from pathlib import Path
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 2026   # usage: python generate_data.py [seed] [n_emails]
rng = np.random.default_rng(SEED)
NOW = pd.Timestamp('2026-11-18 16:00:00'); START = pd.Timestamp('2026-01-01')
days = pd.date_range(START, NOW.normalize()); ND = len(days)
OUT = str(Path(__file__).resolve().parent / 'data'); os.makedirs(OUT, exist_ok=True)
def norm(a): a = np.array(a, float); return a/a.sum()
def pick(opts, p=None):
    return opts[rng.choice(len(opts), p=None if p is None else norm(p))]
def ln(median, sigma): return float(rng.lognormal(math.log(median), sigma))

# ---------------- departments & users ----------------
DEPTS = {  # headcount, target weight, click weight, report weight
 'IT & Security':(70,.9,.45,1.5),'Finance':(55,1.9,1.0,1.0),'Human Resources':(30,1.5,1.1,.95),
 'Sales':(100,1.2,1.4,.7),'Marketing':(45,1.0,1.2,.8),'Operations':(110,.8,1.3,.75),
 'Legal & Compliance':(18,1.1,.6,1.2),'Customer Support':(85,1.0,1.35,.8),'Executive Office':(14,2.5,.9,.7),
 'Procurement':(28,1.6,1.0,.95),'Research & Development':(65,.9,.7,1.0)}
TITLES = {'IT & Security':['Systems Administrator','Network Engineer','Security Analyst','Help Desk Technician'],
 'Finance':['Accountant','Accounts Payable Clerk','Financial Analyst','Payroll Specialist'],
 'Human Resources':['HR Coordinator','Recruiter','Benefits Specialist','HR Generalist'],
 'Sales':['Account Executive','Sales Representative','Sales Engineer','Business Development Rep'],
 'Marketing':['Content Specialist','Marketing Analyst','Campaign Manager','Designer'],
 'Operations':['Operations Coordinator','Logistics Planner','Process Analyst','Facilities Lead'],
 'Legal & Compliance':['Paralegal','Compliance Analyst','Contracts Specialist','Counsel'],
 'Customer Support':['Support Agent','Support Specialist','Team Lead','QA Analyst'],
 'Executive Office':['Chief of Staff','Executive Assistant','VP Operations','CFO Office Lead'],
 'Procurement':['Procurement Officer','Buyer','Vendor Manager','Sourcing Analyst'],
 'Research & Development':['Software Engineer','Data Scientist','Research Associate','QA Engineer']}
FIRST = "Aiden Maya Liam Priya Noah Ayesha Ethan Nimal Sophia Kasun Olivia Rohan Lucas Ishara Emma Arjun Mason Dilini Amelia Tharindu Harper Sanjay Logan Chamari Elijah Nadeesha James Fatima Benjamin Anika Henry Ravindu Chloe Omar Grace Kavindu Daniel Sara Jacob Malik Zoe Imran Leah Suresh Ella Marcus Nora Pavan Layla Victor Hannah Dinesh Isla Tobias Mei Carlos Yara Felix Anya Hugo Selin".split()
LAST = "Perera Fernando Silva Jayawardena Smith Johnson Williams Brown Jones Garcia Miller Davis Patel Kumar Singh Nguyen Tan Lim Wong Muller Schmidt Fischer Weber Wilson Taylor Thomas Moore Martin Clark Lewis Walker Hall Allen Young King Wright Scott Green Baker Adams Nelson Hill Campbell Mitchell Roberts Carter Phillips Evans Turner Torres Parker Collins Edwards Stewart Morris Rogers Reed Cook Morgan Bell Murphy Bailey".split()
LOCS = [('Colombo','Sri Lanka'),('Chicago','United States'),('London','United Kingdom'),('Singapore','Singapore'),('Frankfurt','Germany'),('Sydney','Australia'),('Toronto','Canada')]
LOCP = [.28,.24,.14,.10,.10,.07,.07]
SEN = ['Associate','Specialist','Manager','Director','Executive']; SENP=[.52,.26,.15,.05,.02]; SENW={'Associate':1,'Specialist':1,'Manager':1.5,'Director':2.1,'Executive':3}
users=[]; seen=set(); uid=0
dept_rows=[]
for di,(d,(hc,tw,cw,rw)) in enumerate(DEPTS.items(),1):
    dept_rows.append(dict(department_id=f'D{di:02d}',department_name=d,headcount=hc))
    for _ in range(hc):
        uid+=1
        while True:
            f,l=pick(FIRST),pick(LAST); em=f'{f}.{l}'.lower()
            if em in seen: em=f'{em}{rng.integers(2,99)}'
            if em not in seen: seen.add(em); break
        sen = 'Executive' if d=='Executive Office' and rng.random()<.5 else pick(SEN,SENP)
        loc = LOCS[rng.choice(len(LOCS),p=LOCP)]
        users.append(dict(user_id=f'U{uid:04d}',full_name=f'{f} {l}',email=f'{em}@acmecorp.example',department=d,
            department_id=f'D{di:02d}',job_title=pick(TITLES[d]),seniority=sen,office_city=loc[0],office_country=loc[1],
            hire_date=(pd.Timestamp('2026-01-01')-pd.Timedelta(days=int(rng.integers(30,3650)))).normalize(),
            _tw=tw*SENW[sen]*float(rng.lognormal(0,.7)),
            _cp=float(np.clip(cw*rng.beta(1.5,9),.005,.7)),_rp=float(np.clip(rw*rng.beta(4,5),.03,.95))))
U = pd.DataFrame(users); nU=len(U)
tw_all = norm(U._tw.values)

# ---------------- attack taxonomy ----------------
TYPES=['Credential Harvesting','Business Email Compromise','Invoice / Payment Fraud','Malware Attachment','Spear Phishing','Whaling (Executive Impersonation)','Quishing (QR Code)','Callback / Support Scam','HR / Payroll Scam','File-Sharing Lure','Delivery / Package Scam']
TYPE_P=[.20,.10,.12,.10,.08,.04,.08,.05,.07,.10,.06]
OPP_P=[.26,.08,.16,.09,.06,.02,.07,.05,.06,.09,.06]
SUBJ={TYPES[0]:["Action Required: Verify your account","Your password expires today","Unusual sign-in activity detected","Mailbox storage full - upgrade now","Security alert: new device login","Re-validate your Microsoft 365 account"],
 TYPES[1]:["Quick task for you","Are you available?","Updated wire instructions","Confidential - need your help today","Vendor bank details changed"],
 TYPES[2]:["Invoice overdue - immediate payment required","Payment confirmation","Remittance advice attached","Past due statement","Purchase order for review"],
 TYPES[3]:["Shipping document - please review","Scanned document from printer","Resume - Application for Open Position","Expense report Q3","Voicemail message attached"],
 TYPES[4]:["Re: Contract revisions for your review","Follow-up on yesterday's meeting","Updated project timeline","Your performance review document"],
 TYPES[5]:["Board meeting - confidential materials","Urgent request from the CEO","Acquisition due diligence documents"],
 TYPES[6]:["Scan to re-enroll in MFA","Benefits enrollment - scan QR code","Parking permit renewal - scan QR"],
 TYPES[7]:["Your subscription has been renewed","Order confirmation - call to cancel","Antivirus renewal receipt"],
 TYPES[8]:["Payroll update required","Open enrollment - benefits update","Salary adjustment letter","Direct deposit change confirmation"],
 TYPES[9]:["A document was shared with you","Files shared via OneDrive","Please review the shared folder","Signature requested on document"],
 TYPES[10]:["Package delivery failed - action needed","Customs fee required for your parcel","Reschedule your delivery"]}
TCAT={TYPES[0]:[('Credential Theft',.85),('Data Exfiltration',.15)],TYPES[1]:[('Financial Fraud',.85),('Impersonation / Social Engineering',.15)],
 TYPES[2]:[('Financial Fraud',.9),('Malware Delivery',.1)],TYPES[3]:[('Malware Delivery',.8),('Ransomware Precursor',.2)],
 TYPES[4]:[('Impersonation / Social Engineering',.5),('Data Exfiltration',.3),('Credential Theft',.2)],
 TYPES[5]:[('Impersonation / Social Engineering',.6),('Financial Fraud',.4)],TYPES[6]:[('Credential Theft',.9),('Malware Delivery',.1)],
 TYPES[7]:[('Financial Fraud',.6),('Impersonation / Social Engineering',.4)],TYPES[8]:[('Credential Theft',.55),('Financial Fraud',.45)],
 TYPES[9]:[('Credential Theft',.8),('Data Exfiltration',.2)],TYPES[10]:[('Financial Fraud',.5),('Credential Theft',.5)]}
SEV=['Low','Medium','High','Critical']
SEVP={TYPES[0]:[.20,.45,.30,.05],TYPES[1]:[.05,.30,.45,.20],TYPES[2]:[.15,.40,.35,.10],TYPES[3]:[.10,.30,.40,.20],TYPES[4]:[.12,.38,.38,.12],
 TYPES[5]:[.02,.13,.45,.40],TYPES[6]:[.20,.45,.30,.05],TYPES[7]:[.30,.47,.20,.03],TYPES[8]:[.20,.50,.26,.04],TYPES[9]:[.25,.50,.22,.03],TYPES[10]:[.50,.40,.09,.01]}
DET={TYPES[0]:.93,TYPES[1]:.80,TYPES[2]:.90,TYPES[3]:.96,TYPES[4]:.83,TYPES[5]:.76,TYPES[6]:.78,TYPES[7]:.75,TYPES[8]:.88,TYPES[9]:.87,TYPES[10]:.94}
URLP={TYPES[0]:.97,TYPES[1]:0,TYPES[2]:.5,TYPES[3]:.15,TYPES[4]:.6,TYPES[5]:.08,TYPES[6]:.95,TYPES[7]:0,TYPES[8]:.8,TYPES[9]:.98,TYPES[10]:.95}
CLICKF={TYPES[0]:1.1,TYPES[1]:.4,TYPES[2]:1.0,TYPES[3]:1.0,TYPES[4]:1.5,TYPES[5]:.8,TYPES[6]:1.2,TYPES[7]:.5,TYPES[8]:1.3,TYPES[9]:1.4,TYPES[10]:.9}
SUBP={TYPES[0]:.40,TYPES[2]:.15,TYPES[4]:.30,TYPES[6]:.45,TYPES[8]:.35,TYPES[9]:.40,TYPES[10]:.15,TYPES[5]:.1}
REPLY={TYPES[1],TYPES[5],TYPES[7],TYPES[4]}
ATT={TYPES[0]:[('None',.85),('HTML',.15)],TYPES[1]:[('None',1)],TYPES[2]:[('PDF',.5),('XLSX',.15),('HTML',.15),('DOCX',.2)],
 TYPES[3]:[('PDF',.2),('DOCM',.15),('XLSM',.15),('ZIP',.2),('ISO',.08),('HTML',.07),('LNK',.07),('RAR',.08)],
 TYPES[4]:[('None',.45),('DOCX',.25),('PDF',.3)],TYPES[5]:[('None',.8),('PDF',.2)],TYPES[6]:[('PNG',.6),('JPG',.2),('PDF',.2)],
 TYPES[7]:[('PDF',.9),('None',.1)],TYPES[8]:[('PDF',.4),('None',.6)],TYPES[9]:[('None',.9),('HTML',.1)],TYPES[10]:[('None',.8),('PDF',.2)]}
SENDER_LOCAL={TYPES[0]:['security-team','no-reply','account-services','it-helpdesk'],TYPES[1]:['jessica.moore','mark.hamilton','daniel.reid','office.admin'],
 TYPES[2]:['accounts-payable','billing','invoices','finance-dept'],TYPES[3]:['scanner','documents','hr-recruiting','voicemail'],
 TYPES[4]:['project.lead','partner.relations','m.collins','contracts'],TYPES[5]:['ceo.office','chairman.office','exec.assistant'],
 TYPES[6]:['mfa-enroll','benefits','facilities','security-team'],TYPES[7]:['support','orders','renewals','billing'],
 TYPES[8]:['payroll','hr-benefits','hr-department','compensation'],TYPES[9]:['file-share','docs','notifications','sharepoint-noreply'],
 TYPES[10]:['tracking','delivery-notice','shipping','customer-care']}
COUNTRIES=['United States','Nigeria','Russia','China','India','Brazil','Romania','Vietnam','Ukraine','Netherlands','Germany','United Kingdom','Indonesia','Turkey','Unknown (Anonymized)']
COUNTRYP=norm([18,12,11,10,8,6,5,4,3,4,3,3,3,3,7])
DOMAIN_FREE=[('gmail.com','Gmail'),('outlook.com','Outlook.com'),('yahoo.com','Yahoo Mail'),('protonmail.com','ProtonMail'),('zoho.com','Zoho Mail')]
FREEP=norm([.42,.28,.14,.10,.06]); FREE_TYPES={TYPES[1],TYPES[5],TYPES[4],TYPES[7]}

# ---------------- domain pool ----------------
BR="microsoft office365 docusign paypal dhl fedex linkedin dropbox adobe zoom okta workday amazon apple google wetransfer onedrive sharepoint chase ups netflix slack salesforce quickbooks indeed adp coinbase".split()
SUF=["-secure","-login","-support","-verify","-alerts","-portal","-billing","-hr","-docs","-mail","-service","-update",""]
TLD=['.com','.net','.xyz','.top','.info','.online','.site','.click','.co','.support','.ink']; TLDP=norm([22,10,14,10,8,8,6,6,6,5,5])
WORDS="secure portal verify cloud docs mail pay billing track support account login safe center online service access desk".split()
CO=["brightpath","northgate","harborview","summit","redwood","oakline","bluepeak","maplewood","ironbridge","silverline","clearwater","stonegate","pinecrest","westbrook","lakeshore"]
CO2=["logistics","dental","realty","tools","catering","furniture","consulting","printing","travel","fitness","supplies","design"]
leet={'o':'0','l':'1','i':'1','a':'4','e':'3'}
used=set(); pool=[]
def lk():
    b=pick(BR); 
    if rng.random()<.6:
        k=rng.integers(0,len(b)); 
        while b[k] not in leet: k=rng.integers(0,len(b))
        b=b[:k]+leet[b[k]]+b[k+1:]
    return b+pick(SUF)+pick(TLD,TLDP)
def nrd(): return f"{pick(WORDS)}-{pick(WORDS)}-{rng.integers(100,9999)}"+pick(TLD,TLDP)
def comp(): return f"{pick(CO)}-{pick(CO2)}"+pick(['.com','.org','.net'])
for kind,fn,n,agef in [('Lookalike Domain',lk,60,(5,180)),('Newly Registered Domain',nrd,50,(1,30)),('Compromised Legitimate Domain',comp,30,(800,4000))]:
    c=0
    while c<n:
        d=fn()
        if d in used: continue
        used.add(d); c+=1
        prov = 'Compromised Mail Account' if kind.startswith('Comp') else pick(['Custom SMTP Server','Microsoft 365 (Attacker Tenant)','Google Workspace (Attacker Tenant)','Bulk Mailer Abuse'],[.35,.25,.2,.2])
        pool.append(dict(domain=d,type=kind,provider=prov,age=int(rng.integers(*agef)),country=COUNTRIES[rng.choice(len(COUNTRIES),p=COUNTRYP)]))
for d,p in DOMAIN_FREE: pool.append(dict(domain=d,type='Free Webmail',provider=p,age=int(rng.integers(5000,9000)),country=None))
custom=[p for p in pool if p['type']!='Free Webmail']; free=[p for p in pool if p['type']=='Free Webmail']
order=rng.permutation(len(custom)); zipf=norm([1/(r+2)**.9 for r in range(len(custom))]); cust_p=np.zeros(len(custom)); cust_p[order]=zipf
LAND=[f"{pick(WORDS)}{pick(['-app','-form','-files','-cdn'])}{rng.integers(10,999)}"+pick(['.com','.net','.xyz','.site']) for _ in range(40)]
PATH=['login','verify','auth','secure','document','view','invoice','track','signin','update','confirm']
def mkurl(host): return f"hxxps://{host.replace('.','[.]')}/{pick(PATH)}/{''.join(rng.choice(list('abcdef0123456789'),8))}"
def choose_domain(atype):
    if atype in FREE_TYPES and rng.random()<.45: return free[rng.choice(len(free),p=FREEP)]
    return custom[rng.choice(len(custom),p=cust_p)]

# ---------------- campaigns ----------------
ADJ="Crimson Silent Midnight Golden Phantom Rapid Hollow Iron Velvet Azure Ember Shadow Cobalt Amber".split()
THEME={TYPES[0]:'Credential Harvest',TYPES[1]:'Wire Request',TYPES[2]:'Invoice Wave',TYPES[3]:'Dropper Run',TYPES[4]:'Targeted Lure',TYPES[5]:'Boardroom Ruse',TYPES[6]:'QR Swarm',TYPES[7]:'Callback Scam',TYPES[8]:'Payroll Diversion',TYPES[9]:'Share Lure',TYPES[10]:'Parcel Phish'}
FOCUS={TYPES[2]:['Finance','Procurement'],TYPES[1]:['Finance'],TYPES[3]:['Human Resources'],TYPES[5]:['Executive Office'],TYPES[8]:['Human Resources','Finance'],TYPES[7]:['Customer Support','Sales']}
WD=np.array([1.0,1.25,1.3,1.2,.95,.35,.3])
camps=[]; startp=norm([.6+.9*i/ND+(.2 if days[i].month>=10 else 0) for i in range(ND-3)])
for i in range(1,35):
    at=pick(TYPES,TYPE_P); s=days[rng.choice(len(startp),p=startp)]; dur=int(rng.integers(2,13)); e=min(s+pd.Timedelta(days=dur),days[-1])
    cd=pd.date_range(s,e); dp=norm([WD[x.weekday()] for x in cd])
    doms=[]; 
    for _ in range(int(rng.integers(1,5))):
        dm=choose_domain(at)
        if dm not in doms: doms.append(dm)
    hosts=[d['domain'] for d in doms if d['type']!='Free Webmail'] or [pick(LAND)]
    urls=[mkurl(pick(hosts) if rng.random()<.7 else pick(LAND)) for _ in range(int(rng.integers(1,4)))]
    focus=FOCUS.get(at) or ([pick(list(DEPTS))] if rng.random()<.3 else [])
    uw=U._tw.values*np.where(U.department.isin(focus),5,1)
    ctry=[COUNTRIES[rng.choice(len(COUNTRIES),p=COUNTRYP)] for _ in range(int(rng.integers(1,3)))]
    camps.append(dict(campaign_id=f'CMP-{i:03d}',campaign_name=f'{pick(ADJ)} {THEME[at]}',type=at,start=s,end=e,days=cd,day_p=dp,domains=doms,
        dom_p=norm([1/(k+1) for k in range(len(doms))]),urls=urls,focus=focus,user_p=norm(uw),countries=ctry,size=float(rng.lognormal(0,.3)),
        actor=pick(['TA-2201','TA-3317','TA-4108','TA-5560','TA-6092','Unattributed'],[.15,.15,.15,.15,.1,.3])))
OPP=dict(campaign_id='CMP-000',campaign_name='Opportunistic (Unattributed)',type=None)
opp_urls=[mkurl(pick([p['domain'] for p in custom])) for _ in range(50)]
cp=norm([c['size'] for c in camps])
dw=np.array([WD[d.weekday()]*(.75+.6*i/(ND-1))*(1.15 if d.month>=10 else 1) for i,d in enumerate(days)]); daily_p=norm(dw)
HOURP=norm([.5,.4,.4,.5,.6,.8,1.2,2.5,4.5,5.5,5.5,4.5,3.2,4.0,4.8,4.5,3.5,2.5,1.6,1.2,1.0,.8,.7,.6])

# ---------------- phishing emails ----------------
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000; rows=[]
for _ in range(N):
    c = camps[rng.choice(len(camps),p=cp)] if rng.random()<.6 else OPP
    at = c['type'] or pick(TYPES,OPP_P)
    day = days[rng.choice(ND,p=daily_p)] if c is OPP else c['days'][rng.choice(len(c['days']),p=c['day_p'])]
    ts = day+pd.Timedelta(hours=int(rng.choice(24,p=HOURP)),minutes=int(rng.integers(0,60)),seconds=int(rng.integers(0,60)))
    if ts>NOW: ts=NOW-pd.Timedelta(minutes=int(rng.integers(5,600)))
    t=(ts.normalize()-START).days/(ND-1)
    dm = choose_domain(at) if c is OPP else c['domains'][rng.choice(len(c['domains']),p=c['dom_p'])]
    country = (pick(c['countries']) if c is not OPP else COUNTRIES[rng.choice(len(COUNTRIES),p=COUNTRYP)]) if dm['country'] is None else ('Unknown (Anonymized)' if rng.random()<.05 else dm['country'])
    has_url = rng.random()<URLP[at]
    url = None; land=None
    if has_url:
        url = pick(opp_urls) if c is OPP else pick(c['urls']); land=url.split('//')[1].split('/')[0].replace('[.]','.')
    att = pick([a for a,_ in ATT[at]],[p for _,p in ATT[at]])
    uidx = rng.choice(nU,p=tw_all if c is OPP else c['user_p']); u=U.iloc[uidx]
    sev = pick(SEV,SEVP[at]); tc=pick([a for a,_ in TCAT[at]],[p for _,p in TCAT[at]])
    detected = rng.random()<min(.97,DET[at]-.03+.06*t)
    if detected:
        r=rng.random(); action='Blocked' if r<.74 else ('Quarantined' if r<.94 else 'Delivered with Warning')
        method = pick(['Sandbox Detonation'] if at==TYPES[3] else ['Impersonation Protection','ML Classifier'] if at in (TYPES[1],TYPES[5]) else ['QR / Image Analysis','URL Reputation'] if at==TYPES[6] else ['URL Reputation','Sender Reputation','ML Classifier','Signature Match'])
    else: action='Delivered to Inbox'; method='Not Detected'
    delivered = action.startswith('Delivered')
    clicked=opened=replied=sub=rep=0; cts=rts=None
    if delivered:
        m=1.0 if action=='Delivered to Inbox' else .35; tf=1.15-.3*t
        if has_url and rng.random()<min(.9,u._cp*1.5*CLICKF[at]*m*tf): clicked=1
        if att!='None' and rng.random()<min(.9,u._cp*1.6*m*tf): opened=1
        if at in REPLY and rng.random()<min(.9,u._cp*1.8*m): replied=1
        if clicked and rng.random()<SUBP.get(at,0): sub=1
        if rng.random()<min(.95,u._rp*(1 if m==1 else 1.15)*(.55 if sub else 1)*(.9+.3*t)): rep=1
        if clicked: cts=min(ts+pd.Timedelta(minutes=ln(9,1.0)),NOW)
        if rep:
            rts=ts+pd.Timedelta(minutes=ln(35,1.0))
            if cts is not None and rts<=cts: rts=cts+pd.Timedelta(minutes=float(rng.integers(2,60)))
            rts=min(rts,NOW)
    spam = float(np.clip(rng.normal(7.5,1.2) if detected else rng.normal(3.8,1.3), .5,10)) 
    free_d = dm['type']=='Free Webmail'
    auth = lambda: pick(['Pass','Fail','None'],[.95,.03,.02] if free_d else [.55,.30,.15])
    rows.append(dict(received_datetime=ts,campaign_id=c['campaign_id'],sender_email=f"{pick(SENDER_LOCAL[at])}@{dm['domain']}",sender_domain=dm['domain'],
        sender_domain_type=dm['type'],sender_domain_age_days=dm['age'],email_provider=dm['provider'],sender_country=country,subject=pick(SUBJ[at]),
        attack_type=at,threat_category=tc,severity=sev,attachment_type=att,malicious_url=url,url_landing_domain=land,spf_result=auth(),dkim_result=auth(),dmarc_result=auth(),
        spam_score=round(spam,1),target_user_id=u.user_id,department=u.department,detection_status='Detected' if detected else 'Missed',detection_method=method,action_taken=action,
        is_detected=int(detected),is_blocked=int(action in('Blocked','Quarantined')),is_delivered=int(delivered),is_missed=int(not detected),clicked=clicked,
        opened_attachment=opened,replied=replied,submitted_credentials=sub,reported_by_user=rep,click_datetime=cts,report_datetime=rts))
E=pd.DataFrame(rows).sort_values('received_datetime').reset_index(drop=True)
E.insert(0,'email_id',[f'PE-2026-{i+1:06d}' for i in range(len(E))])
E['minutes_to_click']=((E.click_datetime-E.received_datetime).dt.total_seconds()/60).round(1)
E['minutes_to_report']=((E.report_datetime-E.received_datetime).dt.total_seconds()/60).round(1)
rd=E.received_datetime
E.insert(2,'received_date',rd.dt.normalize()); E.insert(3,'year_month',rd.dt.strftime('%Y-%m'))
E.insert(4,'week_start_date',(rd.dt.normalize()-pd.to_timedelta(rd.dt.weekday,unit='D')))
E.insert(5,'iso_week',rd.dt.isocalendar().week.astype(int)); E.insert(6,'day_of_week',rd.dt.day_name()); E.insert(7,'day_of_week_num',rd.dt.weekday+1); E.insert(8,'hour_of_day',rd.dt.hour)

# ---------------- incidents ----------------
TEAMS={'Critical':(['Incident Response Team','SOC Tier 2','Threat Intelligence'],[.55,.30,.15]),'High':(['SOC Tier 2','Incident Response Team','SOC Tier 1','Threat Intelligence'],[.40,.25,.20,.15]),
 'Medium':(['SOC Tier 1','SOC Tier 2','IT Security Operations','Threat Intelligence'],[.45,.25,.20,.10]),'Low':(['SOC Tier 1','IT Security Operations','SOC Tier 2'],[.6,.25,.15])}
ANALYSTS={'SOC Tier 1':['Amal Peiris','Jordan Blake','Reena Das','Colin Ford'],'SOC Tier 2':['Nisha Rao','Peter Lang','Sam Ortega','Ruwan De Silva'],
 'Incident Response Team':['Elena Petrov','Marcus Hale','Tara Quinn'],'Threat Intelligence':['Wei Zhang','Hana Sato','Ivan Kovac'],'IT Security Operations':['Dev Malhotra','Lucy Frost','Kamal Wijesinghe']}
RESP={'Critical':10,'High':22,'Medium':55,'Low':150}; RES={'Critical':5,'High':12,'Medium':24,'Low':48}; SLA={'Critical':8,'High':24,'Medium':48,'Low':96}
REM=['Password Reset','Mailbox Purge','Block Sender Domain','Block Malicious URL','Endpoint Isolation','User Awareness Coaching','Session Revocation']
inc=[]
for r in E.itertuples():
    make=False; src=None; created=None
    if r.is_delivered and (r.reported_by_user or r.clicked or r.submitted_credentials):
        make=True
        if r.reported_by_user: src='Employee Report'; created=r.report_datetime+pd.Timedelta(minutes=float(rng.integers(2,20)))
        else: src='SOC Monitoring'; created=r.click_datetime+pd.Timedelta(minutes=float(rng.integers(30,600)))
    elif r.is_delivered and r.severity in('Critical','High') and rng.random()<.25:
        make=True; src='SOC Threat Hunting'; created=r.received_datetime+pd.Timedelta(hours=float(rng.integers(2,48)))
    elif r.is_blocked and r.severity=='Critical' and rng.random()<.08:
        make=True; src='Email Gateway Alert'; created=r.received_datetime+pd.Timedelta(minutes=float(rng.integers(5,120)))
    if not make: continue
    if created>NOW: created=NOW-pd.Timedelta(minutes=float(rng.integers(5,90)))
    sev=r.severity
    if r.submitted_credentials and sev!='Critical': sev=SEV[SEV.index(sev)+1]
    t=(created.normalize()-START).days/(ND-1); f=1.15-.35*t
    team=pick(*TEAMS[sev]); an=pick(ANALYSTS[team])
    rm=ln(RESP[sev],.6)*f; first=created+pd.Timedelta(minutes=rm)
    rh=ln(RES[sev],.7)*f*(float(rng.uniform(15,80)) if rng.random()<.05 else 1)
    resolved = created+pd.Timedelta(hours=rh)<=NOW
    age_h=(NOW-created).total_seconds()/3600
    if resolved: status='Resolved'; inv=pick(['Closed - Confirmed Phishing','Closed - Remediated'],[.55,.45]); res_dt=created+pd.Timedelta(hours=rh); rhrs=round(rh,2)
    else:
        res_dt=None; rhrs=None
        if age_h<6: status=pick(['Open','In Progress'],[.6,.4])
        else: status=pick(['Open','In Progress','Escalated'],[.25,.55,.20])
        inv={'Open':pick(['New','Triage']),'In Progress':pick(['Under Investigation','Containment','Remediation']),'Escalated':'Escalated to Incident Response'}[status]
        if first>NOW: first=NOW; rm=(NOW-created).total_seconds()/60
    due=created+pd.Timedelta(hours=SLA[sev])
    overdue=int(res_dt is None and NOW>due); breached=int(overdue or (res_dt is not None and res_dt>due))
    inc.append(dict(email_id=r.email_id,created_datetime=created,detection_source=src,severity=sev,attack_type=r.attack_type,department=r.department,target_user_id=r.target_user_id,
        assigned_team=team,assigned_analyst=an,status=status,investigation_status=inv,first_response_datetime=first,response_time_minutes=round(rm,1),
        resolved_datetime=res_dt,resolution_time_hours=rhrs,sla_target_hours=SLA[sev],sla_due_datetime=due,is_overdue=overdue,sla_breached=breached,
        credentials_compromised=int(r.submitted_credentials),remediation_action=pick(REM)))
I=pd.DataFrame(inc).sort_values('created_datetime').reset_index(drop=True)
I.insert(0,'incident_id',[f'INC-2026-{i+1:05d}' for i in range(len(I))])
I.insert(3,'created_date',I.created_datetime.dt.normalize()); I.insert(4,'year_month',I.created_datetime.dt.strftime('%Y-%m'))
I['resolved_date']=I.resolved_datetime.dt.normalize()
E['incident_id']=E.email_id.map(dict(zip(I.email_id,I.incident_id)))

# ---------------- simulations ----------------
TPL=[('Fake Password Reset',1.1,.45),('Gift Card Request',.8,.1),('Invoice Attached',1.0,.2),('Shared Document',1.2,.4),('HR Policy Update',1.1,.35),('Delivery Notice',.9,.2),('MFA Re-enrollment',1.0,.5)]
sims=[]
for m in range(1,12):
    sd=pd.Timestamp(2026,m,int(rng.integers(8,20)))
    while sd.weekday()>3: sd+=pd.Timedelta(days=1)
    tpl=TPL[(m-1)%len(TPL)]; t=(sd-START).days/(ND-1); sid=f'SIM-2026-{m:02d}'
    part=rng.choice(nU,size=int(nU*rng.uniform(.7,.85)),replace=False)
    for ui in part:
        u=U.iloc[ui]; delivered=1
        opened = rng.random()<.82
        clicked = int(opened and rng.random()<min(.9,u._cp*tpl[1]*(1.25-.4*t)*1.0))
        sub = int(clicked and rng.random()<tpl[2])
        rep = int(rng.random()<min(.95,u._rp*.6*(.8+.6*t)*(.3 if clicked else 1)))
        out='Submitted Credentials' if sub else 'Clicked' if clicked else 'Reported' if rep else 'No Action'
        sims.append(dict(simulation_id=sid,simulation_name=f'{sd.strftime("%b %Y")} - {tpl[0]}',template_type=tpl[0],send_date=sd,user_id=u.user_id,department=u.department,
            email_opened=int(opened),clicked=clicked,submitted_credentials=sub,reported=rep,minutes_to_report=round(ln(18,.9),1) if rep else None,outcome=out,passed=int(not clicked)))
S=pd.DataFrame(sims)

# ---------------- training ----------------
COURSES=[('TRN-01','Annual Security Awareness 2026','2026-01-15','2026-03-31',(.96,.04,0)),('TRN-02','Phishing Recognition Refresher','2026-06-01','2026-09-30',(.91,.09,0)),
 ('TRN-03','Social Engineering & BEC Defense','2026-10-01','2026-12-15',(.48,.22,.30))]
CPM=dict(zip(U.user_id,U._cp)); tr=[]
for cid,cn,a,d,(pc,pi,pn) in COURSES:
    a=pd.Timestamp(a); d=pd.Timestamp(d)
    for u in U.itertuples():
        adj=1-.25*CPM[u.user_id]
        if d<NOW:
            comp_=rng.random()<pc*adj
            status='Completed' if comp_ else 'Overdue'
        else:
            r=rng.random(); pcc=pc*adj
            status='Completed' if r<pcc else ('In Progress' if r<pcc+pi else 'Not Started')
        cd=None;score=None;mins=None
        if status=='Completed':
            late=rng.random()<.12
            cd=min(a+pd.Timedelta(days=int(rng.integers(1,(d-a).days))) + (pd.Timedelta(days=int(rng.integers(1,20))) if late and d<NOW else pd.Timedelta(0)),NOW).normalize()
            score=int(np.clip(rng.normal(86,9),50,100)); mins=int(rng.integers(25,70))
        tr.append(dict(training_id=f'{cid}-{u.user_id}',course_id=cid,course_name=cn,user_id=u.user_id,department=u.department,assigned_date=a,due_date=d,status=status,completion_date=cd,
            score_pct=score,duration_minutes=mins,completed_on_time=(int(cd<=d) if cd is not None else None)))
T=pd.DataFrame(tr)

# ---------------- daily filter stats ----------------
dc=E[E.is_detected==1].groupby('received_date').size()
fd=[]
for i,d in enumerate(days):
    t=i/(ND-1); wk=d.weekday()>=5
    scanned=int(rng.normal(12000 if wk else 46000*(.95+.15*rng.random()),1500))
    det=int(dc.get(d,0)); fp=int(rng.poisson(.00007*scanned*(1.15-.35*t)))
    fd.append(dict(date=d,total_inbound_emails_scanned=scanned,phishing_detected=det,false_positives=fp,total_flagged=det+fp,false_positive_rate_pct=round(100*fp/max(det+fp,1),2),
        legit_emails_released_after_review=int(fp*rng.uniform(.8,1.0))))
F=pd.DataFrame(fd)

# ---------------- dimensions ----------------
dd=pd.date_range('2026-01-01','2026-12-31')
D=pd.DataFrame(dict(date=dd,year=dd.year,quarter='Q'+dd.quarter.astype(str),month_num=dd.month,month_name=dd.strftime('%B'),year_month=dd.strftime('%Y-%m'),
  iso_week=dd.isocalendar().week.astype(int).values,week_start_date=dd-pd.to_timedelta(dd.weekday,unit='D'),day_of_week=dd.day_name(),day_of_week_num=dd.weekday+1,is_weekend=(dd.weekday>=5).astype(int)))
DEP=pd.DataFrame(dept_rows)
C=pd.DataFrame([dict(campaign_id=c['campaign_id'],campaign_name=c['campaign_name'],primary_attack_type=c['type'],start_date=c['start'],end_date=c['end'],duration_days=(c['end']-c['start']).days+1,
  primary_target_department=', '.join(c['focus']) or 'Broad / None',origin_countries=', '.join(dict.fromkeys(c['countries'])),sender_domain_count=len(c['domains']),threat_actor_alias=c['actor']) for c in camps]+
  [dict(campaign_id='CMP-000',campaign_name='Opportunistic (Unattributed)',primary_attack_type='Mixed',start_date=START,end_date=NOW.normalize(),duration_days=ND,primary_target_department='Broad / None',origin_countries='Various',sender_domain_count=len(pool),threat_actor_alias='Unattributed')])
C['total_emails']=C.campaign_id.map(E.campaign_id.value_counts()).fillna(0).astype(int)
Ud=U.drop(columns=[c for c in U.columns if c.startswith('_')])
tabs={'dim_date':D,'dim_department':DEP,'dim_user':Ud,'dim_campaign':C,'fact_phishing_emails':E,'fact_incidents':I,'fact_simulations':S,'fact_training':T,'fact_filter_daily':F}
for k,v in tabs.items(): v.to_csv(f'{OUT}/{k}.csv',index=False)
for k,v in tabs.items(): print(k,v.shape)
