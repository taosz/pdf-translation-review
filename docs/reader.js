
import * as pdfjs from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs';
pdfjs.GlobalWorkerOptions.workerSrc='https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs';
const pt=document.documentElement.lang.toLowerCase()==='pt-br';
const text=(en,br)=>pt?br:en;
const maxBytes=50*1024*1024,maxPages=300;
const el=id=>document.getElementById(id), previous=el('previous'),next=el('next');
const sides={};
for(const id of ['original','translated']){
  const side=sides[id]={id,file:el(id+'-file'),input:el(id+'-page'),total:el(id+'-total'),status:el(id+'-status'),canvas:el(id+'-canvas'),doc:null,loading:null,render:null,generation:0,renderGeneration:0};
  side.file.addEventListener('change',()=>open(side,side.file.files?.[0]));
  el(id+'-clear').addEventListener('click',()=>clear(side));
  side.input.addEventListener('change',()=>{const n=Number(side.input.value);if(Number.isInteger(n)&&n>=1&&n<=side.doc?.numPages)draw(side,n);else if(side.doc)side.input.value=String(side.page);});
}
function update(){const a=sides.original,b=sides.translated;previous.disabled=!a.doc||!b.doc||a.page<=1||b.page<=1;next.disabled=!a.doc||!b.doc||a.page>=a.doc.numPages||b.page>=b.doc.numPages;}
function clear(side,resetInput=true){side.generation++;side.renderGeneration++;side.render?.cancel();side.render=null;side.loading?.destroy();side.loading=null;side.doc=null;side.page=1;if(resetInput)side.file.value='';side.input.value='1';side.input.disabled=true;side.total.textContent='';side.status.textContent='';side.canvas.width=0;side.canvas.height=0;update();}
async function open(side,file){clear(side,false);if(!file)return;const generation=side.generation;side.status.textContent=text('Opening PDF locally…','Abrindo o PDF neste navegador…');try{
  if(!file.size||file.size>maxBytes||!/\.pdf$/i.test(file.name))throw Error('invalid');
  const bytes=new Uint8Array(await file.arrayBuffer());if(generation!==side.generation)return;
  const header=new TextDecoder().decode(bytes.subarray(0,1024));if(!header.includes('%PDF-'))throw Error('invalid');
  side.loading=pdfjs.getDocument({data:bytes,isEvalSupported:false});const doc=await side.loading.promise;
  if(generation!==side.generation){await doc.destroy();return;}if(doc.numPages<1||doc.numPages>maxPages)throw Error('pages');
  side.doc=doc;side.page=1;side.input.max=String(doc.numPages);side.input.disabled=false;side.total.textContent=text('of ','de ')+doc.numPages;side.status.textContent='';await draw(side,1);
 }catch(error){if(generation!==side.generation)return;side.loading?.destroy();side.loading=null;side.doc=null;side.input.disabled=true;side.total.textContent='';side.status.textContent=error.message==='pages'?text('This reader supports at most 300 pages per PDF.','Este leitor aceita no máximo 300 páginas por PDF.'):text('Could not open this PDF. Choose a non-empty, unencrypted PDF up to 50 MiB.','Não foi possível abrir o PDF. Escolha um arquivo não vazio, sem senha e de até 50 MiB.');update();}}
async function draw(side,n){const generation=++side.renderGeneration,old=side.render;old?.cancel();side.page=n;side.input.value=String(n);update();try{if(old)await old.promise.catch(()=>{});if(generation!==side.renderGeneration||!side.doc)return;const page=await side.doc.getPage(n);if(generation!==side.renderGeneration)return;const raw=page.getViewport({scale:1});const scale=Math.min(1.8,1200/raw.width,1600/raw.height);const viewport=page.getViewport({scale});side.canvas.width=Math.ceil(viewport.width);side.canvas.height=Math.ceil(viewport.height);side.render=page.render({canvasContext:side.canvas.getContext('2d'),viewport});await side.render.promise;if(generation===side.renderGeneration)side.status.textContent='';}catch(error){if(generation===side.renderGeneration&&error.name!=='RenderingCancelledException')side.status.textContent=text('Could not render this page; try another PDF reader.','Não foi possível exibir esta página; experimente outro leitor de PDF.');}}
function shift(delta){for(const side of Object.values(sides))if(side.doc)void draw(side,side.page+delta);}
previous.addEventListener('click',()=>shift(-1));next.addEventListener('click',()=>shift(1));




function samplePdf(lines){
 const commands=['BT','/F1 18 Tf','54 730 Td',...lines.flatMap((line,i)=>[...(i?['0 -32 Td']:[]),'('+line.replace(/[\\()]/g,'\\$&')+') Tj']),'ET'].join('\n');
 const objects=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R] /Count 1 >>','<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>','<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>','<< /Length '+commands.length+' >>\nstream\n'+commands+'\nendstream'];
 let pdf='%PDF-1.4\n',offsets=[0];for(let i=0;i<objects.length;i++){offsets.push(pdf.length);pdf+=(i+1)+' 0 obj\n'+objects[i]+'\nendobj\n';}
 const xref=pdf.length;pdf+='xref\n0 '+offsets.length+'\n0000000000 65535 f \n';for(const offset of offsets.slice(1))pdf+=String(offset).padStart(10,'0')+' 00000 n \n';pdf+='trailer\n<< /Size '+offsets.length+' /Root 1 0 R >>\nstartxref\n'+xref+'\n%%EOF\n';
 return new TextEncoder().encode(pdf);
}
el('try-example').addEventListener('click',()=>{
 sides.original.file.value='';sides.translated.file.value='';
 void open(sides.original,new File([samplePdf(['Fictional practice example','Do not exceed 12 bar.','Check the label before use.'])],'fictional-original.pdf',{type:'application/pdf'}));
 void open(sides.translated,new File([samplePdf(['Ejemplo ficticio para practicar','No exceda 12 bar.','Revise la etiqueta antes de usar.'])],'fictional-spanish.pdf',{type:'application/pdf'}));
});
