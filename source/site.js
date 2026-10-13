(function(){
  var SM = window.SMHC;
  if (!SM){ try { SM = JSON.parse(document.getElementById('smhc-config').textContent); } catch(e){ SM = null; } }
  SM = SM || {ids:[], names:{}, views:[]};
  var views = Array.prototype.slice.call(document.querySelectorAll('.view'));
  var byName = {}; views.forEach(function(v){ byName[v.getAttribute('data-view')] = v; });
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('nav.main a[data-nav]'));
  var nav = document.getElementById('mainnav');
  var menuBtn = document.querySelector('.menu-btn');
  var current = null;

  function sectionFor(name){
    if (SM.ids.indexOf(name) > -1) return 'services';
    return name;
  }
  function show(hash, fromLoad){
    var token = (hash || '').replace(/^#/, '');
    if (!token) token = 'home';
    var target = null, view = byName[token];
    if (!view){
      target = document.getElementById(token);
      if (target){ var v = target.closest('.view'); if (v) view = v; }
    }
    if (!view){ view = byName.home; token = 'home'; target = null; }
    var name = view.getAttribute('data-view');
    if (current !== view){
      views.forEach(function(v){ v.hidden = (v !== view); });
      if (!fromLoad){ view.classList.remove('fade'); void view.offsetWidth; view.classList.add('fade'); }
      current = view;
      var sec = sectionFor(name);
      navLinks.forEach(function(a){
        if (a.classList.contains('btn')) return;
        if (a.getAttribute('data-nav') === sec) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
      });
      var title = SM.names[name] ? SM.names[name] + ' | St Matthews Healthcare' : (name === 'home' ? 'St Matthews Healthcare' : (view.getAttribute('aria-label') + ' | St Matthews Healthcare'));
      try { document.title = title; } catch(e){}
    }
    if (target && target !== view){
      requestAnimationFrame(function(){ target.scrollIntoView({block:'start'}); });
    } else if (!fromLoad){
      window.scrollTo(0, 0);
    }
    if (nav.classList.contains('open')){ nav.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); }
  }
  // one page per address on the live site; every view in one page in the preview
  var multi = views.length === 1;
  if (multi){
    current = views[0]; current.hidden = false;
    var sec0 = sectionFor(current.getAttribute('data-view'));
    navLinks.forEach(function(a){ if (!a.classList.contains('btn') && a.getAttribute('data-nav') === sec0) a.setAttribute('aria-current', 'page'); });
    try {
      var q = new URLSearchParams(location.search).get('service');
      var sel0 = document.getElementById('f-svc');
      if (q && sel0 && sel0.querySelector('option[value="' + q.replace(/[^a-z-]/g, '') + '"]')) sel0.value = q;
    } catch(e){}
    document.addEventListener('click', function(e){
      var a = e.target.closest('a[href^="#"]');
      if (a && nav.classList.contains('open')){ nav.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); }
    });
  } else {
    window.addEventListener('hashchange', function(){ show(location.hash); });
    document.addEventListener('click', function(e){
      var a = e.target.closest('a[href^="#"]');
      if (!a) return;
      var h = a.getAttribute('href');
      if (h === location.hash){ e.preventDefault(); show(h); }
      var svc = a.getAttribute('data-svc');
      if (svc){ var sel = document.getElementById('f-svc'); if (sel) sel.value = svc; }
    });
    show(location.hash, true);
  }

  // menu
  menuBtn.addEventListener('click', function(){
    var open = !nav.classList.contains('open');
    nav.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // text size
  var tsBtns = Array.prototype.slice.call(document.querySelectorAll('.ts button'));
  function setTs(n){
    document.documentElement.classList.remove('ts-1', 'ts-2');
    if (n > 0) document.documentElement.classList.add('ts-' + n);
    tsBtns.forEach(function(b){ b.setAttribute('aria-pressed', b.getAttribute('data-ts') == n ? 'true' : 'false'); });
    try { localStorage.setItem('smhc-ts', String(n)); } catch(e){}
  }
  tsBtns.forEach(function(b){ b.addEventListener('click', function(){ setTs(+b.getAttribute('data-ts')); }); });
  try { var saved = localStorage.getItem('smhc-ts'); if (saved) setTs(+saved); } catch(e){}

  // toast + copy
  var toast = document.getElementById('toast'), tt;
  function say(msg){ toast.textContent = msg; toast.hidden = false; clearTimeout(tt); tt = setTimeout(function(){ toast.hidden = true; }, 2600); }
  function copyText(text, btn){
    function ok(){ if (btn){ var sp = btn.querySelector('span') || btn; if (!btn.hasAttribute('data-o')) btn.setAttribute('data-o', sp.textContent); btn.classList.add('done'); sp.textContent = 'Copied'; clearTimeout(btn._t); btn._t = setTimeout(function(){ btn.classList.remove('done'); sp.textContent = btn.getAttribute('data-o'); btn.removeAttribute('data-o'); }, 1600); } say('Copied: ' + (text.length > 60 ? text.slice(0, 57) + '...' : text)); }
    function fail(){ say('Select the text and copy it: ' + (text.length > 60 ? text.slice(0, 57) + '...' : text)); }
    try { navigator.clipboard.writeText(text).then(ok, fail); } catch(e){ fail(); }
  }
  document.addEventListener('click', function(e){
    var b = e.target.closest('[data-copy]');
    if (b){ e.preventDefault(); copyText(b.getAttribute('data-copy'), b); }
  });

  // finder
  var cards = Array.prototype.slice.call(document.querySelectorAll('#sgrid .scard'));
  var fbs = Array.prototype.slice.call(document.querySelectorAll('.fb'));
  var state = {type:'all', region:'all', tags:[], place:null};
  var count = document.getElementById('fcount'), empty = document.getElementById('fempty');
  var pins = Array.prototype.slice.call(document.querySelectorAll('.filters .pin[data-place]'));
  function apply(){
    var n = 0;
    cards.forEach(function(c){
      var ok = (state.type === 'all' || c.getAttribute('data-type') === state.type)
        && (state.region === 'all' || c.getAttribute('data-region') === state.region)
        && (!state.place || c.getAttribute('data-place') === state.place);
      var tags = (c.getAttribute('data-tags') || '').split(' ');
      state.tags.forEach(function(t){ if (tags.indexOf(t) < 0) ok = false; });
      c.hidden = !ok; if (ok) n++;
    });
    fbs.forEach(function(b){
      var g = b.getAttribute('data-f'), v = b.getAttribute('data-v');
      var on = g === 'tag' ? state.tags.indexOf(v) > -1 : state[g] === v;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    pins.forEach(function(p){ p.classList.toggle('on', p.getAttribute('data-place') === state.place); });
    var placeName = state.place ? (' in ' + (pins.filter(function(p){ return p.getAttribute('data-place') === state.place; })[0] || {getAttribute:function(){return '';}}).getAttribute('aria-label').split(',')[0]) : '';
    count.textContent = n === 10 ? 'Showing all 10 services' : ('Showing ' + n + ' of 10 services' + placeName);
    empty.hidden = n !== 0;
  }
  fbs.forEach(function(b){
    b.addEventListener('click', function(){
      var g = b.getAttribute('data-f'), v = b.getAttribute('data-v');
      if (g === 'tag'){ var i = state.tags.indexOf(v); if (i > -1) state.tags.splice(i, 1); else state.tags.push(v); }
      else { state[g] = v; if (g === 'region') state.place = null; }
      apply();
    });
  });
  function pinClick(p){ var v = p.getAttribute('data-place'); state.place = state.place === v ? null : v; state.region = 'all'; apply(); }
  pins.forEach(function(p){
    p.addEventListener('click', function(){ pinClick(p); });
    p.addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); pinClick(p); } });
  });
  var reset = document.getElementById('freset');
  if (reset) reset.addEventListener('click', function(){ state = {type:'all', region:'all', tags:[], place:null}; apply(); });

  // enquiry delivery: a secure form handler when one is configured at launch,
  // otherwise the sender's own email app, addressed and ready to send
  var EP = SM.endpoint || {};
  var MAXURL = 1900;
  function mailHref(to, subject, lines){
    var cut = false, body = lines.join('\r\n');
    function build(b){ return 'mailto:' + to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(b); }
    var href = build(body);
    if (href.length > MAXURL){
      cut = true;
      var note = '\r\n\r\n[Shortened here. Full details to follow.]';
      var lo = 0, hi = body.length;
      while (lo < hi){ var mid = Math.ceil((lo + hi) / 2); if (build(body.slice(0, mid) + note).length <= MAXURL) lo = mid; else hi = mid - 1; }
      href = build(body.slice(0, lo).replace(/\s+\S*$/, '') + note);
    }
    return {href: href, cut: cut};
  }
  function post(url, data){
    var ctl = ('AbortController' in window) ? new AbortController() : null;
    var t = setTimeout(function(){ if (ctl) ctl.abort(); }, 12000);
    return fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data), signal: ctl ? ctl.signal : undefined})
      .then(function(r){ clearTimeout(t); if (!r.ok) throw new Error('send'); return r; }, function(e){ clearTimeout(t); throw e; });
  }
  function openMail(a){ try { a.click(); } catch(e){} }
  function setBtnText(btn, text){ var sp = btn.querySelector('span'); if (sp) sp.textContent = text; else btn.textContent = text; }
  // send(kind, data, ui): ui = {mail, long, k, t, p, f, to, subject, lines, sentP, sentF, show}
  function send(kind, data, ui){
    var m = mailHref(ui.to, ui.subject, ui.lines);
    ui.mail.setAttribute('href', m.href);
    ui.long.hidden = !m.cut;
    function viaMail(auto){
      ui.k.textContent = 'Nearly there'; ui.t.textContent = ui.readyT;
      ui.p.innerHTML = ui.readyP; ui.f.hidden = false; ui.mail.hidden = false;
      setBtnText(ui.mail, auto ? 'Open the email again' : 'Open the email');
      ui.show();
      if (auto) openMail(ui.mail);
    }
    if (EP[kind]){
      ui.busy(true);
      post(EP[kind], data).then(function(){
        ui.busy(false);
        ui.k.textContent = 'Sent'; ui.t.textContent = ui.sentT; ui.p.textContent = ui.sentP;
        ui.long.hidden = true; ui.f.hidden = true; ui.mail.hidden = true; ui.show();
      }, function(){ ui.busy(false); viaMail(false); });
    } else viaMail(true);
  }

  // referral form
  var form = document.getElementById('refform'), done = document.getElementById('refdone');
  var sum = document.getElementById('refsum'), err = document.getElementById('f-err');
  function val(id){ var el = document.getElementById(id); return el ? el.value.trim() : ''; }
  function txt(id){ var el = document.getElementById(id); return el && el.value ? el.options[el.selectedIndex].text : ''; }
  var okMail = function(v){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); };
  if (form){
    var refSubmit = form.querySelector('button[type="submit"]');
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var role = val('f-role'), name = val('f-name'), email = val('f-email');
      ['f-role', 'f-name', 'f-email'].forEach(function(id){ document.getElementById(id).removeAttribute('aria-invalid'); });
      if (!role || !name || !okMail(email)){
        err.hidden = false;
        var bad = !role ? 'f-role' : !name ? 'f-name' : 'f-email';
        document.getElementById(bad).setAttribute('aria-invalid', 'true'); document.getElementById(bad).focus(); return;
      }
      err.hidden = true;
      var svc = txt('f-svc') || 'Not sure yet', need = val('f-need');
      var data = {form: 'referral', from: name, organisation: val('f-org'), role: role, email: email, telephone: val('f-tel'),
                  service: svc, need: need, funding: val('f-fund'), when: val('f-when'), area: val('f-area'), message: val('f-msg')};
      var lines = [
        'Referral enquiry for St Matthews Healthcare',
        '',
        'From: ' + name + (data.organisation ? ', ' + data.organisation : ''),
        'Role: ' + role,
        'Email: ' + email + (data.telephone ? '   Telephone: ' + data.telephone : ''),
        '',
        'Service of interest: ' + svc,
        'Main need: ' + need,
        'Funding route: ' + data.funding,
        'How soon: ' + data.when,
        'Area: ' + (data.area || 'Not given'),
        '',
        'About the need:',
        data.message || 'Not given',
        '',
        'No name, date of birth or NHS number has been included. Please contact me to share these securely.'
      ];
      sum.textContent = lines.join('\n');
      var subject = 'Referral enquiry: ' + (need && need !== 'Not sure yet' ? need : 'placement') + (svc !== 'Not sure yet' ? ', ' + svc.split(',')[0] : '');
      send('referral', data, {
        to: SM.refEmail, subject: subject, lines: lines,
        mail: document.getElementById('refmail'), long: document.getElementById('reflong'),
        k: document.getElementById('refdone-k'), t: document.getElementById('refdone-t'), p: document.getElementById('refdone-p'), f: document.getElementById('refdone-f'),
        readyT: 'Your referral is ready to send.',
        readyP: 'Your email app should now be open with the referral addressed to <b>' + SM.refEmail + '</b>. Attach any documents, then press send.',
        sentT: 'Thank you. Your referral is with our team.',
        sentP: 'Our referral team will be in touch. If it is urgent, call ' + SM.refPhone + '.',
        busy: function(on){ refSubmit.disabled = on; setBtnText(refSubmit, on ? 'Sending' : 'Send referral'); },
        show: function(){ form.hidden = true; done.hidden = false; try { done.focus({preventScroll: true}); } catch(x){ done.focus(); } done.scrollIntoView({block: 'start'}); }
      });
    });
    document.getElementById('refcopy').addEventListener('click', function(e){ copyText(sum.textContent, e.currentTarget); });
    document.getElementById('refedit').addEventListener('click', function(){ done.hidden = true; form.hidden = false; document.getElementById('f-role').focus(); });
  }

  // careers enquiry: a short form behind every area of work
  var JD = document.getElementById('jobdlg'), JF = document.getElementById('jobform'), JN = document.getElementById('jobdone'),
      JS = document.getElementById('jobsum'), JE = document.getElementById('j-err'), JT = document.getElementById('job-t'), jobOpener = null;
  function openJob(btn){
    jobOpener = btn;
    var role = btn.getAttribute('data-job') || '';
    var sel = document.getElementById('j-role'); sel.value = role;
    JT.textContent = role ? 'Enquire about ' + role.toLowerCase() : 'Send an enquiry';
    JF.hidden = false; JN.hidden = true; JE.hidden = true;
    document.documentElement.classList.add('noscroll');
    if (typeof JD.showModal === 'function'){ if (!JD.open) JD.showModal(); } else { JD.setAttribute('open', ''); JD.classList.add('nomodal'); }
    JD.querySelector('.dlg-body').scrollTop = 0;
    var first = document.getElementById('j-name');
    setTimeout(function(){ try { first.focus({preventScroll: true}); } catch(x){ first.focus(); } }, 30);
  }
  function closeJob(){
    if (!JD.open && !JD.hasAttribute('open')) return;
    if (typeof JD.close === 'function' && JD.open) JD.close(); else { JD.removeAttribute('open'); }
  }
  if (JD){
    JD.addEventListener('close', function(){
      document.documentElement.classList.remove('noscroll');
      if (jobOpener){ try { jobOpener.focus({preventScroll: true}); } catch(x){} }
    });
    document.addEventListener('click', function(e){
      var b = e.target.closest('[data-job]');
      if (b){ e.preventDefault(); openJob(b); }
    });
    document.getElementById('job-x').addEventListener('click', closeJob);
    document.getElementById('jobclose').addEventListener('click', closeJob);
    JD.addEventListener('click', function(e){ if (e.target === JD) closeJob(); });
    document.addEventListener('keydown', function(e){
      if (!JD.hasAttribute('open')) return;
      if (e.key === 'Escape' && JD.classList.contains('nomodal')) closeJob();
      if (e.key === 'Tab'){
        var f = Array.prototype.slice.call(JD.querySelectorAll('a[href], button:not([disabled]), input, select, textarea')).filter(function(el){ return el.offsetParent !== null; });
        if (!f.length) return;
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && (i <= 0)){ e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && (i === -1 || i === f.length - 1)){ e.preventDefault(); f[0].focus(); }
      }
    });
    window.addEventListener('hashchange', closeJob);
    var jobSubmit = JF.querySelector('button[type="submit"]');
    JF.addEventListener('submit', function(e){
      e.preventDefault();
      var name = val('j-name'), email = val('j-email');
      ['j-name', 'j-email'].forEach(function(id){ document.getElementById(id).removeAttribute('aria-invalid'); });
      if (!name || !okMail(email)){
        JE.hidden = false; var bad = !name ? 'j-name' : 'j-email';
        document.getElementById(bad).setAttribute('aria-invalid', 'true'); document.getElementById(bad).focus(); return;
      }
      JE.hidden = true;
      var role = val('j-role'), where = txt('j-where') || 'Anywhere in the group';
      var data = {form: 'careers', role: role || 'Not sure yet', name: name, email: email, telephone: val('j-tel'),
                  where: where, experience: txt('j-exp'), hours: txt('j-hours'), message: val('j-msg')};
      var lines = [
        'Careers enquiry for St Matthews Healthcare',
        '',
        'Area of work: ' + data.role,
        'Name: ' + name,
        'Email: ' + email + (data.telephone ? '   Telephone: ' + data.telephone : ''),
        'Where: ' + where,
        'Experience: ' + (data.experience || 'Not given'),
        'Hours: ' + (data.hours || 'Not sure yet'),
        '',
        'About me:',
        data.message || 'Not given'
      ];
      JS.textContent = lines.join('\n');
      var subject = 'Careers enquiry: ' + (role || 'general enquiry') + (where !== 'Anywhere in the group' ? ', ' + where.split(',')[0] : '');
      send('careers', data, {
        to: SM.recEmail, subject: subject, lines: lines,
        mail: document.getElementById('jobmail'), long: document.getElementById('joblong'),
        k: document.getElementById('jobdone-k'), t: document.getElementById('jobdone-t'), p: document.getElementById('jobdone-p'), f: document.getElementById('jobdone-f'),
        readyT: 'Your enquiry is ready to send.',
        readyP: 'Your email app should now be open with your enquiry addressed to <b>' + SM.recEmail + '</b>. Attach your CV if you would like to, then press send.',
        sentT: 'Thank you. Your enquiry is with our recruitment team.',
        sentP: 'Our recruitment team will be in touch using the details you gave.',
        busy: function(on){ jobSubmit.disabled = on; setBtnText(jobSubmit, on ? 'Sending' : 'Send enquiry'); },
        show: function(){ JF.hidden = true; JN.hidden = false; JD.querySelector('.dlg-body').scrollTop = 0; try { JN.focus({preventScroll: true}); } catch(x){ JN.focus(); } }
      });
    });
    document.getElementById('jobcopy').addEventListener('click', function(e){ copyText(JS.textContent, e.currentTarget); });
    document.getElementById('jobedit').addEventListener('click', function(){ JN.hidden = true; JF.hidden = false; document.getElementById('j-name').focus(); });
  }

  // brochure viewer: one click opens the brochure on screen
  var V = document.getElementById('viewer'), VI = document.getElementById('viewer-img'), VT = document.getElementById('viewer-t'),
      VD = document.getElementById('viewer-dl'), VX = document.getElementById('viewer-x'), VB = document.getElementById('viewer-body'), opener = null;
  function openViewer(t){
    opener = t;
    VI.removeAttribute('src'); VB.classList.remove('ready');
    VI.onload = function(){ VB.classList.add('ready'); };
    VI.src = t.getAttribute('data-view-img');
    VI.alt = 'The ' + t.getAttribute('data-view-title') + ' brochure';
    VT.textContent = t.getAttribute('data-view-title');
    VD.setAttribute('href', t.getAttribute('data-view-pdf'));
    VD.setAttribute('data-dl', t.getAttribute('data-view-file'));
    if (!window.claude) VD.setAttribute('download', t.getAttribute('data-view-file'));
    V.classList.toggle('land', t.hasAttribute('data-view-land'));
    V.hidden = false; VB.scrollTop = 0;
    document.documentElement.classList.add('noscroll');
    try { VX.focus({preventScroll: true}); } catch(e){ VX.focus(); }
  }
  function closeViewer(){
    if (V.hidden) return;
    V.hidden = true; document.documentElement.classList.remove('noscroll');
    if (opener) { try { opener.focus({preventScroll: true}); } catch(e){} }
  }
  if (V){
    document.addEventListener('click', function(e){
      var t = e.target.closest('[data-view-img]');
      if (!t) return;
      e.preventDefault(); openViewer(t);
    });
    VX.addEventListener('click', closeViewer);
    VB.addEventListener('click', function(e){ if (e.target === VB) closeViewer(); });
    document.addEventListener('keydown', function(e){
      if (V.hidden) return;
      if (e.key === 'Escape') { e.preventDefault(); closeViewer(); }
      if (e.key === 'Tab') { var f = [VD, VX]; var i = f.indexOf(document.activeElement); e.preventDefault(); f[(i + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus(); }
    });
    window.addEventListener('hashchange', closeViewer);
  }

  // brochure downloads: the platform save dialog where it is available, a new tab otherwise
  var DL = null;
  try {
    if (window.claude && typeof window.claude.use === 'function'){
      window.claude.use('downloads').then(function(ns){ DL = ns; }, function(){ DL = null; });
    }
  } catch(e){}
  Array.prototype.slice.call(document.querySelectorAll('a[data-dl]')).forEach(function(a){ a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener'); });
  document.addEventListener('click', function(e){
    var a = e.target.closest('a[data-dl]');
    if (!a || !DL) return;
    e.preventDefault();
    var file = a.getAttribute('data-dl');
    say('Preparing ' + file + '...');
    fetch(a.getAttribute('href')).then(function(r){ if (!r.ok) throw new Error('fetch'); return r.blob(); })
      .then(function(blob){ return DL.save({filename: file, data: blob}); })
      .then(function(){ say('Brochure ready: ' + file); }, function(er){
        var code = er && er.code;
        if (code === 'declined') say('Download cancelled.');
        else say('This brochure could not be saved here. Ask us for it on ' + '01604 844 192.');
      });
  });
})();
