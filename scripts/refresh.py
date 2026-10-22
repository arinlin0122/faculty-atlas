import concurrent.futures,datetime,json,pathlib,urllib.request,urllib.error,xml.etree.ElementTree as ET
root=pathlib.Path(__file__).resolve().parent.parent
path=root/'status.json'
previous=json.loads(path.read_text()) if path.exists() else {}
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
report=dict(previous,checkedAt=now(),feedError=None)
try:
    req=urllib.request.Request('https://www.raspberrypi.org/blog/feed/',headers={'User-Agent':'FacultyAtlas/1.0'})
    with urllib.request.urlopen(req,timeout=30) as r: feed=ET.fromstring(r.read())
    articles=[{'title':i.findtext('title'),'url':i.findtext('link'),'date':i.findtext('pubDate')} for i in feed.findall('.//item')[:6]]
    articles=[i for i in articles if i['title'] and (i['url'] or '').startswith('https://www.raspberrypi.org/')]
    if not articles: raise ValueError('No valid feed items')
    report.update(articles=articles,feedUpdatedAt=now())
except Exception as e: report['feedError']=str(e)
urls=['https://www.teacherhorizons.com/jobs?countries=China','https://www.teacherhorizons.com/jobs?countries=China&subjects=Physics','https://www.tes.com/jobs/browse/china','https://www.teacherhorizons.com/jobs','https://www.teacherhorizons.com/subjects/physics','https://www.schrole.com/','https://www.tes.com/jobs/','https://phet.colorado.edu/','https://spark.iop.org/','https://teachcomputing.org/','https://www.raspberrypi.org/','https://www.ibo.org/professional-development/']
def check(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'FacultyAtlas/1.0'}),timeout=20) as r: code=r.status
        return {'url':url,'status':code,'state':'Responding'}
    except urllib.error.HTTPError as e: return {'url':url,'status':e.code,'state':'Access limited' if e.code in (403,429) else 'Needs review'}
    except Exception: return {'url':url,'status':None,'state':'Could not check'}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: report['sources']=list(pool.map(check,urls))
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
if report['feedError']: raise SystemExit('Feed refresh failed; retained previous content: '+report['feedError'])
print('Refreshed',len(report['articles']),'articles at',report['feedUpdatedAt'])
