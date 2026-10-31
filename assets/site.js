/* LearnAIFast shared script: copy buttons on prompts, newsletter form, and redirects for old #links. */
(function(){
  var OLD={"what-is-ai":"/what-is-ai/","ai-for-students":"/ai-for-students/","prompts":"/how-to-write-ai-prompts/","about":"/about/","contact":"/contact/","privacy":"/privacy-policy/","disclaimer":"/disclaimer/","guides":"/guides/","home":"/"};
  if(location.pathname==="/"&&location.hash){var k=location.hash.slice(1); if(OLD[k]&&OLD[k]!=="/") location.replace(OLD[k]);}

  document.querySelectorAll(".prompt").forEach(function(el){
    var b=document.createElement("button"); b.type="button"; b.textContent="Copy";
    b.addEventListener("click",function(){
      var text=el.querySelector(".t").textContent;
      function done(){b.textContent="Copied"; setTimeout(function(){b.textContent="Copy";},1500);}
      function fallback(){var r=document.createRange(); r.selectNodeContents(el.querySelector(".t")); var s=getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent="Selected";}
      try{ navigator.clipboard.writeText(text).then(done,fallback); }catch(e){ fallback(); }
    });
    el.appendChild(b);
  });

  var nf=document.getElementById("nf");
  if(nf) nf.addEventListener("submit",function(e){
    e.preventDefault();
    var v=document.getElementById("nf-email").value.trim(), ok=document.getElementById("nf-ok");
    ok.hidden=false;
    ok.textContent=/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)?"Preview only: connect this form to your email tool (e.g. Mailchimp) on the live site.":"Enter a valid email address, like you@example.com.";
  });
})();
