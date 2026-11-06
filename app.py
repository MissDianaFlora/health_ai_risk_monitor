from pathlib import Path
import pandas as pd, plotly.express as px, streamlit as st
BASE=Path(__file__).resolve().parent; FILE=BASE/'data'/'health_ai_risks.csv'
st.set_page_config(page_title='Health AI Risk Monitor',page_icon='🩺',layout='wide')
st.title('Health AI Risk Monitor'); st.caption("What's new in publicly reported Health AI risk")
st.info('Monitoring research signals only. Items are not medical advice or proof of harm. Review original evidence before public or client claims.')
if not FILE.exists(): st.error('No monitoring data yet. Run `python monitor.py` first.'); st.stop()
df=pd.read_csv(FILE,encoding='utf-8-sig'); df['published_date']=pd.to_datetime(df.published_at,errors='coerce',utc=True); df['first_seen_date']=pd.to_datetime(df.first_seen_at,errors='coerce',utc=True); now=pd.Timestamp.now(tz='UTC')
with st.sidebar:
 st.header('Monitor filters'); window=st.radio('Monitoring window',['24 hours','7 days','30 days','All'],index=2); cond=st.multiselect('Health condition',sorted(df.health_condition.dropna().unique())); risk=st.multiselect('Risk category',sorted(df.risk_category.dropna().unique())); sev=st.slider('Minimum severity',1,5,1)
 dates=df.published_date.dropna().dt.date; dr=st.date_input('Source published/released',value=(dates.min(),dates.max()),min_value=dates.min(),max_value=dates.max()) if len(dates) else ()
f=df.copy(); delta={'24 hours':pd.Timedelta(hours=24),'7 days':pd.Timedelta(days=7),'30 days':pd.Timedelta(days=30)}.get(window)
if delta is not None:f=f[f.first_seen_date>=now-delta]
if cond:f=f[f.health_condition.isin(cond)]
if risk:f=f[f.risk_category.isin(risk)]
f=f[f.severity>=sev]
if isinstance(dr,(tuple,list)) and len(dr)==2:f=f[(f.published_date.dt.date>=dr[0])&(f.published_date.dt.date<=dr[1])]
new24=int((df.first_seen_date>=now-pd.Timedelta(hours=24)).sum()); new7=int((df.first_seen_date>=now-pd.Timedelta(days=7)).sum()); new30=int((df.first_seen_date>=now-pd.Timedelta(days=30)).sum()); regulatory=int(df.is_regulatory_watch.fillna(False).astype(bool).sum())
a,b,c,d=st.columns(4); a.metric('New in 24h',new24); b.metric('New in 7 days',new7); c.metric('New in 30 days',new30); d.metric('Regulatory watch',regulatory)
tabs=st.tabs(["What's New",'Risk Watch','Regulatory Watch','Health Conditions','Explore Signals','Methodology'])
with tabs[0]:
 st.subheader("What's New")
 latest=f.sort_values('first_seen_date',ascending=False)
 for _,r in latest.head(25).iterrows():
  badge='🆕 NEW' if r.first_seen_date>=now-pd.Timedelta(hours=48) else 'Monitoring'; st.markdown(f"**{badge} · {r.risk_category} · Severity {int(r.severity)}/5**")
  st.markdown(f"[{r.title}]({r.url})"); st.caption(f"Published: {r.published_date.date() if pd.notna(r.published_date) else 'Unknown'} · First seen: {r.first_seen_date.strftime('%Y-%m-%d %H:%M UTC') if pd.notna(r.first_seen_date) else 'Unknown'} · {r.publisher} · {r.health_condition} · {r.ai_use_case}"); st.divider()
with tabs[1]:
 x=f.risk_category.value_counts().reset_index(); x.columns=['Risk','Signals']; st.plotly_chart(px.bar(x,x='Signals',y='Risk',orientation='h',title='Current monitored risk signals'),use_container_width=True)
 dated=f.dropna(subset=['published_date']).copy(); dated['date']=dated.published_date.dt.date; tr=dated.groupby(['date','risk_category']).size().reset_index(name='Signals'); st.plotly_chart(px.line(tr,x='date',y='Signals',color='risk_category',markers=True,title='Risk signals by source publication date'),use_container_width=True)
with tabs[2]:
 reg=f[f.is_regulatory_watch.fillna(False).astype(bool)]; st.metric('Regulatory/official-source signals in selected view',len(reg)); st.dataframe(reg[['published_at','title','publisher','health_condition','risk_category','severity','url']],column_config={'url':st.column_config.LinkColumn('Source',display_text='Open ↗')},hide_index=True,use_container_width=True)
with tabs[3]:
 x=f.health_condition.value_counts().reset_index(); x.columns=['Health condition','Signals']; st.plotly_chart(px.bar(x,x='Signals',y='Health condition',orientation='h',title='Signals by health condition'),use_container_width=True)
with tabs[4]:
 disp=f.copy(); disp['Read']=disp.url; st.dataframe(disp[['published_at','first_seen_at','title','Read','publisher','health_condition','ai_use_case','risk_category','severity','evidence_level','watch_status']],column_config={'Read':st.column_config.LinkColumn('Article',display_text='Open source ↗')},hide_index=True,use_container_width=True); st.download_button('Download filtered monitoring data',f.to_csv(index=False).encode('utf-8-sig'),'health_ai_monitor.csv','text/csv')
with tabs[5]:
 st.markdown('''### Monitoring model
**Public source → first detected → risk classification → condition/use-case tagging → ongoing watch.**

`published_at` is when the source says the article was published. `first_seen_at` is when this monitor first discovered the record. The app uses first-seen time for **What's New** and source publication time for the date filter.

All records default to **Pending human review**. Absence of new articles is not treated as evidence that a risk is resolved.''')
