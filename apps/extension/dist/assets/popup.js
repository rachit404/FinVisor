(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();function e(){return new Promise((e,t)=>{chrome.runtime.sendMessage({type:`FINVISOR_GET_CURRENT_STOCK_CONTEXT`},n=>{if(chrome.runtime.lastError){t(Error(chrome.runtime.lastError.message));return}e(n)})})}function t(e){return new Promise((t,n)=>{chrome.runtime.sendMessage({type:`FINVISOR_ANALYZE_STOCK`,prompt:e},e=>{if(chrome.runtime.lastError){n(Error(chrome.runtime.lastError.message));return}t(e)})})}var n=document.querySelector(`#status`),r=document.querySelector(`#stock-context`),i=document.querySelector(`#question`),a=document.querySelector(`#ask-button`),o=document.querySelector(`#answer`);async function s(){if(!(!n||!r))try{let t=await e();if(!t.success||!t.context){n.textContent=t.error??`No stock context found.`;return}let i=t.context;n.textContent=`Stock context found.`,r.innerHTML=`
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
    `}catch(e){n.textContent=e instanceof Error?e.message:`Unable to load stock context.`}}async function c(){let e=i?.value.trim();if(!e){o&&(o.textContent=`Please enter a question.`);return}a&&(a.disabled=!0),o&&(o.textContent=`Analyzing stock...`);try{let n=await t(e);if(!n.success||!n.data)throw Error(n.error??`Unable to analyze stock.`);let r=n.data;o&&(o.innerHTML=`
        <h3>Analysis</h3>

        <p>
          <strong>Action:</strong>
          ${r.action}
        </p>

        <p>
          <strong>Confidence:</strong>
          ${r.confidence}%
        </p>

        <p>
          <strong>Summary:</strong>
          ${r.summary}
        </p>

        <strong>Reasons:</strong>

        <ul>
          ${r.reasons.map(e=>`<li>${e}</li>`).join(``)}
        </ul>
      `)}catch(e){o&&(o.textContent=e instanceof Error?e.message:`Unable to analyze stock.`)}finally{a&&(a.disabled=!1)}}s(),a?.addEventListener(`click`,()=>{c()});