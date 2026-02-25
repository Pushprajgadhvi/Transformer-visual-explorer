"""
transformer_tools.py
──────────────────────
Merged utility / encoding-fix scripts for the Transformer Live Demo.
Each section is labelled with its original filename.

Usage:
  Run any section's main() directly, e.g.:
  >>> from transformer_tools import fix_encoding; fix_encoding.main()
  Or just run: python transformer_tools.py  (runs diagnostics by default)
"""



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: fix_encoding.py
# Original encoding fixer (fix nav icons, arrows in transformer_complete.html)


# ══════════════════════════════════════════════════════════════════════════════

with open('transformer_complete.html', 'rb') as f:
    data = f.read()

content = data.decode('utf-8', errors='replace')

# Fix the nav-icon spans — replace broken emoji with HTML entities
import re

nav_icons = {
    "goto('overview')": '&#127758;',   # globe
    "goto('embed')": '&#128288;',       # symbols  
    "goto('sdpa')": '&#127919;',        # target
    "goto('single')": '&#128065;',      # eye
    "goto('multi')": '&#129504;',       # brain
    "goto('masked')": '&#128274;',      # lock
    "goto('cross')": '&#128279;',       # link
    "goto('ffn')": '&#9881;',           # gear
    "goto('encoder')": '&#128442;',     # inbox
    "goto('decoder')": '&#128452;',     # outbox
    "goto('train')": '&#128200;',       # chart
}

# Fix each nav item by replacing the broken icon span content
for nav_fn, icon in nav_icons.items():
    # Pattern: <div class="nav-item..." onclick="goto('xxx')"><span class="nav-icon">???</span>
    pattern = r'(<div class="nav-item[^"]*" onclick="' + nav_fn.replace('(', r'\(').replace(')', r'\)').replace("'", r"'") + r'"><span class="nav-icon">)[^<]+(</span>)'
    replacement = r'\g<1>' + icon + r'\g<2>'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        content = new_content
        print(f'Fixed icon for {nav_fn}')
    else:
        print(f'No match for {nav_fn}')

# Fix nav logo
content = content.replace(
    '<h1>⚡ Transformer Guide</h1>',
    '<h1>&#9889; Transformer Guide</h1>'
)

# Also fix arch-arrow divs (the ↓ arrows)
content = re.sub(r'<div class="arch-arrow">[^<]*N layers</div>',
    '<div class="arch-arrow">&#8595; x N layers</div>', content)
content = re.sub(r'(<div class="arch-arrow">)[^<]+(</div>)',
    r'\g<1>&#8595;\g<2>', content, count=20)

with open('transformer_complete.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. File size:', len(open('transformer_complete.html','rb').read()), 'bytes')



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: append_js.py
# JavaScript appender — appends the full <script> block to transformer_complete.html


# ══════════════════════════════════════════════════════════════════════════════

js = r"""
<script>
// ====================================================
// MATH CORE
// ====================================================
let rng;
function seedRng(s){rng=()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};}
function rn(){let u=0,v=0;while(!u)u=rng();while(!v)v=rng();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function cm(r,c,sc=0.35){return Array.from({length:r},()=>Array.from({length:c},()=>+(rn()*sc).toFixed(3)));}
function mm(A,B){const r=A.length,k=B.length,c=B[0].length;return Array.from({length:r},(_,i)=>Array.from({length:c},(__,j)=>A[i].reduce((s,v,l)=>s+v*B[l][j],0)));}
function smx(v,t=1){const s=v.map(x=>x/t),mx=Math.max(...s),ex=s.map(x=>Math.exp(x-mx)),sm=ex.reduce((a,b)=>a+b,0);return ex.map(x=>+(x/sm).toFixed(4));}
function pe(pos,d){return Array.from({length:d},(_,i)=>i%2===0?Math.sin(pos/Math.pow(10000,i/d)):Math.cos(pos/Math.pow(10000,(i-1)/d)));}
function hashStr(s){return s.split('').reduce((a,c)=>a+c.charCodeAt(0),0);}
function toks(s){return s.trim().split(/\s+/).filter(Boolean).slice(0,8);}
function embed(tList,d){seedRng(hashStr(tList.join('')));return tList.map((_,i)=>{const e=Array.from({length:d},()=>+(rn()*0.5).toFixed(3));const p=pe(i,d);return e.map((v,j)=>+(v+p[j]*0.1).toFixed(3));});}
function selfAttn(tkns,d,temp=1){
  const emb=embed(tkns,d);
  const Wq=cm(d,d),Wk=cm(d,d),Wv=cm(d,d);
  const Q=mm(emb,Wq).map(r=>r.map(v=>+v.toFixed(3)));
  const K=mm(emb,Wk).map(r=>r.map(v=>+v.toFixed(3)));
  const V=mm(emb,Wv).map(r=>r.map(v=>+v.toFixed(3)));
  const KT=K[0].map((_,j)=>K.map(r=>r[j]));
  const raw=mm(Q,KT).map(r=>r.map(v=>+(v/Math.sqrt(d)).toFixed(3)));
  const attn=raw.map(r=>smx(r,temp));
  const out=mm(attn,V).map(r=>r.map(v=>+v.toFixed(3)));
  return{emb,Q,K,V,raw,attn,out};
}

// ====================================================
// MATRIX TABLE RENDERER
// ====================================================
function matHtml(mat,rowLabels,colLabels,color='var(--ac)'){
  const maxCols=Math.min(mat[0].length,6);
  let h=`<table class="mat"><thead><tr><th></th>`;
  for(let j=0;j<maxCols;j++)h+=`<th>${colLabels?colLabels[j]:'d'+j}</th>`;
  if(mat[0].length>maxCols)h+=`<th>…</th>`;
  h+=`</tr></thead><tbody>`;
  mat.forEach((row,i)=>{
    h+=`<tr><td style="color:${color};font-weight:700;white-space:nowrap">${rowLabels?rowLabels[i]:'r'+i}</td>`;
    row.slice(0,maxCols).forEach(v=>{
      const a=Math.min(Math.abs(v)/0.8,1);
      const bg=v>0?`rgba(124,111,255,${a*0.3})`:`rgba(244,63,94,${a*0.25})`;
      h+=`<td style="background:${bg}">${v.toFixed(2)}</td>`;
    });
    if(row.length>maxCols)h+=`<td style="color:var(--mt)">…</td>`;
    h+=`</tr>`;
  });
  return h+`</tbody></table>`;
}

// ====================================================
// HEATMAP RENDERER
// ====================================================
function heatHtml(mat,rowL,colL,cellPx=42,onClickRow=null){
  const n=mat.length,m=mat[0].length;
  const px=Math.min(cellPx,Math.floor(300/m));
  let h=``;
  mat.forEach((row,i)=>{
    row.forEach((v,j)=>{
      const a=Math.pow(v<0?0:v,0.55);
      const r=Math.round(70+185*a),g=Math.round(70+25*a),b=Math.round(110+145*(1-a));
      const txt=v<0?'✗':v.toFixed(2);
      h+=`<div class="hcell" style="width:${px}px;height:${px}px;background:rgba(${r},${g},${b},${0.25+a*0.75});color:${v>0.3?'#fff':'rgba(255,255,255,.45)'};"
        data-r="${i}" data-c="${j}" data-v="${v}"
        onmouseenter="showTip(event,'${rowL?rowL[i]:'r'+i} → ${colL?colL[j]:'c'+j}: ${v<0?'masked':v.toFixed(3)}')"
        onmouseleave="hideTip()"
        ${onClickRow?`onclick="${onClickRow}(${i})"`:''}>
        <span style="font-size:${px<36?'.52rem':'.62rem'}">${txt}</span></div>`;
    });
  });
  return h;
}
function setHmap(id,mat,rowL,colL,cellPx=42,onClickRow=null){
  const el=document.getElementById(id);
  if(!el)return;
  el.style.gridTemplateColumns=`repeat(${mat[0].length},${Math.min(cellPx,Math.floor(300/mat[0].length))}px)`;
  el.innerHTML=heatHtml(mat,rowL,colL,cellPx,onClickRow);
}

// ====================================================
// SCORE BARS
// ====================================================
function sbarsHtml(weights,labels){
  const mx=Math.max(...weights)||1;
  return weights.map((w,i)=>`
    <div class="sbar-row sl"><span class="sbar-tok">${labels[i]}</span>
    <div class="sbar-wrap"><div class="sbar-fill" style="width:${(w/mx*100).toFixed(1)}%"></div></div>
    <span class="sbar-v">${w.toFixed(3)}</span></div>`).join('');
}

// ====================================================
// TOOLTIP
// ====================================================
function showTip(e,txt){const t=document.getElementById('tip');t.textContent=txt;t.style.left=(e.clientX+12)+'px';t.style.top=(e.clientY-30)+'px';t.style.opacity='1';}
function hideTip(){document.getElementById('tip').style.opacity='0';}

// ====================================================
// NAV
// ====================================================
const SECTIONS=['overview','embed','sdpa','single','multi','masked','cross','ffn','encoder','decoder','train'];
function goto(id){
  SECTIONS.forEach(s=>{
    document.getElementById('s-'+s).classList.toggle('active',s===id);
  });
  document.querySelectorAll('.nav-item').forEach(el=>{
    const onclick=el.getAttribute('onclick')||'';
    el.classList.toggle('active',onclick.includes("'"+id+"'"));
  });
  // Trigger render for that section
  const fn={embed:renderPE,sdpa:renderSDPA,single:runSH,multi:runMH,masked:runMasked,cross:runCross,ffn:runFFN,encoder:runEncoder,decoder:runDecoder,train:renderTrain};
  if(fn[id])fn[id]();
}

// ====================================================
// TABS HELPER
// ====================================================
function activateTab(tabClass,panelClass,name){
  document.querySelectorAll('.'+tabClass).forEach(t=>{t.classList.toggle('on',t.textContent.trim()===name||t.dataset.tab===name);});
  document.querySelectorAll('.'+panelClass).forEach(p=>{p.classList.toggle('on',p.dataset.panel===name);});
}
function shTab(n){
  document.querySelectorAll('#s-single .tab').forEach((t,i)=>t.classList.toggle('on',['q','k','v'][i]===n));
  ['q','k','v'].forEach(x=>document.getElementById('sh-tp'+x).classList.toggle('on',x===n));
}
function maskTab(n){
  document.querySelectorAll('#s-train .tab').forEach((t,i)=>t.classList.toggle('on',['pad','causal'][i]===n));
  ['pad','causal'].forEach(x=>document.getElementById('mask-'+x).classList.toggle('on',x===n));
}

// ====================================================
// SECTION: EMBEDDINGS + PE
// ====================================================
function renderPE(){
  const sent=document.getElementById('pe-sent').value;
  const d=parseInt(document.getElementById('pe-dm').value);
  const tkns=toks(sent);
  seedRng(hashStr(tkns.join('')));
  const emb=Array.from({length:tkns.length},()=>Array.from({length:d},()=>+(rn()*0.5).toFixed(3)));
  const pos=tkns.map((_,i)=>pe(i,d).map(v=>+v.toFixed(3)));
  const final=emb.map((row,i)=>row.map((v,j)=>+(v+pos[i][j]).toFixed(3)));
  document.getElementById('pe-emb-tbl').innerHTML=matHtml(emb,tkns,null,'var(--q)');
  document.getElementById('pe-pos-tbl').innerHTML=matHtml(pos,tkns,null,'var(--k)');
  document.getElementById('pe-final-tbl').innerHTML=matHtml(final,tkns,null,'var(--ac2)');
  drawPECanvas(tkns.length,d);
}
function drawPECanvas(n,d){
  const cv=document.getElementById('pe-canvas');if(!cv)return;
  cv.width=cv.offsetWidth||500;cv.height=140;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
  ctx.clearRect(0,0,W,H);
  const cw=W/Math.min(d,20),ch=H/Math.min(n,8);
  for(let i=0;i<Math.min(n,8);i++){
    for(let j=0;j<Math.min(d,20);j++){
      const v=pe(i,Math.min(d,20)*2)[j];
      const a=(v+1)/2;
      const r=Math.round(80+175*a),g=Math.round(80+25*a),b=Math.round(110+145*(1-a));
      ctx.fillStyle=`rgb(${r},${g},${b})`;
      ctx.fillRect(j*cw,i*ch,cw-1,ch-1);
    }
  }
}

// ====================================================
// SECTION: SDPA
// ====================================================
function renderSDPA(){
  const sent=document.getElementById('sdpa-sent').value;
  const dk=parseInt(document.getElementById('sdpa-dk').value);
  const temp=parseFloat(document.getElementById('sdpa-t').value);
  const tkns=toks(sent);
  const{raw,attn}=selfAttn(tkns,dk,temp);
  document.getElementById('sdpa-raw-tbl').innerHTML=matHtml(raw,tkns,tkns,'var(--q)');
  document.getElementById('sdpa-attn-tbl').innerHTML=matHtml(attn,tkns,tkns,'var(--ac2)');
  setHmap('sdpa-hmap',attn,tkns,tkns,44);
  // Animate steps
  const steps=document.querySelectorAll('#sdpa-steps .sitem');
  let idx=0;
  clearInterval(window._sdpaTimer);
  window._sdpaTimer=setInterval(()=>{steps.forEach(s=>s.classList.remove('on'));steps[idx].classList.add('on');idx=(idx+1)%steps.length;},1800);
}

// ====================================================
// SECTION: SINGLE-HEAD
// ====================================================
let shState={},shSel=0,shAnim=null;
const shSentences=['The cat sat on mat','Attention is all you need','I love deep learning','Neural nets learn features','BERT reads both ways'];
function shRandom(){document.getElementById('sh-sent').value=shSentences[Math.floor(Math.random()*shSentences.length)];runSH();}
function runSH(){
  const sent=document.getElementById('sh-sent').value;
  const d=parseInt(document.getElementById('sh-dm').value);
  const temp=parseFloat(document.getElementById('sh-t').value);
  const tkns=toks(sent);
  shState=selfAttn(tkns,d,temp);shState.tkns=tkns;shState.d=d;
  shSel=Math.min(shSel,tkns.length-1);
  renderShTokens(tkns);
  document.getElementById('sh-tpq').innerHTML=matHtml(shState.Q,tkns,null,'var(--q)');
  document.getElementById('sh-tpk').innerHTML=matHtml(shState.K,tkns,null,'var(--k)');
  document.getElementById('sh-tpv').innerHTML=matHtml(shState.V,tkns,null,'var(--v)');
  setHmap('sh-hmap',shState.attn,tkns,tkns,44,'shSelectTok');
  renderShSel(shSel);
  drawFlowCanvas('sh-canvas',shState.attn,tkns,shSel);
  renderShOutput();
}
function renderShTokens(tkns){
  document.getElementById('sh-tokens').innerHTML=tkns.map((t,i)=>`<div class="tok${i===shSel?' on':''}" onclick="shSelectTok(${i})"><span style="color:var(--mt);font-size:.65rem">[${i}]</span> ${t}</div>`).join('');
}
function shSelectTok(i){shSel=i;renderShTokens(shState.tkns);renderShSel(i);drawFlowCanvas('sh-canvas',shState.attn,shState.tkns,i);highlightHmapRow('sh-hmap',i,shState.tkns[0].length||5);}
function renderShSel(i){
  if(!shState.attn)return;
  document.getElementById('sh-sel-lbl').textContent=`"${shState.tkns[i]}" pos ${i}`;
  document.getElementById('sh-sbars').innerHTML=sbarsHtml(shState.attn[i],shState.tkns);
}
function highlightHmapRow(id,rowIdx){
  document.querySelectorAll('#'+id+' .hcell').forEach(c=>{c.style.outline=parseInt(c.dataset.r)===rowIdx?'2px solid var(--ac)':'none';});
}
function renderShOutput(){
  const el=document.getElementById('sh-output');if(!el)return;
  el.innerHTML=shState.tkns.map((t,i)=>{
    const top=shState.attn[i].indexOf(Math.max(...shState.attn[i]));
    return`<div style="margin-bottom:10px"><div style="font-size:.75rem;margin-bottom:3px"><span style="color:var(--v);font-weight:700">${t}</span><span style="color:var(--mt);font-size:.67rem"> → attends to "${shState.tkns[top]}"</span></div>
    <div class="ovec">${shState.out[i].slice(0,8).map(v=>`<div class="odim" style="background:rgba(251,191,36,${Math.min(Math.abs(v)/0.6,0.3)})">${v.toFixed(2)}</div>`).join('')}</div></div>`;
  }).join('');
}

// ====================================================
// FLOW CANVAS (shared)
// ====================================================
let _flowAfId=null,_flowParts=[];
function drawFlowCanvas(canvasId,attn,tkns,focusIdx){
  const cv=document.getElementById(canvasId);if(!cv)return;
  cv.width=cv.offsetWidth||600;cv.height=280;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
  const n=tkns.length,pad=50,xSt=(W-pad*2)/(n-1||1);
  const nodes=tkns.map((t,i)=>({x:pad+i*xSt,label:t.substring(0,5),idx:i}));
  const yT=55,yB=225;
  if(_flowAfId)cancelAnimationFrame(_flowAfId);
  _flowParts=[];
  for(let i=0;i<n;i++){
    if(focusIdx!==undefined&&i!==focusIdx)continue;
    for(let j=0;j<n;j++){
      const w=attn[i][j];
      if(w>0.07)_flowParts.push({from:i,to:j,w,progress:Math.random()});
    }
  }
  function frame(){
    ctx.clearRect(0,0,W,H);
    // Draw arcs
    for(let i=0;i<n;i++){
      if(focusIdx!==undefined&&i!==focusIdx)continue;
      for(let j=0;j<n;j++){
        const w=attn[i][j];if(w<0.02)continue;
        const al=Math.pow(w,0.55);
        ctx.beginPath();ctx.moveTo(nodes[i].x,yT+18);
        const cx=(nodes[i].x+nodes[j].x)/2,cy=(yT+yB)/2-38*Math.sign(j-i)*(i===j?0:1);
        ctx.quadraticCurveTo(cx,cy,nodes[j].x,yB-18);
        const g=ctx.createLinearGradient(nodes[i].x,yT,nodes[j].x,yB);
        g.addColorStop(0,`rgba(124,111,255,${al})`);g.addColorStop(1,`rgba(56,217,169,${al})`);
        ctx.strokeStyle=g;ctx.lineWidth=Math.max(0.4,w*4.5);ctx.stroke();
      }
    }
    // Particles
    _flowParts.forEach(p=>{
      p.progress+=0.009;if(p.progress>1)p.progress=0;
      const fn=nodes[p.from],tn=nodes[p.to],t=p.progress;
      const cx=(fn.x+tn.x)/2,cy=(yT+yB)/2-38*Math.sign(p.to-p.from)*(p.from===p.to?0:1);
      const px=(1-t)*(1-t)*fn.x+2*(1-t)*t*cx+t*t*tn.x;
      const py=(1-t)*(1-t)*(yT+18)+2*(1-t)*t*cy+t*t*(yB-18);
      ctx.beginPath();ctx.arc(px,py,2+p.w*3,0,Math.PI*2);
      ctx.fillStyle=`rgba(255,255,255,${p.w*0.85})`;ctx.fill();
    });
    // Query nodes (top)
    nodes.forEach((nd,i)=>{
      const sel=focusIdx===undefined||i===focusIdx;
      const g=ctx.createRadialGradient(nd.x,yT,2,nd.x,yT,17);
      g.addColorStop(0,sel?'#a78bfa':'#2a2d45');g.addColorStop(1,sel?'#5b4fcf':'#1a1c30');
      ctx.beginPath();ctx.arc(nd.x,yT,17,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
      if(sel){ctx.strokeStyle='#a78bfa';ctx.lineWidth=2;ctx.stroke();}
      ctx.fillStyle='#fff';ctx.font='600 9px Inter';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(nd.label,nd.x,yT);
      ctx.fillStyle='rgba(160,160,200,.5)';ctx.font='8px Inter';ctx.fillText('Q',nd.x,yT-26);
    });
    // Key/Value nodes (bottom)
    nodes.forEach((nd,i)=>{
      const av=focusIdx!==undefined?attn[focusIdx][i]:attn.reduce((s,r)=>s+r[i],0)/n;
      const g=ctx.createRadialGradient(nd.x,yB,2,nd.x,yB,17);
      g.addColorStop(0,`rgba(52,211,153,${0.4+av*0.6})`);g.addColorStop(1,`rgba(16,80,55,${0.4+av*0.6})`);
      ctx.beginPath();ctx.arc(nd.x,yB,17,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
      ctx.strokeStyle=`rgba(52,211,153,${0.3+av*0.65})`;ctx.lineWidth=2;ctx.stroke();
      ctx.fillStyle='#fff';ctx.font='600 9px Inter';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(nd.label,nd.x,yB);
      ctx.fillStyle='rgba(160,200,160,.5)';ctx.font='8px Inter';ctx.fillText('K/V',nd.x,yB+26);
    });
    _flowAfId=requestAnimationFrame(frame);
  }
  frame();
}

// ====================================================
// SECTION: MULTI-HEAD
// ====================================================
let mhState={},mhSelHead=0;
function runMH(){
  const sent=document.getElementById('mh-sent').value;
  const d=parseInt(document.getElementById('mh-dm').value);
  const h=parseInt(document.getElementById('mh-h').value);
  const temp=parseFloat(document.getElementById('mh-t').value);
  const tkns=toks(sent);
  const dk=Math.max(2,Math.floor(d/h));
  // Compute h heads each with dk dimensions
  const heads=Array.from({length:h},(_,hi)=>{
    seedRng(hashStr(tkns.join(''))+hi*137);
    const emb=embed(tkns,dk);
    const Wq=cm(dk,dk),Wk=cm(dk,dk),Wv=cm(dk,dk);
    const Q=mm(emb,Wq),K=mm(emb,Wk),V=mm(emb,Wv);
    const KT=K[0].map((_,j)=>K.map(r=>r[j]));
    const raw=mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(dk)));
    const attn=raw.map(r=>smx(r,temp));
    const out=mm(attn,V);
    return{Q,K,V,attn,out};
  });
  // Final projection
  const concat=tkns.map((_,i)=>heads.flatMap(hd=>hd.out[i]));
  seedRng(hashStr('proj'));
  const Wo=cm(h*dk,d);
  const final=mm(concat,Wo).map(r=>r.map(v=>+v.toFixed(3)));
  mhState={tkns,heads,final,d,h,dk};
  renderMHTokens(tkns);
  renderMHHeads();
  mhSelectHead(mhSelHead<h?mhSelHead:0);
  renderMHOutput(final,tkns);
}
function renderMHTokens(tkns){
  document.getElementById('mh-tokens').innerHTML=tkns.map(t=>`<div class="tok">${t}</div>`).join('');
}
function renderMHHeads(){
  const{heads,tkns,h}=mhState;
  const wrap=document.getElementById('mh-heads');
  wrap.innerHTML=heads.map((hd,hi)=>{
    const cellPx=Math.min(32,Math.floor(160/tkns.length));
    const cells=hd.attn.map(row=>row.map(v=>{
      const a=Math.pow(v,0.55),r=Math.round(70+185*a),g=Math.round(70+25*a),b=Math.round(110+145*(1-a));
      return`<div class="hmc" style="background:rgba(${r},${g},${b},${0.3+a*0.7});width:${cellPx}px"></div>`;
    }).join('')).join('');
    return`<div class="head-box${hi===mhSelHead?' active':''}" onclick="mhSelectHead(${hi})">
      <div class="head-title">Head ${hi}</div>
      <div class="head-mini" style="grid-template-columns:repeat(${tkns.length},${cellPx}px)">${cells}</div>
      <div style="font-size:.62rem;color:var(--mt);margin-top:4px">d_k=${mhState.dk}</div>
    </div>`;
  }).join('');
}
function mhSelectHead(i){
  mhSelHead=i;
  document.querySelectorAll('.head-box').forEach((b,j)=>b.classList.toggle('active',j===i));
  document.getElementById('mh-sel-h').textContent='Head '+i;
  const{heads,tkns}=mhState;
  setHmap('mh-detail-hmap',heads[i].attn,tkns,tkns,44);
  document.getElementById('mh-detail-sbars').innerHTML=sbarsHtml(heads[i].attn[0],tkns);
}
function renderMHOutput(final,tkns){
  const el=document.getElementById('mh-output');if(!el)return;
  el.innerHTML=`<div style="font-size:.72rem;color:var(--mt);margin-bottom:8px">Final output after W_O projection (${final[0].length} dims):</div>`;
  el.innerHTML+=tkns.map((t,i)=>`<div style="margin-bottom:8px"><div style="font-size:.72rem;color:var(--v);font-weight:700;margin-bottom:3px">${t}</div>
    <div class="ovec">${final[i].slice(0,8).map(v=>`<div class="odim">${v.toFixed(2)}</div>`).join('')}</div></div>`).join('');
}

// ====================================================
// SECTION: MASKED ATTENTION
// ====================================================
function runMasked(){
  const sent=document.getElementById('mk-sent').value;
  const d=parseInt(document.getElementById('mk-dm').value);
  const tkns=toks(sent);
  const{raw,attn:unmasked}=selfAttn(tkns,d);
  // Apply causal mask
  const maskedRaw=raw.map((row,i)=>row.map((v,j)=>j>i?-Infinity:v));
  const maskedAttn=maskedRaw.map(row=>{
    const finite=row.map(v=>isFinite(v)?v:-1e9);
    return smx(finite);
  }).map((row,i)=>row.map((v,j)=>j>i?0:v)); // zero out for display
  // Display matrices
  const rawDisp=maskedRaw.map(row=>row.map(v=>isFinite(v)?v:-9.99));
  document.getElementById('mk-raw').innerHTML=matHtml(rawDisp,tkns,tkns,'var(--r)');
  document.getElementById('mk-attn').innerHTML=matHtml(maskedAttn,tkns,tkns,'var(--ac2)');
  setHmap('mk-hmap',maskedAttn,tkns,tkns,46);
}

// ====================================================
// SECTION: CROSS-ATTENTION
// ====================================================
function runCross(){
  const encSent=document.getElementById('ca-enc').value;
  const decSent=document.getElementById('ca-dec').value;
  const d=parseInt(document.getElementById('ca-dm').value);
  const encToks=toks(encSent),decToks=toks(decSent);
  seedRng(hashStr(encSent+decSent));
  const encEmb=embed(encToks,d),decEmb=embed(decToks,d);
  const Wq=cm(d,d),Wk=cm(d,d),Wv=cm(d,d);
  const Q=mm(decEmb,Wq),K=mm(encEmb,Wk),V=mm(encEmb,Wv);
  const KT=K[0].map((_,j)=>K.map(r=>r[j]));
  const raw =mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(d)));
  const attn=raw.map(r=>smx(r));
  // Token bars
  document.getElementById('ca-dec-toks').innerHTML=decToks.map(t=>`<div class="tok">${t}</div>`).join('');
  document.getElementById('ca-enc-toks').innerHTML=encToks.map(t=>`<div class="tok" style="color:var(--k)">${t}</div>`).join('');
  // Heatmap: rows=dec tokens, cols=enc tokens
  const el=document.getElementById('ca-hmap');
  const cellPx=Math.min(44,Math.floor(560/Math.max(encToks.length,1)));
  el.style.gridTemplateColumns=`repeat(${encToks.length},${cellPx}px)`;
  el.innerHTML=heatHtml(attn,decToks,encToks,cellPx);
  document.getElementById('ca-sbars').innerHTML=`<div class="card-title"><div class="dot" style="background:var(--ac2)"></div>Cross-Attention weights (decoder token 0 → encoder)</div>`+sbarsHtml(attn[0],encToks);
}

// ====================================================
// SECTION: FFN
// ====================================================
function runFFN(){
  const d=parseInt(document.getElementById('ffn-dm').value);
  const ff=parseInt(document.getElementById('ffn-ff').value);
  const el=document.getElementById('ffn-vis');
  const x=Array.from({length:d},()=>+(rn()*0.5).toFixed(3));
  const W1=Array.from({length:d},()=>Array.from({length:ff},()=>+(rn()*0.3).toFixed(3)));
  const b1=Array.from({length:ff},()=>+(rn()*0.1).toFixed(3));
  const h1=x.map==undefined?[]:Array.from({length:ff},(_,j)=>Math.max(0,x.reduce((s,v,i)=>s+v*W1[i][j],0)+b1[j]));
  const W2=Array.from({length:ff},()=>Array.from({length:d},()=>+(rn()*0.3).toFixed(3)));
  const b2=Array.from({length:d},()=>+(rn()*0.1).toFixed(3));
  const out=Array.from({length:d},(_,j)=>h1.reduce((s,v,i)=>s+v*W2[i][j],0)+b2[j]);
  const res=x.map((v,i)=>+(v+out[i]).toFixed(3));
  const mean=res.reduce((a,b)=>a+b,0)/res.length;
  const std=Math.sqrt(res.reduce((s,v)=>s+(v-mean)**2,0)/res.length)||1;
  const ln=res.map(v=>+((v-mean)/std).toFixed(3));
  el.innerHTML=`
    <div style="font-size:.72rem;color:var(--mt);margin-bottom:6px">Input x (${d} dims):</div>
    <div class="ovec">${x.map(v=>`<div class="odim" style="color:var(--q)">${v.toFixed(2)}</div>`).join('')}</div>
    <div style="font-size:.72rem;color:var(--mt);margin:6px 0 4px">After FFN (${ff}→${d}):</div>
    <div class="ovec">${out.map(v=>`<div class="odim" style="color:var(--ac3)">${v.toFixed(2)}</div>`).join('')}</div>`;
  document.getElementById('ffn-ln-vis').innerHTML=`
    <div style="font-size:.72rem;color:var(--mt);margin-bottom:6px">Residual x + FFN(x):</div>
    <div class="ovec">${res.map(v=>`<div class="odim" style="color:var(--ac)">${v.toFixed(2)}</div>`).join('')}</div>
    <div style="font-size:.72rem;color:var(--mt);margin:6px 0 4px">After LayerNorm (μ=${mean.toFixed(2)}, σ=${std.toFixed(2)}):</div>
    <div class="ovec">${ln.map(v=>`<div class="odim" style="color:var(--ac2)">${v.toFixed(2)}</div>`).join('')}</div>`;
}

// ====================================================
// SECTION: ENCODER
// ====================================================
function runEncoder(){
  const sent=document.getElementById('enc-sent').value;
  const nLayers=parseInt(document.getElementById('enc-l').value);
  const nHeads=parseInt(document.getElementById('enc-h').value);
  const d=8,temp=1;
  const tkns=toks(sent);
  const vis=document.getElementById('enc-layer-vis');
  const norms=[];
  let repr=embed(tkns,d);
  let html='';
  for(let l=0;l<nLayers;l++){
    seedRng(hashStr(tkns.join(''))+l*211);
    const dk=Math.max(2,Math.floor(d/nHeads));
    const heads=Array.from({length:nHeads},(_,hi)=>{
      seedRng(hashStr(tkns.join(''))+l*211+hi*37);
      const Wq=cm(d,dk),Wk=cm(d,dk),Wv=cm(d,dk);
      const Q=mm(repr,Wq),K=mm(repr,Wk),V=mm(repr,Wv);
      const KT=K[0].map((_,j)=>K.map(r=>r[j]));
      const raw=mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(dk)));
      const attn=raw.map(r=>smx(r,temp));
      return{attn,out:mm(attn,V)};
    });
    // Avg attention for display
    const attnAvg=tkns.map((_,i)=>tkns.map((_,j)=>+(heads.reduce((s,h)=>s+h.attn[i][j],0)/nHeads).toFixed(3)));
    const norm=repr.map(r=>{const m=r.reduce((a,b)=>a+b,0)/r.length;const s=Math.sqrt(r.reduce((a,v)=>a+(v-m)**2,0)/r.length)||1;return r.map(v=>+((v-m)/s).toFixed(3));});
    repr=norm;
    const avgNorm=norm.reduce((s,r)=>s+r.reduce((a,b)=>a+Math.abs(b),0)/r.length,0)/norm.length;
    norms.push(avgNorm);
    html+=`<div style="margin-bottom:14px">
      <div style="font-size:.72rem;color:var(--ac);font-weight:700;margin-bottom:6px">Layer ${l+1} — Avg attention (${nHeads} head${nHeads>1?'s':''})</div>
      <div class="hmap" style="grid-template-columns:repeat(${tkns.length},40px)">${heatHtml(attnAvg,tkns,tkns,40)}</div>
    </div>`;
  }
  vis.innerHTML=html;
  drawNormCanvas(norms);
}
function drawNormCanvas(norms){
  const cv=document.getElementById('enc-canvas');if(!cv)return;
  cv.width=cv.offsetWidth||600;cv.height=180;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height,n=norms.length;
  ctx.clearRect(0,0,W,H);
  const mx=Math.max(...norms)*1.1||1;
  const xs=Array.from({length:n},(_,i)=>60+i*(W-80)/(n-1||1));
  ctx.beginPath();ctx.strokeStyle='var(--bd)';
  for(let i=0;i<=4;i++){const y=H-20-(H-40)*i/4;ctx.moveTo(40,y);ctx.lineTo(W-10,y);}
  ctx.stroke();
  ctx.beginPath();ctx.strokeStyle='rgba(124,111,255,.8)';ctx.lineWidth=2;
  xs.forEach((x,i)=>{const y=H-20-(H-40)*(norms[i]/mx);i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);});
  ctx.stroke();
  xs.forEach((x,i)=>{
    const y=H-20-(H-40)*(norms[i]/mx);
    ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.fillStyle='var(--ac)';ctx.fill();
    ctx.fillStyle='var(--tx)';ctx.font='10px Inter';ctx.textAlign='center';
    ctx.fillText('L'+(i+1),x,H-5);ctx.fillText(norms[i].toFixed(2),x,y-10);
  });
}

// ====================================================
// SECTION: DECODER
// ====================================================
function runDecoder(){
  const encSent=document.getElementById('dec-enc').value;
  const decSent=document.getElementById('dec-dec').value;
  const d=8,temp=1;
  const encToks=toks(encSent),decToks=toks(decSent);
  // 1. Masked self-attention
  const{attn:selfAttnW}=selfAttn(decToks,d);
  const masked=selfAttnW.map((row,i)=>row.map((v,j)=>j>i?0:v));
  // 2. Cross-attention
  seedRng(hashStr(encSent+decSent));
  const encEmb=embed(encToks,d),decEmb=embed(decToks,d);
  const Wq=cm(d,d),Wk=cm(d,d),Wv=cm(d,d);
  const Q=mm(decEmb,Wq),K=mm(encEmb,Wk),V=mm(encEmb,Wv);
  const KT=K[0].map((_,j)=>K.map(r=>r[j]));
  const crossRaw=mm(Q,KT).map(r=>r.map(v=>v/Math.sqrt(d)));
  const crossAttn=crossRaw.map(r=>smx(r));
  // 3. FFN output
  const out=crossAttn.map((row,i)=>{
    const v=V.map(r=>r[i]);
    return row.reduce((s,w,j)=>s.map((x,k)=>x+w*V[j][k]),Array(d).fill(0)).map(x=>+x.toFixed(3));
  });
  setHmap('dec-masked-hmap',masked,decToks,decToks,44);
  const el=document.getElementById('dec-cross-hmap');
  const cellPx=Math.min(44,Math.floor(300/Math.max(encToks.length,1)));
  el.style.gridTemplateColumns=`repeat(${encToks.length},${cellPx}px)`;
  el.innerHTML=heatHtml(crossAttn,decToks,encToks,cellPx);
  const fEl=document.getElementById('dec-ffn-out');
  fEl.innerHTML=decToks.map((t,i)=>`<div style="margin-bottom:8px"><div style="font-size:.72rem;color:var(--ac2);font-weight:700">${t}</div>
    <div class="ovec">${out[i].slice(0,6).map(v=>`<div class="odim">${v.toFixed(2)}</div>`).join('')}</div></div>`).join('');
}

// ====================================================
// SECTION: TRAINING
// ====================================================
function renderTrain(){
  renderLoss();
  renderPadMask();
  renderCausalMask();
  renderTrainConcepts();
}
function renderLoss(){
  const conf=parseFloat(document.getElementById('tr-conf').value);
  const cv=document.getElementById('loss-canvas');if(!cv)return;
  cv.width=cv.offsetWidth||500;cv.height=160;
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
  ctx.clearRect(0,0,W,H);
  const xs=Array.from({length:100},(_,i)=>0.01+i*0.0098);
  const ys=xs.map(x=>-Math.log(x));
  const mx=Math.max(...ys.slice(0,50));
  // Grid
  ctx.strokeStyle='rgba(255,255,255,.06)';ctx.lineWidth=1;
  for(let i=0;i<=4;i++){ctx.beginPath();ctx.moveTo(40,10+i*(H-20)/4);ctx.lineTo(W-10,10+i*(H-20)/4);ctx.stroke();}
  // Curve
  ctx.beginPath();ctx.strokeStyle='rgba(124,111,255,.7)';ctx.lineWidth=2.5;
  xs.forEach((x,i)=>{const px=40+i*(W-50)/99,py=H-10-(H-20)*Math.min(ys[i]/mx,1);i===0?ctx.moveTo(px,py):ctx.lineTo(px,py);});
  ctx.stroke();
  // Current point
  const curX=40+(conf-0.01)/(0.99-0.01)*(W-50);
  const curY=H-10-(H-20)*Math.min(-Math.log(conf)/mx,1);
  ctx.beginPath();ctx.arc(curX,curY,6,0,Math.PI*2);ctx.fillStyle='var(--ac3)';ctx.fill();
  ctx.fillStyle='var(--tx)';ctx.font='11px Inter';ctx.textAlign='center';ctx.fillText(`conf=${conf.toFixed(2)} → loss=${(-Math.log(conf)).toFixed(3)}`,curX,curY-14);
  ctx.fillStyle='rgba(124,111,255,.15)';ctx.fillRect(40,curY,curX-40,H-10-curY);
}
function renderPadMask(){
  const n=5,padIdx=4;
  const mat=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>j===padIdx?-1:1));
  const el=document.getElementById('pad-hmap');
  el.style.gridTemplateColumns=`repeat(${n},44px)`;
  const labels=['The','cat','sat','on','[PAD]'];
  el.innerHTML=mat.map((row,i)=>row.map((v,j)=>{
    const c=v<0?'rgba(244,63,94,.7)':'rgba(52,211,153,.5)';
    return`<div class="hcell" style="width:44px;height:44px;background:${c};color:#fff">${v<0?'×':'✓'}</div>`;
  }).join('')).join('');
}
function renderCausalMask(){
  const n=5;
  const mat=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>j<=i?1:-1));
  const el=document.getElementById('causal-hmap');
  el.style.gridTemplateColumns=`repeat(${n},44px)`;
  el.innerHTML=mat.map(row=>row.map(v=>`<div class="hcell" style="width:44px;height:44px;background:${v>0?'rgba(124,111,255,.6)':'rgba(244,63,94,.4)'};color:#fff">${v>0?'✓':'×'}</div>`).join('')).join('');
}
function renderTrainConcepts(){
  const el=document.getElementById('train-concepts');if(!el)return;
  const items=[
    {icon:'📉',name:'Learning Rate',desc:'~1e-4 with warmup + decay'},
    {icon:'🎲',name:'Dropout',desc:'0.1 on attention & FFN'},
    {icon:'🔢',name:'Batch Size',desc:'Tokens per batch ~4096'},
    {icon:'🔥',name:'Warmup Steps',desc:'4000 steps linear ramp'},
    {icon:'⚖️',name:'Weight Decay',desc:'L2 regularisation 0.01'},
    {icon:'✂️',name:'Gradient Clip',desc:'Max norm 1.0'},
  ];
  el.innerHTML=items.map(it=>`<div class="concept-card"><div class="icon">${it.icon}</div><h4>${it.name}</h4><p>${it.desc}</p></div>`).join('');
}

// ====================================================
// OVERVIEW CONCEPTS
// ====================================================
function renderOverviewConcepts(){
  const el=document.getElementById('concept-grid');if(!el)return;
  const items=[
    {icon:'🔤',name:'Embeddings + PE',desc:'Position-aware token vectors',sec:'embed'},
    {icon:'🎯',name:'Scaled Dot-Product',desc:'QKᵀ/√dk attention',sec:'sdpa'},
    {icon:'👁️',name:'Single-Head',desc:'One attention pattern',sec:'single'},
    {icon:'🧠',name:'Multi-Head',desc:'h parallel attention heads',sec:'multi'},
    {icon:'🔒',name:'Masked Attention',desc:'Causal, no future peek',sec:'masked'},
    {icon:'🔗',name:'Cross-Attention',desc:'Encoder→Decoder bridge',sec:'cross'},
    {icon:'⚙️',name:'FFN + LayerNorm',desc:'Per-token MLP + residual',sec:'ffn'},
    {icon:'📥',name:'Encoder',desc:'Bidirectional context',sec:'encoder'},
    {icon:'📤',name:'Decoder',desc:'Autoregressive generation',sec:'decoder'},
    {icon:'📈',name:'Training',desc:'Loss, masking, teacher forcing',sec:'train'},
  ];
  el.innerHTML=items.map(it=>`<div class="concept-card" onclick="goto('${it.sec}')"><div class="icon">${it.icon}</div><h4>${it.name}</h4><p>${it.desc}</p></div>`).join('');
}

// ====================================================
// INIT
// ====================================================
window.addEventListener('resize',()=>{
  if(document.getElementById('s-single').classList.contains('active'))drawFlowCanvas('sh-canvas',shState.attn,shState.tkns,shSel);
  if(document.getElementById('s-embed').classList.contains('active'))renderPE();
  if(document.getElementById('s-train').classList.contains('active'))renderLoss();
  if(document.getElementById('s-encoder').classList.contains('active'))drawNormCanvas&&runEncoder();
});
renderOverviewConcepts();
renderPE();
renderSDPA();
runSH();
runMH();
runMasked();
runCross();
runFFN();
renderTrain();
</script>
</body>
</html>
"""

with open('transformer_complete.html', 'ab') as f:
    f.write(js.encode('utf-8'))
print('done, total:', len(open('transformer_complete.html','rb').read()), 'bytes')



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: fix_html_chars.py
# Pass-1 broken-char fixer (U+FFFD replacement chars → HTML entities)


# ══════════════════════════════════════════════════════════════════════════════

# fix_html_chars.py
# Fixes all corrupted/missing characters (U+FFFD replacement chars) in index.html

REPL = '\ufffd'  # Unicode replacement character (the '?' shown in browser)

with open('index.html', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-8', errors='replace')

fixes = [
    # ── Title ──────────────────────────────────────────────────────────────────
    (f'Transformer Architecture {REPL} Complete Interactive Guide',
     'Transformer Architecture &#8212; Complete Interactive Guide'),

    # ── Overview section ───────────────────────────────────────────────────────
    (f'relies entirely on attention {REPL} no recurrence, no convolutions',
     'relies entirely on attention &#8212; no recurrence, no convolutions'),

    # Decoder pathway arch block — Enc→Dec
    (f'Cross-Attention (Enc{REPL}Dec)',
     'Cross-Attention (Enc&#8594;Dec)'),

    # Linear + Softmax → Token
    (f'Linear + Softmax {REPL} Token',
     'Linear + Softmax &#8594; Token'),

    # ── Embeddings + PE ────────────────────────────────────────────────────────
    # PE Heatmap (positions × dims)
    (f'PE Heatmap (positions {REPL} dims)',
     'PE Heatmap (positions &times; dims)'),

    # ── Scaled Dot-Product (SDPA) section ─────────────────────────────────────
    # Step 1: Q · Kᵀ
    (f'Dot Product: Q {REPL} K{REPL}',
     'Dot Product: Q &middot; K&#7488;'),

    # Step 2: scale by √d_k  (shows as "vd_k" with the √ missing)
    # The √ was encoded wrong -> fix both the step description and any formula
    ('Scale by vd_k',
     'Scale by &radic;d_k'),

    # Step 3: -∞ masking
    ('future positions are masked with -8',
     'future positions are masked with -&infin;'),

    # Step 4: Softmax → Attention Weights
    (f'Softmax {REPL} Attention Weights',
     'Softmax &#8594; Attention Weights'),

    # Step 5: attn · V
    (f'attn {REPL} V',
     'attn &middot; V'),

    # Main SDPA formula:  softmax(QKᵀ / √d_k) · V
    (f'softmax<span class="ha">(</span><span class="hq">Q</span><span class="hk">K{REPL}</span> / vd_k<span class="ha">)</span> {REPL} <span class="hv">V</span>',
     'softmax<span class="ha">(</span><span class="hq">Q</span><span class="hk">K&#7488;</span> / &radic;d_k<span class="ha">)</span> &middot; <span class="hv">V</span>'),

    # Card title: Interactive Q·Kᵀ Score Matrix
    (f'Interactive Q{REPL}K{REPL} Score Matrix',
     'Interactive Q&middot;K&#7488; Score Matrix'),

    # ── Single-Head section ────────────────────────────────────────────────────
    # Description: three vectors — Query, Key, Value
    (f'three vectors {REPL} <span',
     'three vectors &#8212; <span'),

    # ▶ Run button
    (f'<button class="btn btn-p" onclick="runSH()">{REPL} Run</button>',
     '<button class="btn btn-p" onclick="runSH()">&#9654; Run</button>'),

    # 🎲 Random button  (two ? = two replacement chars from multi-byte emoji)
    (f'<button class="btn btn-s" onclick="shRandom()">{REPL}{REPL} Random</button>',
     '<button class="btn btn-s" onclick="shRandom()">&#127922; Random</button>'),

    # Score Bars — [0]
    (f'Score Bars {REPL} <span',
     'Score Bars &#8212; <span'),

    # ── Multi-Head section ─────────────────────────────────────────────────────
    # ▶ Run button mh
    (f'<button class="btn btn-p" onclick="runMH()">{REPL} Run</button>',
     '<button class="btn btn-p" onclick="runMH()">&#9654; Run</button>'),

    # All Heads — Attention Heatmaps
    (f'All Heads {REPL} Attention Heatmaps',
     'All Heads &#8212; Attention Heatmaps'),

    # MultiHead formula: Concat(head1,…,headₕ) · W_O
    # MultiHead(Q,K,V) = Concat(head1,…,head?) · W_O
    (f'Concat(head1,\u2026,head{REPL}) {REPL} <strong>W_O</strong>',
     'Concat(head&#8321;,&hellip;,head&#8341;) &middot; <strong>W_O</strong>'),

    # ── Masked Attention section ───────────────────────────────────────────────
    # causal mask description uses -∞
    ('we apply a <b>causal mask</b> by setting future scores to -8 before softmax',
     'we apply a <b>causal mask</b> by setting future scores to -&infin; before softmax'),

    # Raw Scores label
    ('Raw Scores (masked future = -8)',
     'Raw Scores (masked future = -&infin;)'),

    # ── Cross-Attention section ────────────────────────────────────────────────
    # badge: Encoder→Decoder
    (f'<span class="badge">Encoder{REPL}Decoder</span>',
     '<span class="badge">Encoder&#8594;Decoder</span>'),

    # heatmap label: decoder rows → encoder cols
    (f'Cross-Attention Heatmap (decoder rows {REPL} encoder cols)',
     'Cross-Attention Heatmap (decoder rows &#8594; encoder cols)'),

    # ── FFN + LayerNorm section ────────────────────────────────────────────────
    # FFN formula: max(0, x·W1 + b1)·W2 + b2
    (f'FFN(x) = max(0, x{REPL}W1 + b1){REPL}W2 + b2',
     'FFN(x) = max(0, x&middot;W1 + b1)&middot;W2 + b2'),

    # LayerNorm formula: γ · (x − μ)/σ + β
    (f'LayerNorm(x) = {REPL} {REPL} (x - {REPL})/s + {REPL}',
     'LayerNorm(x) = &gamma; &middot; (x - &mu;)/&sigma; + &beta;'),

    # ── Training section ───────────────────────────────────────────────────────
    # Loss formula: L = -Σ y_true · log(softmax(logits))
    (f'L = -S y_true {REPL} log(softmax(logits))',
     'L = -&Sigma; y_true &middot; log(softmax(logits))'),

    # Padding mask -∞
    ('Attention to PAD positions is blocked by setting scores to -8.',
     'Attention to PAD positions is blocked by setting scores to -&infin;.'),

    # Causal mask description 0…i
    (f'position i can only attend to positions 0{REPL}i',
     'position i can only attend to positions 0&hellip;i'),

    # ── Encoder section ────────────────────────────────────────────────────────
    # ▶ Run Encoder button
    (f'<button class="btn btn-p" onclick="runEncoder()">{REPL} Run Encoder</button>',
     '<button class="btn btn-p" onclick="runEncoder()">&#9654; Run Encoder</button>'),

    # Encoder description arrow
    ('Multi-Head Self-Attention',
     'Multi-Head Self-Attention'),  # no change needed, already fine

    # ── Decoder section ────────────────────────────────────────────────────────
    # ▶ Run button decoder
    (f'<button class="btn btn-p" onclick="runDecoder()">{REPL} Run</button>',
     '<button class="btn btn-p" onclick="runDecoder()">&#9654; Run</button>'),

    # ── FFN run button ─────────────────────────────────────────────────────────
    (f'<button class="btn btn-p" onclick="runFFN()">{REPL} Run</button>',
     '<button class="btn btn-p" onclick="runFFN()">&#9654; Run</button>'),
]

count = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed: {repr(old[:60])}')
        count += 1
    else:
        print(f'NOT FOUND: {repr(old[:60])}')

# Now fix any remaining lone REPL characters that weren't caught above
# by scanning and reporting them so we know what's left
remaining = [(i, content[max(0,i-30):i+30]) for i in range(len(content)) if content[i] == REPL]
if remaining:
    print(f'\n{len(remaining)} remaining replacement chars:')
    for pos, ctx in remaining:
        print(f'  pos {pos}: ...{repr(ctx)}...')
else:
    print('\nNo remaining replacement characters! All fixed.')

# Fix the triple \r\r\r\n line endings → normal \r\n
content = content.replace('\r\r\r\n', '\r\n')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone. Applied {count} fixes. Saved index.html ({len(content.encode())} bytes)')



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: fix_final.py
# Pass-2 broken-char fixer (raw byte analysis, targeted replacements)


# ══════════════════════════════════════════════════════════════════════════════

# fix_final.py  –  fix all 16 corrupted chars in index.html
# Reads the file as bytes, decodes with replacement, applies targeted fixes, saves as UTF-8.

with open('index.html', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-8', errors='replace')
R = '\ufffd'   # the replacement char we are hunting

# --------------------------------------------------------------------------
# Each tuple: (exact_old_string, new_string)
# We match the MINIMAL context around each ? so each pattern is unique.
# --------------------------------------------------------------------------
fixes = [
    # pos 17316 – "Dot Product: Q ? K?" inside <h4>
    (
        f'<h4>Dot Product: Q {R} K{R}</h4>',
        '<h4>Dot Product: Q &middot; K<sup>T</sup></h4>'
    ),

    # pos 17425 – "Shape: (n ? n)"
    (
        f'Shape: (n {R} n).',
        'Shape: (n &times; n).'
    ),

    # pos 18682 – formula:  K? / vd_k) ? V  (K^T and the bullet)
    # The formula card reads:  ...K?</span> / vd_k<span...>) ? <span...>V</span>
    (
        f'<span class="hk">K{R}</span> / vd_k<span class="ha">)</span> {R} <span class="hv">V</span>',
        '<span class="hk">K<sup>T</sup></span> / &radic;d_k<span class="ha">)</span> &middot; <span class="hv">V</span>'
    ),

    # pos 18867 – card title: Interactive Q?K?
    (
        f'Interactive Q{R}K{R} Score Matrix',
        'Interactive Q&middot;K<sup>T</sup> Score Matrix'
    ),

    # pos 20472 – single-head description:  "Value ? by projecting"
    (
        f'</span> {R} by projecting its embedding',
        '</span> &#8212; by projecting its embedding'
    ),

    # pos 25164 – card title: "Selected Head Detail ?"
    (
        f'Selected Head Detail {R} <span',
        'Selected Head Detail &#8212; <span'
    ),

    # pos 25636 + 25645 – MultiHead formula:  Concat(head1,?,head?) ? W_O
    # The two ?s are: the ellipsis between head1 and headN, and the · bullet
    (
        f'Concat(head1,{R},head{R}) {R} <strong>W_O</strong>',
        'Concat(head<sub>1</sub>,&hellip;,head<sub>h</sub>) &middot; <strong>W_O</strong>'
    ),

    # pos 27657 – masked attention info box:  "position 3 ? leaking future labels"
    (
        f'position 3 {R} leaking future labels',
        'position 3 &#8212; leaking future labels'
    ),

    # pos 30802 – FFN formula card:  "d_ff = 4 ? d_model"
    (
        f'd_ff = 4 {R} d_model',
        'd_ff = 4 &times; d_model'
    ),

    # pos 31030 – FFN info box:  "4? larger than d_model"
    (
        f'typically 4{R} larger than d_model',
        'typically 4&times; larger than d_model'
    ),

    # pos 31935/31942/31949 – LayerNorm formula:  "= ? ? (x - ?)/s + ?"
    # γ · (x - μ)/σ + β
    (
        f'LayerNorm(x) = {R} {R} (x - {R})/s + {R}',
        'LayerNorm(x) = &gamma; &middot; (x - &mu;)/&sigma; + &beta;'
    ),

    # pos 34293 – decoder description:  "(3) FFN ? each followed"
    (
        f'(3) FFN {R} each followed',
        '(3) FFN &#8212; each followed'
    ),

    # pos 36259 – training info:  "decoder input ? not the model's prediction"
    (
        f"decoder input {R} not the model",
        "decoder input &#8212; not the model"
    ),
]

# --------------------------------------------------------------------------
# Also fix the two text strings that use plain digits/letters instead of
# proper symbols (no-? issues but wrong nonetheless from the original):
# --------------------------------------------------------------------------
extra_fixes = [
    # "vd_k" (√d_k rendered as plain text) in SDPA step 2
    (
        '<h4>Scale by vd_k</h4>',
        '<h4>Scale by &radic;d<sub>k</sub></h4>'
    ),
    # "-8" in masked attention description (should be -∞)
    (
        'setting future scores to -8 before softmax',
        'setting future scores to -&infin; before softmax'
    ),
    # Raw Scores label
    (
        'Raw Scores (masked future = -8)',
        'Raw Scores (masked future = -&infin;)'
    ),
    # Padding mask info
    (
        'Attention to PAD positions is blocked by setting scores to -8.',
        'Attention to PAD positions is blocked by setting scores to -&infin;.'
    ),
    # Masked Attention description: "setting future scores to … we cannot"
    (
        'masked with -8 so the model',
        'masked with -&infin; so the model'
    ),
    # Softmax arrow step 4 (was rendered with unicode replacement in original but
    # already shows as literal → in some encodings; ensure it's an entity)
    # In step 4 the text "Softmax → Attention Weights" already uses →, leave as is.
]

applied = 0
for old, new in fixes + extra_fixes:
    if old in content:
        content = content.replace(old, new)
        print(f'[OK] Fixed: {repr(old[:70])}')
        applied += 1
    else:
        print(f'[--] Not found: {repr(old[:70])}')

# Clean up triple-carriage-return line endings (\r\r\r\n → \r\n)
content = content.replace('\r\r\r\n', '\r\n')

# Check remaining replacement chars
remaining = [i for i, c in enumerate(content) if c == R]
print(f'\nApplied {applied} fixes.')
print(f'Remaining U+FFFD chars: {len(remaining)}')
if remaining:
    for p in remaining:
        ctx = content[max(0,p-40):min(len(content),p+40)].replace('\r','').replace('\n','')
        print(f'  still at pos {p}: {repr(ctx)}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nSaved index.html  ({len(content.encode())} bytes)')



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: fix_remaining.py
# Pass-3 broken-char fixer (byte-level, LayerNorm Greek letters etc.)


# ══════════════════════════════════════════════════════════════════════════════

# fix_remaining.py – fixes the remaining 8 corruption chars in index.html
# based on raw byte analysis

with open('index.html', 'rb') as f:
    content_bytes = f.read()

# We'll work on raw bytes to do surgical replacements, then write as UTF-8 text
# REPL char bytes
R_bytes = b'\xef\xbf\xbd'     # U+FFFD

# Each fix: (old_bytes, new_bytes)
# We target the minimal unique byte sequence around each bad spot.
byte_fixes = [
    # ------------------------------------------------------------------
    # pos 17092:  "Dot Product: Q [REPL] K?" inside <h4>
    # raw: ... 51 20 ef bf bd 20 4b 3f 3c 2f 68 34 3e ...
    #          Q  sp  REPL     sp  K  ?  </h4>
    (
        b'Dot Product: Q ' + R_bytes + b' K?</h4>',
        b'Dot Product: Q &middot; K<sup>T</sup></h4>'
    ),

    # ------------------------------------------------------------------
    # pos 18455 (in formula):   )/span> [REPL] <span class="hv">V
    # This is the  ·  bullet between softmax(...) and V
    # raw: ... 3e 29 3c 2f 73 70 61 6e 3e 20 ef bf bd 20 3c 73 70 61 6e 20 63 6c 61 73 73 ...
    #          > )  <  /  s  p  a  n  >  sp REPL     sp <  s  p  a  n  sp c  l  a  s  s
    (
        b')</span> ' + R_bytes + b' <span class="hv">V</span>',
        b')</span> &middot; <span class="hv">V</span>'
    ),

    # ------------------------------------------------------------------
    # pos 18636: "Interactive Q[REPL]K? Score Matrix"
    # raw: ... 51 ef bf bd 4b 3f 20 53 63 6f 72 65 ...
    #          Q  REPL      K  ?  sp S  c  o  r  e
    (
        b'Interactive Q' + R_bytes + b'K? Score Matrix',
        b'Interactive Q&middot;K<sup>T</sup> Score Matrix'
    ),

    # ------------------------------------------------------------------
    # pos 25325+25334: Concat(head1,[REPL],head?) [REPL] <strong>W_O
    # raw at 25325: ... 28 68 65 61 64 31 2c ef bf bd 2c 68 65 61 64 3f 29 20 ef bf bd 20 3c 73 74 72 6f 6e 67 ...
    #              (   h  e  a  d  1  ,  REPL          ,  h  e  a  d  ?  )  sp REPL     sp <  s  t  r  o  n  g
    (
        b'Concat(head1,' + R_bytes + b',head?) ' + R_bytes + b' <strong>W_O</strong>',
        b'Concat(head<sub>1</sub>,&hellip;,head<sub>h</sub>) &middot; <strong>W_O</strong>'
    ),

    # ------------------------------------------------------------------
    # pos 31568/75/82: LayerNorm(x) = ? [REPL] (x - [REPL])/s + [REPL]
    # raw: ... 3d 20 3f 20 ef bf bd 20 28 78 20 2d 20 ef bf bd 29 2f 73 20 2b 20 ef bf bd ...
    #          =  sp ?  sp REPL     sp (  x  sp -  sp REPL     )  /  s  sp +  sp REPL
    # The '?' here is a LITERAL question mark (0x3f) = the γ that got mangled
    (
        b'LayerNorm(x) = ? ' + R_bytes + b' (x - ' + R_bytes + b')/s + ' + R_bytes,
        b'LayerNorm(x) = &gamma; &middot; (x - &mu;)/&sigma; + &beta;'
    ),
]

out = content_bytes
applied = 0
for old, new in byte_fixes:
    if old in out:
        out = out.replace(old, new)
        print(f'[OK] Fixed bytes: {repr(old[:50])}')
        applied += 1
    else:
        print(f'[--] Not found: {repr(old[:50])}')

# Also fix remaining plain-text issues (no-encoding but wrong content)
text = out.decode('utf-8', errors='replace')

text_fixes = [
    # vd_k  → √d_k  (appears in SDPA formula and step 2)
    ('<h4>Scale by vd_k</h4>',
     '<h4>Scale by &radic;d<sub>k</sub></h4>'),

    # Also appears in formula: / vd_k
    ('/ vd_k<span',
     '/ &radic;d<sub>k</sub><span'),

    # -8 → -∞  (masking descriptions)
    ('set future scores to -8.',
     'set future scores to -&infin;.'),
    ('future scores to -8 before softmax',
     'future scores to -&infin; before softmax'),
    ('setting scores to -8.',
     'setting scores to -&infin;.'),
    ('masked with -8 so the model',
     'masked with -&infin; so the model'),
    ('masked future = -8)',
     'masked future = -&infin;)'),
]

for old, new in text_fixes:
    if old in text:
        text = text.replace(old, new)
        print(f'[OK] Text fix: {repr(old[:60])}')
        applied += 1
    else:
        print(f'[--] Not found (text): {repr(old[:60])}')

# Remaining check
R = '\ufffd'
still = [(i, text[max(0,i-30):i+30].replace('\r','').replace('\n',''))
         for i, c in enumerate(text) if c == R]
print(f'\nApplied {applied} fixes total.')
print(f'Remaining replacement chars: {len(still)}')
for p, ctx in still:
    print(f'  pos {p}: {repr(ctx)}')

# Normalise line endings
text = text.replace('\r\r\r\n', '\r\n').replace('\r\r\n', '\r\n')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print(f'\nSaved index.html ({len(text.encode())} bytes)')



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: fix_plain_question_marks.py
# Pass-4 broken-char fixer (literal ? bytes — buttons, arrows, KT formula)


# ══════════════════════════════════════════════════════════════════════════════

# fix_plain_question_marks.py
# Fixes remaining plain '?' (ASCII 0x3f) that are really broken symbols,
# plus the emoji-button issue (emoji bytes that got corrupted)
# Works on the raw bytes for precision.

with open('index.html', 'rb') as f:
    raw = f.read()

R = b'\xef\xbf\xbd'   # U+FFFD (should be 0 remaining after previous scripts)

# ─── PLAIN ASCII '?' fixes (0x3f in wrong places) ─────────────────────────
# These are places where an emoji or special char became a literal '?'
# We match by surrounding context (bytes).

byte_fixes = [
    # ── Overview: "Enc?Dec" arrow ──────────────────────────────────────────
    # <div ...>Cross-Attention (Enc?Dec)</div>
    (b'Cross-Attention (Enc?Dec)', b'Cross-Attention (Enc&#8594;Dec)'),

    # ── Overview arch block: "Softmax ? Token" ────────────────────────────
    (b'Linear + Softmax ? Token', b'Linear + Softmax &#8594; Token'),

    # ── SDPA: step 4 "Softmax ? Attention Weights" ────────────────────────
    (b'Softmax ? Attention Weights', b'Softmax &#8594; Attention Weights'),

    # ── SDPA formula: K? (Kᵀ) inside hk span - the remaining ? after K ───
    # The context is:  <span class="hk">K?</span>
    (b'<span class="hk">K?</span>', b'<span class="hk">K<sup>T</sup></span>'),

    # ── SDPA score matrix title Q?K? ──────────────────────────────────────
    # Already partially fixed to Q&middot;K? → fix the trailing ?
    (b'K<sup>T</sup> Score Matrix',  b'K<sup>T</sup> Score Matrix'),  # already good, skip
    # In case it still shows Q?K?:
    (b'Q?K? Score Matrix', b'Q&middot;K<sup>T</sup> Score Matrix'),

    # ── Single-Head Run button emoji (▶)  ─────────────────────────────────
    # The emoji ▶ (U+25B6) in UTF-8 is 0xE2 0x96 0xB6
    # It got stored as literal '?' which we need to detect from context
    (b'onclick="runSH()">? Run<', b'onclick="runSH()">&#9654; Run<'),

    # ── Single-Head Random button (🎲) ────────────────────────────────────
    # 🎲 = U+1F3B2, UTF-8: F0 9F 8E B2
    # showed as two ?s:
    (b'onclick="shRandom()">?? Random<', b'onclick="shRandom()">&#127922; Random<'),

    # ── Multi-Head Run button ─────────────────────────────────────────────
    (b'onclick="runMH()">? Run<', b'onclick="runMH()">&#9654; Run<'),

    # ── FFN Run button ────────────────────────────────────────────────────
    (b'onclick="runFFN()">? Run<', b'onclick="runFFN()">&#9654; Run<'),

    # ── Encoder Run Encoder button ────────────────────────────────────────
    (b'onclick="runEncoder()">? Run Encoder<', b'onclick="runEncoder()">&#9654; Run Encoder<'),

    # ── Decoder Run button ────────────────────────────────────────────────
    (b'onclick="runDecoder()">? Run<', b'onclick="runDecoder()">&#9654; Run<'),

    # ── Cross-Attention badge: Encoder?Decoder ────────────────────────────
    (b'<span class="badge">Encoder?Decoder</span>', b'<span class="badge">Encoder&#8594;Decoder</span>'),

    # ── Cross-Attention heatmap label: decoder rows ? encoder cols ────────
    (b'decoder rows ? encoder cols', b'decoder rows &#8594; encoder cols'),

    # SDPA step 1: "Q ? K?" where ? is the middot and K? ends with KT
    # If still not fixed:
    (b'Dot Product: Q ? K?</h4>', b'Dot Product: Q &middot; K<sup>T</sup></h4>'),

    # MultiHead Concat – if head? still broken from byte-level:
    (b',head?) ', b',head<sub>h</sub>) '),
]

out = raw
applied = 0
for old, new in byte_fixes:
    count_before = out.count(old)
    if count_before > 0:
        out = out.replace(old, new)
        print(f'[OK x{count_before}] {repr(old[:60])}')
        applied += count_before
    else:
        # don't print "not found" for the ones we know are already correct
        pass

# Decode and do text-level fixes
text = out.decode('utf-8', errors='replace')

text_fixes = [
    # Raw Scores label for masked attention
    ('masked future = -8)', 'masked future = -&infin;)'),
    # Masked attention description
    ('masked with -8 so', 'masked with -&infin; so'),
    # training section masking descriptions
    ('blocked by setting scores to -8', 'blocked by setting scores to -&infin;'),
    # Encoder description arrow
    ('Multi-Head Self-Attention &#8594; Add&amp;Norm &#8594; FFN &#8594; Add&amp;Norm',
     'Multi-Head Self-Attention &#8594; Add&amp;Norm &#8594; FFN &#8594; Add&amp;Norm'),  # no-op if already good
    # FFN formula d_ff = 4 × d_model (already fixed, skip)
]

for old, new in text_fixes:
    if old != new and old in text:
        text = text.replace(old, new)
        print(f'[OK text] {repr(old[:60])}')
        applied += 1

# Final REPL check
R_char = '\ufffd'
still_repl = [(i, text[max(0,i-30):i+30]) for i, c in enumerate(text) if c == R_char]
# Remaining literal ? check in key places:
checks = [
    ('Enc?Dec',),
    ('Softmax ? Attention',),
    ('? Run<',),
    ('?? Random',),
    ('Encoder?Decoder',),
    ('decoder rows ?',),
    ('K?</span>',),
]
print(f'\n[INFO] Applied {applied} byte/text fixes.')
print(f'[INFO] Remaining U+FFFD: {len(still_repl)}')
for p, ctx in still_repl:
    print(f'  pos {p}: {repr(ctx)}')

print('\n[INFO] Checking for remaining broken ? patterns:')
for (pat,) in checks:
    found = pat.encode() in out or pat in text
    print(f'  {"STILL BROKEN" if found else "OK           "}: {repr(pat)}')

# Normalise line endings
text = text.replace('\r\r\r\n', '\r\n').replace('\r\r\n', '\r\n')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print(f'\nSaved index.html ({len(text.encode())} bytes)')



# ══════════════════════════════════════════════════════════════════════════════

# SECTION: diagnose.py
# Diagnostic: find remaining U+FFFD chars and dump context to file


# ══════════════════════════════════════════════════════════════════════════════

# Look at raw bytes around remaining broken positions to understand encoding
with open('index.html', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-8', errors='replace')
R = '\ufffd'

positions = [i for i, c in enumerate(content) if c == R]

print(f'Remaining: {len(positions)} chars')
print()

# Map character positions to byte positions
byte_map = []
byte_pos = 0
for char in content:
    byte_map.append(byte_pos)
    byte_pos += len(char.encode('utf-8', errors='replace'))

with open('raw_bytes.txt', 'w', encoding='utf-8') as f:
    for cp in positions:
        bp = byte_map[cp]
        surrounding_bytes = raw[max(0, bp-15):bp+15]
        # Show chars around it
        ctx_chars = content[max(0,cp-30):cp+30].replace('\r','').replace('\n','')
        f.write(f'char_pos={cp}  byte_pos={bp}\n')
        f.write(f'  context: {repr(ctx_chars)}\n')
        f.write(f'  raw bytes: {" ".join(f"{b:02x}" for b in surrounding_bytes)}\n\n')

print('Written raw_bytes.txt')



# ══════════════════════════════════════════════════════════════════════════════

# ENTRY POINT


# ══════════════════════════════════════════════════════════════════════════════


if __name__ == '__main__':
    import sys
    print('transformer_tools.py')
    print('====================')
    print('Available sections: fix_encoding, append_js, fix_html_chars,')
    print('                    fix_final, fix_remaining, fix_plain_question_marks, diagnose')
    print()
    print('Run individual sections directly or import them as needed.')
    print('Current index.html, styles.css, and app.js are the clean separated files.')
