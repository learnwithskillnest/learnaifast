/* LearnAIFast: floating "Chat on WhatsApp" button, shared by every page. */
(function(){
  if(document.getElementById("lf-wa")) return;
  var NUM="919453712002";
  var page=document.title.split(/\s[|–-]\s/)[0];
  var msg="Hi LearnAIFast, I have a question about \""+page+"\": ";
  var a=document.createElement("a");
  a.id="lf-wa"; a.href="https://wa.me/"+NUM+"?text="+encodeURIComponent(msg);
  a.target="_blank"; a.rel="noopener"; a.setAttribute("aria-label","Chat with LearnAIFast on WhatsApp");
  a.innerHTML='<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M12 3C6.9 3 3 6.6 3 11c0 2.2 1 4.200 2.700 5.600L5 21l4.300-2.200c.9.200 1.800.300 2.700.300 5.100 0 9-3.600 9-8.100S17.100 3 12 3zm-4 9.200a1.200 1.200 0 1 1 0-2.400 1.200 1.200 0 0 1 0 2.400zm4 0a1.200 1.200 0 1 1 0-2.400 1.200 1.200 0 0 1 0 2.400zm4 0a1.200 1.200 0 1 1 0-2.400 1.200 1.200 0 0 1 0 2.400z"/></svg><span>Chat on WhatsApp</span>';
  var s=document.createElement("style");
  s.textContent="#lf-wa{position:fixed;right:max(16px,env(safe-area-inset-right,0px));bottom:max(16px,env(safe-area-inset-bottom,0px));z-index:50;display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:999px;background:#25D366;color:#0B2A17;font:600 15px/1 system-ui,-apple-system,'Segoe UI',sans-serif;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.18)}#lf-wa:hover{background:#1EBE5B}#lf-wa:focus-visible{outline:2px solid #0B2A17;outline-offset:3px}@media (max-width:640px){#lf-wa{padding:12px}#lf-wa span{display:none}}@media print{#lf-wa{display:none}}";
  document.head.appendChild(s); document.body.appendChild(a);
})();
