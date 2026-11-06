from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime, timezone
import hashlib, html, re, unicodedata
import feedparser, pandas as pd
from bs4 import BeautifulSoup
from ftfy import fix_text
BASE=Path(__file__).resolve().parent; DATA=BASE/'data'; DATA.mkdir(parents=True,exist_ok=True); OUT=DATA/'health_ai_risks.csv'
QUERIES=['healthcare AI patient safety','medical AI diagnostic error','health AI bias patients','AI cancer diagnosis error','AI medical device recall','healthcare AI privacy breach','clinical AI regulatory investigation','generative AI medical misinformation','AI mental health patient safety','AI cardiovascular diagnosis risk','AI maternal health safety']
RISK={'Diagnostic accuracy':['misdiagnosis','missed diagnosis','diagnostic error','false positive','false negative','inaccurate'],'Bias and health inequality':['bias','discrimination','health inequality','disparate'],'Patient safety':['patient harm','patient safety','unsafe','adverse event','injury'],'Privacy and data protection':['privacy','data breach','patient data','health data'],'Hallucination and misinformation':['hallucination','misinformation','false information','incorrect advice'],'Transparency and explainability':['black box','explainability','transparency','opaque'],'Automation bias and oversight':['automation bias','human oversight','human review'],'Dataset and model quality':['model drift','training data','data quality'],'Cybersecurity':['cyberattack','ransomware','prompt injection','security breach'],'Regulatory and legal':['regulator','recall','investigation','lawsuit','fine','enforcement']}
CONDITIONS={'Cancer':['cancer','oncology','tumor','tumour'],'Diabetes':['diabetes','diabetic'],'Cardiovascular':['cardiovascular','heart disease','cardiac','stroke'],'Mental health':['mental health','depression','anxiety','psychiatric'],'Neurological':['neurological','dementia','alzheimer','parkinson'],'Maternal health':['maternal','pregnancy','obstetric']}
USES={'Medical imaging':['radiology','medical imaging','mri','ct scan','mammogram'],'Clinical decision support':['clinical decision','decision support','risk prediction'],'Diagnosis':['diagnosis','diagnostic','detection'],'Patient communication':['chatbot','virtual assistant'],'Medication/prescribing':['prescribing','medication','drug recommendation']}
REGULATORS=['fda','nih','who','mhra','nice','ema','department of health','nhs']
def clean(v):
 t=BeautifulSoup(html.unescape(str(v or '')),'html.parser').get_text(' '); return re.sub(r'\s+',' ',unicodedata.normalize('NFC',fix_text(t))).strip()
def classify(t,m,d):
 l=t.lower(); s={k:sum(x in l for x in v) for k,v in m.items()}; b=max(s,key=s.get); return b if s[b] else d
def severity(t):
 l=t.lower(); return 5 if any(x in l for x in ['death','fatal','serious injury']) else 4 if any(x in l for x in ['recall','patient harm','lawsuit','data breach']) else 3 if any(x in l for x in ['investigation','diagnostic error','false negative','false positive']) else 2
def evidence(t):
 l=t.lower(); return 'Formal/confirmed finding' if any(x in l for x in ['regulator found','court ruled','recall','fine imposed','confirmed']) else 'Reported/alleged' if any(x in l for x in ['investigation','lawsuit','complaint','alleged','reported']) else 'Emerging/potential'
def credibility(pub):
 p=pub.lower(); return 5 if any(x in p for x in REGULATORS) else 4 if any(x in p for x in ['reuters','associated press','bbc','financial times','nature','bmj','lancet']) else 3 if any(x in p for x in ['stat','medscape','fierce healthcare']) else 2
def run():
 now=datetime.now(timezone.utc); rows=[]
 old=pd.read_csv(OUT,encoding='utf-8-sig') if OUT.exists() else pd.DataFrame(); oldids=set(old.record_id.astype(str)) if len(old) else set()
 for q in QUERIES:
  feed=feedparser.parse(f'https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-GB&gl=GB&ceid=GB:en',request_headers={'User-Agent':'HealthAIRiskMonitor/1.0'})
  for e in feed.entries[:60]:
   src=e.get('source',{}); pub=clean(src.get('title','')) if isinstance(src,dict) else 'Unknown'; title=clean(e.get('title','')); suffix=f' - {pub}'; title=title[:-len(suffix)] if pub and title.endswith(suffix) else title; summary=clean(e.get('summary','')); text=f' {title} {summary} '; low=text.lower()
   if not any(x in low for x in ['health','medical','patient','clinical','hospital','cancer','diabetes','cardiac','mental health','neurolog','maternal','radiology']):continue
   if not any(x in low for x in ['artificial intelligence',' ai ','machine learning','algorithm','generative ai','chatbot','large language model']):continue
   url=str(e.get('link','')); rid=hashlib.sha256((title+'|'+url).encode()).hexdigest()[:20]; first_seen=now.isoformat(); status='New' if rid not in oldids else 'Monitoring'
   rows.append({'record_id':rid,'first_seen_at':first_seen,'collected_at':now.isoformat(),'published_at':str(e.get('published','')),'title':title,'summary':summary,'url':url,'publisher':pub,'health_condition':classify(text,CONDITIONS,'Other/General health'),'ai_use_case':classify(text,USES,'Other/Unclassified'),'risk_category':classify(text,RISK,'General AI governance risk'),'severity':severity(text),'evidence_level':evidence(text),'source_credibility_score':credibility(pub),'watch_status':status,'is_regulatory_watch':any(x in pub.lower() for x in REGULATORS),'review_status':'Pending human review','search_query':q})
 new=pd.DataFrame(rows)
 if len(old):
  # preserve original first_seen_at for previously known records
  if 'first_seen_at' not in old: old['first_seen_at']=old.get('collected_at','')
  combined=pd.concat([new,old],ignore_index=True); combined=combined.drop_duplicates('record_id',keep='last')
 else: combined=new
 if len(combined): combined.to_csv(OUT,index=False,encoding='utf-8-sig')
 print(f'Saved {len(combined)} unique monitoring signals.')
if __name__=='__main__':run()
