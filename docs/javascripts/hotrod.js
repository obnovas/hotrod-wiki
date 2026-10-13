// Turn "Confidence: X" in article records into timing-tag chips; mark timeline page.
function hrEnhance(){
  document.querySelectorAll(".admonition.abstract p, .admonition.abstract li").forEach(function(p){
    if(p.dataset.hr) return; p.dataset.hr=1;
    p.querySelectorAll("strong").forEach(function(s){
      if(!/^Confidence:?$/.test(s.textContent.trim())) return;
      var n=s.nextSibling; if(!n||n.nodeType!==3) return;
      var m=n.textContent.match(/^\s*([^·]+?)\s*(·|$)/); if(!m) return;
      var v=m[1], c=document.createElement("span");
      c.className="hr-chip "+(/^high/i.test(v)?"hr-chip--high":/^low/i.test(v)?"hr-chip--low":"hr-chip--mid");
      c.textContent=v; n.textContent=n.textContent.slice(m[0].length-(m[2]?m[2].length:0));
      s.after(" ",c," ");
    });
  });
  document.body.classList.toggle("hr-timeline",/\/reference\/timeline\/?$/.test(location.pathname));
}
if(window.document$){document$.subscribe(hrEnhance)}else{document.addEventListener("DOMContentLoaded",hrEnhance)}
