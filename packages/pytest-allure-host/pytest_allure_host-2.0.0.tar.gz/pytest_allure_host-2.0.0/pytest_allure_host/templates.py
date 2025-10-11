"""Template and asset constants for Allure hosting publisher.

Separating large inline CSS/JS blobs from logic code improves readability and
keeps `publisher.py` focused on assembling manifests and uploading artifacts.

Constants here are intentionally raw (no minification beyond what was already
present) to avoid altering runtime behaviour. Any future templating engine
integration can replace these with loader functions while tests assert for
key sentinel substrings.
"""

# flake8: noqa  # Long lines expected for embedded assets

# ---------------------------- Runs Index CSS ----------------------------
RUNS_INDEX_CSS_BASE = (
    ":root{--bg:#fff;--bg-alt:#f6f8fa;--border:#d0d7de;--accent:#0366d6;--pass:#2e7d32;--fail:#d32f2f;--broken:#ff9800;--warn:#d18f00;--code-bg:#f2f4f7;--text:#111;--text-dim:#555;}"
    "@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--bg-alt:#161b22;--border:#30363d;--accent:#58a6ff;--text:#e6edf3;--text-dim:#9aa3b1;--code-bg:#1c232b;}}"
)

RUNS_INDEX_CSS_TABLE = (
    "body{font-family:system-ui;margin:1.5rem;background:var(--bg);color:var(--text);}"  # noqa: E501
    "table{border-collapse:collapse;width:100%;font-size:13px;}"
    "th,td{padding:.45rem .55rem;border:1px solid var(--border);text-align:left;}"
    "thead th{background:var(--bg-alt);position:sticky;top:0;z-index:2;}"
    "tbody tr:nth-child(even){background:var(--bg-alt);}"  # noqa: E501
    "code{background:var(--code-bg);padding:2px 4px;border-radius:3px;font-size:12px;}"
)

RUNS_INDEX_CSS_MISC = (
    ".stats{font-size:12px;color:var(--text-dim);margin:.25rem 0 0;}"
    ".controls{display:flex;flex-wrap:wrap;gap:.5rem;margin:.6rem 0 1rem;align-items:flex-start;}"
    ".controls-section{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;}"
    ".controls input[type=text]{padding:.4rem .55rem;font-size:13px;border:1px solid var(--border);background:var(--bg-alt);color:var(--text);}"  # noqa: E501
    ".badge{display:inline-block;padding:2px 6px;border-radius:999px;font-size:11px;font-weight:600;}"
    ".badge-pass{background:var(--pass);color:#fff;}"
    ".badge-fail{background:var(--fail);color:#fff;}"
    ".badge-broken{background:var(--broken);color:#fff;}"
    "tbody tr.row-fail{outline:2px solid var(--fail);outline-offset:-2px;}"
    ".link-btn.copied{color:var(--pass);}"  # existing style piece
    ".col-hidden{display:none !important;}"  # hide columns when toggled
    "#col-panel button{font-size:11px;}"  # existing style piece
    ".pfb-pass{color:var(--pass);font-weight:600;}"
    ".pfb-fail{color:var(--fail);font-weight:600;}"
    ".pfb-broken{color:var(--broken);font-weight:600;}"
    ".dense td, .dense th{padding:.25rem .35rem !important;font-size:12px;}"
    ".tag-chip{display:inline-block;background:var(--bg-alt);border:1px solid var(--border);padding:2px 5px;margin:0 4px 3px 0;border-radius:12px;font-size:11px;cursor:pointer;user-select:none;}"
    ".tag-chip:hover{background:var(--accent);color:#fff;border-color:var(--accent);}"
    "#spark-wrap{display:flex;flex-direction:column;gap:.25rem;}"
    "#spark{width:140px;height:26px;display:block;}"
    "\n.sr-only{position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden;}"
)

# Additional enhancements CSS (density toggle, in-progress marker, notice)
RUNS_INDEX_CSS_ENH = (
    "#runs-table.dense td{padding:4px 6px}"  # compact row density
    "#runs-table.dense th{padding:4px 6px}"  # ensure headers match
    ".run--inprogress .time::after{content:' • running';font-style:italic;color:#666;}"
    "#notice{margin:8px 0;color:#444;font-style:italic;}"
)

# ---------------------------- Runs Index JS ----------------------------
# NOTE: INIT and BATCH values are injected separately by publisher.
RUNS_INDEX_JS = (
    "(function(){"
    "const tbl=document.getElementById('runs-table');"
    "const filter=document.getElementById('run-filter');"
    "const stats=document.getElementById('stats');"
    "const pfbStats=document.getElementById('pfb-stats');"
    "const onlyFail=document.getElementById('only-failing');"
    "const clearBtn=document.getElementById('clear-filter');"
    "const themeBtn=document.getElementById('theme-toggle');"
    "const accentBtn=document.getElementById('accent-toggle');"
    "const colBtn=document.getElementById('col-toggle');"
    "const densityBtn=document.getElementById('density-toggle');"
    "const tzBtn=document.getElementById('tz-toggle');"
    "let localTime=false;"
    "let colPanel=null;"
    "const LS='ah_runs_';"
    "function lsGet(k){try{return localStorage.getItem(LS+k);}catch(e){return null;}}"
    "function lsSet(k,v){try{localStorage.setItem(LS+k,v);}catch(e){}}"
    "function hidden(){return [...tbl.tBodies[0].querySelectorAll('tr.pr-hidden')];}"
    "function updateLoadButton(){const hiddenRows=hidden();const loadBtn=document.getElementById('load-more');if(!loadBtn)return;if(hiddenRows.length){loadBtn.style.display='inline-block';loadBtn.textContent='Load more ('+hiddenRows.length+')';}else{loadBtn.style.display='none';}}"
    "function revealNextBatch(batch){hidden().slice(0,batch).forEach(r=>r.classList.remove('pr-hidden'));updateLoadButton();}"  # progressive reveal
    "function failingTotal(){return [...tbl.tBodies[0].rows].reduce((a,r)=>a+ (Number(r.dataset.failed||0)>0?1:0),0);}"
    "function applyStats(){const total=tbl.tBodies[0].rows.length;const rows=[...tbl.tBodies[0].rows];const vis=rows.filter(r=>r.style.display!=='none');stats.textContent=vis.length+' / '+total+' shown';let p=0,f=0,b=0;vis.forEach(r=>{p+=Number(r.dataset.passed||0);f+=Number(r.dataset.failed||0);b+=Number(r.dataset.broken||0);});pfbStats.textContent=' P:'+p+' F:'+f+' B:'+b;}"
    "function applyFooter(){const total=tbl.tBodies[0].rows.length;const hid=hidden().length;const el=document.getElementById('footer-stats');if(el){el.textContent=(total-hid)+' / '+total+' loaded';}}"
    "function applyFilter(){const loadBtn=document.getElementById('load-more');const raw=filter.value.trim().toLowerCase();const tokens=raw.split(/\\s+/).filter(Boolean);const onlyF=onlyFail.checked;if(tokens.length&&document.querySelector('.pr-hidden')){hidden().forEach(r=>r.classList.remove('pr-hidden'));updateLoadButton();}const rows=[...tbl.tBodies[0].rows];rows.forEach(r=>{const hay=r.getAttribute('data-search')||'';const hasTxt=!tokens.length||tokens.every(t=>hay.indexOf(t)>-1);const failing=Number(r.dataset.failed||0)>0;r.style.display=(hasTxt&&(!onlyF||failing))?'':'none';if(failing){r.classList.add('failing-row');}else{r.classList.remove('failing-row');}});document.querySelectorAll('tr.row-active').forEach(x=>x.classList.remove('row-active'));if(tokens.length===1){const rid=tokens[0];const match=[...tbl.tBodies[0].rows].find(r=>r.querySelector('td.col-run_id code')&&r.querySelector('td.col-run_id code').textContent.trim().toLowerCase()===rid);if(match)match.classList.add('row-active');}applyStats();}"
    "function relFmt(sec){if(sec<60)return Math.floor(sec)+'s';sec/=60;if(sec<60)return Math.floor(sec)+'m';sec/=60;if(sec<24)return Math.floor(sec)+'h';sec/=24;if(sec<7)return Math.floor(sec)+'d';const w=Math.floor(sec/7);if(w<4)return w+'w';const mo=Math.floor(sec/30);if(mo<12)return mo+'mo';return Math.floor(sec/365)+'y';}"
    "function updateAges(){const now=Date.now()/1000;tbl.tBodies[0].querySelectorAll('td.age').forEach(td=>{const ep=Number(td.getAttribute('data-epoch'));if(!ep){td.textContent='-';return;}td.textContent=relFmt(now-ep);});}"
    "const loadBtn=document.getElementById('load-more');if(loadBtn){loadBtn.addEventListener('click',()=>{revealNextBatch(Number(loadBtn.getAttribute('data-batch'))||300);applyFilter();lsSet('loaded',String(tbl.tBodies[0].rows.length-hidden().length));});}"
    "// Infinite scroll (observer)"
    "if('IntersectionObserver' in window && loadBtn){const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting && hidden().length){revealNextBatch(Number(loadBtn.getAttribute('data-batch'))||300);applyFilter();}});},{root:null,rootMargin:'120px'});io.observe(loadBtn);}"
    "filter.addEventListener('input',()=>{applyFilter();lsSet('filter',filter.value);});"
    "filter.addEventListener('keydown',e=>{if(e.key==='Enter'){applyFilter();}});"
    "onlyFail.addEventListener('change',()=>{applyFilter();lsSet('onlyFail',onlyFail.checked?'1':'0');});"
    "clearBtn&&clearBtn.addEventListener('click',()=>{filter.value='';onlyFail.checked=false;applyFilter();filter.focus();});"
    "const ACCENTS=['#0366d6','#6f42c1','#d32f2f','#1b7f3b','#b08800'];"
    "function applyAccent(c){document.documentElement.style.setProperty('--accent',c);lsSet('accent',c);}"  # noqa: E501
    "accentBtn&&accentBtn.addEventListener('click',()=>{const cur=lsGet('accent')||ACCENTS[0];const idx=(ACCENTS.indexOf(cur)+1)%ACCENTS.length;applyAccent(ACCENTS[idx]);});"
    "function applyTheme(mode){document.documentElement.classList.remove('force-light','force-dark');if(mode==='light'){document.documentElement.classList.add('force-light');}else if(mode==='dark'){document.documentElement.classList.add('force-dark');}lsSet('theme',mode);}"  # noqa: E501
    "themeBtn&&themeBtn.addEventListener('click',()=>{const cur=lsGet('theme')||'auto';const next=cur==='auto'?'dark':(cur==='dark'?'light':'auto');applyTheme(next);themeBtn.textContent='Theme('+next+')';});"
    "densityBtn&&densityBtn.addEventListener('click',()=>{const dense=tbl.classList.toggle('dense');lsSet('dense',dense?'1':'0');densityBtn.textContent=dense?'Dense(-)':'Dense(+)' ;});"
    "tzBtn&&tzBtn.addEventListener('click',()=>{localTime=!localTime;updateTimeCells();tzBtn.textContent=localTime?'UTC':'Local';lsSet('tz',localTime?'local':'utc');});"
    "function updateTimeCells(){[...tbl.tBodies[0].rows].forEach(r=>{const utcCell=r.querySelector('td.col-utc');if(!utcCell)return;const ep=Number(r.dataset.epoch||0);if(!ep){utcCell.textContent='-';return;}if(localTime){const d=new Date(ep*1000);utcCell.textContent=d.toLocaleString();}else{const d=new Date(ep*1000);utcCell.textContent=d.toISOString().replace('T',' ').slice(0,19);} });}"
    "function extract(r,col){if(col.startsWith('meta:')){const idx=[...tbl.tHead.querySelectorAll('th')].findIndex(h=>h.dataset.col===col);return idx>-1?r.cells[idx].textContent:'';}switch(col){case 'size':return r.querySelector('td.col-size').getAttribute('title');case 'files':return r.querySelector('td.col-files').getAttribute('title');case 'pfb':return r.querySelector('td.col-pfb').textContent;case 'passpct':return r.querySelector('td.col-passpct').textContent;case 'run_id':return r.querySelector('td.col-run_id').textContent;case 'utc':return r.querySelector('td.col-utc').textContent;case 'context':return r.querySelector('td.col-context').textContent;case 'tags':return r.querySelector('td.col-tags').textContent;default:return r.textContent;}}"
    "let sortState=null;"
    "function sortBy(th){const col=th.dataset.col;const tbody=tbl.tBodies[0];const rows=[...tbody.rows];let dir=1;if(sortState&&sortState.col===col){dir=-sortState.dir;}sortState={col,dir};const numeric=(col==='size'||col==='files');rows.sort((r1,r2)=>{const a=extract(r1,col);const b=extract(r2,col);if(numeric){return ((Number(a)||0)-(Number(b)||0))*dir;}return a.localeCompare(b)*dir;});rows.forEach(r=>tbody.appendChild(r));tbl.tHead.querySelectorAll('th.sortable').forEach(h=>h.removeAttribute('data-sort'));th.setAttribute('data-sort',dir===1?'asc':'desc');updateAriaSort();lsSet('sort_col',col);lsSet('sort_dir',String(dir));}"
    "tbl.tHead.querySelectorAll('th.sortable').forEach(th=>{th.addEventListener('click',()=>sortBy(th));});"
    "function updateAriaSort(){tbl.tHead.querySelectorAll('th.sortable').forEach(th=>{th.setAttribute('aria-sort','none');});if(sortState){const th=tbl.tHead.querySelector(`th[data-col='${sortState.col}']`);if(th)th.setAttribute('aria-sort',sortState.dir===1?'ascending':'descending');}}"  # noqa: E501
)
# Ensure sortBy calls updateAriaSort: simple append inside closure
if "function sortBy(th)" in RUNS_INDEX_JS:
    RUNS_INDEX_JS = RUNS_INDEX_JS.replace(
        "rows.forEach(r=>tbody.appendChild(r));tbl.tHead.querySelectorAll('th.sortable').forEach(h=>h.removeAttribute('data-sort'));th.setAttribute('data-sort',dir===1?'asc':'desc');lsSet('sort_col',col);lsSet('sort_dir',String(dir));}",
        "rows.forEach(r=>tbody.appendChild(r));tbl.tHead.querySelectorAll('th.sortable').forEach(h=>h.removeAttribute('data-sort'));th.setAttribute('data-sort',dir===1?'asc':'desc');updateAriaSort();lsSet('sort_col',col);lsSet('sort_dir',String(dir));}",
    )

# Sentinel substrings used in tests to verify template inclusion
RUNS_INDEX_SENTINELS = [
    "ah_runs_",
    "col-toggle",
    "function applyFilter()",
]

# Post-bootstrap JS enhancements: aria-sort hook exposure, filter+URL glue,
# density persistence (already partly handled), failing-run notice, and
# in-progress marking using data-end-iso absence (v1 contract compliance).
RUNS_INDEX_JS_ENH = (
    "document.addEventListener('DOMContentLoaded',()=>{"
    "const table=document.getElementById('runs-table');if(!table)return;"
    "if(localStorage.getItem('runs.dense')==='1'){table.classList.add('dense');}"
    "table.querySelectorAll('tbody tr[data-v=\"1\"]').forEach(tr=>{if(!tr.dataset.endIso){tr.classList.add('run--inprogress');}});"
    "window.setAriaSort=function(idx,dir){table.querySelectorAll('thead th').forEach((th,i)=>th.setAttribute('aria-sort',i===idx?dir:'none'));};"
    "function setQS(k,v){const q=new URLSearchParams(location.search);if(v){q.set(k,v);}else{q.delete(k);}history.replaceState(null,'','?'+q);}"
    "function applyFilters(){const q=new URLSearchParams(location.search);const gi=id=>document.getElementById(id);const branch=(gi('f-branch')?gi('f-branch').value.trim():q.get('branch')||'');const tagsStr=(gi('f-tags')?gi('f-tags').value.trim():q.get('tags')||'');const tags=tagsStr.split(',').filter(Boolean);const from=(gi('f-from')?gi('f-from').value:q.get('from'));const to=(gi('f-to')?gi('f-to').value:q.get('to'));let failing=(gi('f-onlyFailing')?gi('f-onlyFailing').checked:(q.get('onlyFailing')==='1')),anyFail=false;const fromEpoch=from?Date.parse(from+'T00:00:00Z')/1000:0;const toEpoch=to?(Date.parse(to+'T23:59:59Z')/1000):0;table.querySelectorAll('tbody tr[data-v=\"1\"]').forEach(tr=>{const rowBr=(tr.dataset.branch||'');const okBranch=!branch||rowBr===branch||rowBr.indexOf(branch)>=0;let rowTags=[];try{rowTags=JSON.parse(tr.dataset.tags||'[]');}catch(e){}const okTags=!tags.length||tags.every(t=>rowTags.includes(t));const epoch=parseInt(tr.dataset.epoch||'0',10);const okFrom=!from|| (epoch && epoch>=fromEpoch);const okTo=!to|| (epoch && epoch<=toEpoch);const isFail=(parseInt(tr.dataset.f||'0',10)>0);if(isFail)anyFail=true;const okFail=!failing||isFail;tr.hidden=!(okBranch&&okTags&&okFrom&&okTo&&okFail);});if(failing&&!anyFail){const q2=new URLSearchParams(location.search);q2.delete('onlyFailing');history.replaceState(null,'','?'+q2);let n=document.getElementById('notice');if(!n){n=document.createElement('div');n.id='notice';document.body.insertBefore(n,document.body.firstChild);}n.setAttribute('role','status');n.textContent='No failing runs — filter cleared.';}}"
    "window.applyFilters=applyFilters;applyFilters();window._setQSFilter=setQS;"
    "});"
)

# ---------------------------- Dashboard / Summary JS & CSS ----------------------------
# Consolidated summary cards + empty state + toggle logic, extracted from inline string.
RUNS_INDEX_DASHBOARD_CSS = (
    ".sc-toggle{margin:.25rem 0;padding:.25rem .5rem;border:1px solid var(--border,#2b2b2b);background:var(--bg-alt);border-radius:.5rem;cursor:pointer;font-size:12px}"
    "#summary-cards .v.ok{color:#0a7a0a}#summary-cards .v.warn{color:#b8860b}#summary-cards .v.bad{color:#b00020}"
    ".empty{margin:.5rem 0;padding:.6rem .8rem;border:1px solid var(--border,#2b2b2b);border-radius:.5rem;background:var(--bg-alt);opacity:.85;font-size:12px}"
)

RUNS_INDEX_DASHBOARD_JS = (
    "(function(){const tbl=document.getElementById('runs-table');const cards=document.getElementById('summary-cards');if(!tbl||!cards)return;"
    "if(!document.getElementById('sc-span')){const spanCard=document.createElement('div');spanCard.className='card';spanCard.innerHTML='<div class=\"k\">Time span</div><div class=\"v\" id=\"sc-span\">—</div>';cards.appendChild(spanCard);}"
    "const empty=document.getElementById('empty-msg');const toggle=document.getElementById('summary-toggle');"
    "function visibleRows(){return [...tbl.querySelectorAll('tbody tr[data-v]')].filter(r=>!(r.hidden||getComputedStyle(r).display==='none'));}"
    "function fmtPct(n){return isFinite(n)?(Math.round(n*10)/10).toFixed(1)+'%':'—';}"
    r"function update(){const rows=visibleRows();if(empty)empty.hidden=rows.length!==0;const passEl=document.getElementById('sc-pass');const failEl=document.getElementById('sc-fail');const countEl=document.getElementById('sc-count');const latestEl=document.getElementById('sc-latest');let p=0,f=0,b=0,latestIso=null,latestId='—';rows.forEach(r=>{p+=+r.dataset.p||0;f+=+r.dataset.f||0;b+=+r.dataset.b||0;const iso=r.dataset.startIso||r.querySelector('[data-iso]')?.getAttribute('data-iso');if(iso&&(!latestIso||iso>latestIso)){latestIso=iso;latestId=r.dataset.runId||r.getAttribute('data-run-id')||'—';}});if(rows.length===0){[passEl,failEl,countEl,latestEl].forEach(el=>el&&(el.textContent='—'));const span=document.getElementById('sc-span');if(span)span.textContent='—';return;}const total=p+f+b;passEl&&(passEl.textContent=total?fmtPct(p/total*100):'—',passEl.classList.remove('ok','warn','bad'),(()=>{const num=parseFloat(passEl.textContent)||NaN;if(!isNaN(num))passEl.classList.add(num>=90?'ok':(num>=75?'warn':'bad'));})());failEl&&(failEl.textContent=String(f));countEl&&(countEl.textContent=String(rows.length));if(latestEl){if(latestIso){const base=location.pathname.replace(/runs/index\.html.*/,'');latestEl.innerHTML='<a href=\"'+base+latestId+'/\" title=\"Open latest run\">'+latestId+'</a>'; }else{latestEl.textContent=latestId;}}const span=document.getElementById('sc-span');if(span){const isoVals=rows.map(r=>r.dataset.startIso||'').filter(Boolean).sort();if(isoVals.length){const fmt=iso=>{try{return new Date(iso).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'});}catch(e){return iso;}};span.textContent=fmt(isoVals[0])+' → '+fmt(isoVals[isoVals.length-1]);}}}"
    "const orig=window.applyFilters;window.applyFilters=function(){orig&&orig();update();};document.addEventListener('DOMContentLoaded',update);update();"
    "if(toggle){const key='runs.summary.collapsed';function setC(c){cards.hidden=c;toggle.setAttribute('aria-expanded',String(!c));toggle.textContent=c?'Summary ▶':'Summary ▼';try{localStorage.setItem(key,c?'1':'0');}catch(e){}}toggle.addEventListener('click',()=>setC(!cards.hidden));setC((()=>{try{return localStorage.getItem(key)==='1';}catch(e){return false;}})());}"
    "})();"
)
