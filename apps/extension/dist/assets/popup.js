(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();function e(){return new Promise((e,t)=>{chrome.runtime.sendMessage({type:`FINVISOR_GET_CURRENT_STOCK_CONTEXT`},n=>{if(chrome.runtime.lastError){t(Error(chrome.runtime.lastError.message));return}e(n)})})}var t=document.querySelector(`#status`),n=document.querySelector(`#stock-context`);async function r(){if(!(!t||!n))try{let r=await e();if(!r.success||!r.context){t.textContent=r.error??`No stock context found.`;return}let i=r.context;t.textContent=`Stock context found.`,n.innerHTML=`
      <h2>${i.companyName??i.symbol}</h2>

      <p>
        <strong>Symbol:</strong>
        ${i.symbol}
      </p>

      <p>
        <strong>Exchange:</strong>
        ${i.exchange??`Unknown`}
      </p>

      <p>
        <strong>Price:</strong>
        ${i.price??`Unavailable`}
      </p>

      <p>
        <strong>Change:</strong>
        ${i.change??`Unavailable`}
      </p>

      <p>
        <strong>Change %:</strong>
        ${i.changePercent??`Unavailable`}
      </p>
    `}catch(e){t.textContent=e instanceof Error?e.message:`Unable to load stock context.`}}r();