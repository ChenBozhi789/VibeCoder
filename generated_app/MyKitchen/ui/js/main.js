/* MyKitchen main.js - Vanilla JS (no modules). Implements recipe state, persistence, validation, search/filter/sort, copy, and import/export. */
(function(){
  var STORAGE_KEY = 'MyKitchen:state:v1';

  var subscribers = [];
  var appState = {
    recipes: [],
    ui: { search: '', tagFilter: 'all', sort: 'updatedAt_desc' },
    settings: { showPreview: true }
  };

  function loadState(){
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if(!raw) return;
      var data = JSON.parse(raw);
      if(data && typeof data === 'object'){
        if(!data.settings){ data.settings = { showPreview: true }; }
        appState = Object.assign(appState, data);
      }
    } catch(e){ console.warn('Failed to load state', e); }
  }
  function saveState(){
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(appState)); }
    catch(e){ console.warn('Failed to save state', e); }
  }
  function deepMerge(target, source){
    if(!source) return target;
    var out = Array.isArray(target) ? target.slice() : Object.assign({}, target);
    Object.keys(source).forEach(function(k){
      var sv = source[k], tv = out[k];
      if(sv && typeof sv === 'object' && !Array.isArray(sv)){
        out[k] = deepMerge(tv && typeof tv==='object'? tv : {}, sv);
      } else { out[k] = sv; }
    });
    return out;
  }
  function getState(){ return appState; }
  function setState(patch){
    appState = deepMerge(appState, patch || {});
    saveState();
    notify();
  }
  function subscribe(fn){ subscribers.push(fn); }
  function notify(){ subscribers.forEach(function(fn){ try{ fn(appState);}catch(e){console.error(e);} }); }
  function uid(){ return Date.now().toString(36) + Math.random().toString(36).slice(2,8); }

  function parseIngredients(text){
    var arr = (text || '').split(/\r?\n/).map(function(l){ return l.trim(); }).filter(function(l){ return l.length>0; });
    return arr;
  }
  function parseTags(text){
    var arr = (text || '').split(',').map(function(t){ return t.trim(); }).filter(function(t){ return t.length>0; });
    return arr;
  }

  function validateRecipe(data){
    var errors = {};
    if(!data.title || !data.title.trim()){ errors.title = 'Title is required.'; }
    var ing = Array.isArray(data.ingredients) ? data.ingredients : parseIngredients(data.ingredients || '');
    if(ing.length === 0){ errors.ingredients = 'At least one ingredient is required.'; }
    if(data.title && data.title.length > 160){ errors.title = 'Title must be at most 160 characters.'; }
    if(data.instructions && data.instructions.length > 10000){ errors.instructions = 'Instructions too long.'; }
    if(Array.isArray(data.tags)){
      // ok
    }
    return { valid: Object.keys(errors).length===0, errors: errors };
  }

  function addRecipe(data){
    var normalized = {
      title: (data.title || '').trim(),
      ingredients: Array.isArray(data.ingredients) ? data.ingredients : parseIngredients(data.ingredients || ''),
      instructions: (data.instructions || '').trim(),
      tags: Array.isArray(data.tags) ? data.tags : parseTags(data.tags || '')
    };
    var v = validateRecipe(normalized);
    if(!v.valid) return { ok:false, errors: v.errors };
    var recipe = {
      id: uid(),
      title: normalized.title,
      ingredients: normalized.ingredients,
      instructions: normalized.instructions,
      tags: normalized.tags,
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
    var list = getState().recipes.slice();
    list.unshift(recipe);
    setState({ recipes: list });
    return { ok:true, id: recipe.id };
  }

  function updateRecipe(id, patch){
    var list = getState().recipes.slice();
    var idx = list.findIndex(function(r){ return r.id===id; });
    if(idx<0) return { ok:false, error:'Recipe not found' };
    var current = list[idx];
    var merged = {
      title: ('title' in patch ? patch.title : current.title),
      ingredients: ('ingredients' in patch ? (Array.isArray(patch.ingredients) ? patch.ingredients : parseIngredients(patch.ingredients || '')) : current.ingredients),
      instructions: ('instructions' in patch ? (patch.instructions || '') : current.instructions),
      tags: ('tags' in patch ? (Array.isArray(patch.tags) ? patch.tags : parseTags(patch.tags || '')) : current.tags)
    };
    var v = validateRecipe(merged);
    if(!v.valid) return { ok:false, errors: v.errors };
    list[idx] = Object.assign({}, current, merged, { updatedAt: Date.now() });
    setState({ recipes: list });
    return { ok:true };
  }

  function deleteRecipe(id){
    var list = getState().recipes.filter(function(r){ return r.id!==id; });
    setState({ recipes: list });
  }

  function getAllTags(){
    var tags = {};
    getState().recipes.forEach(function(r){
      (r.tags || []).forEach(function(t){ tags[t] = true; });
    });
    return Object.keys(tags).sort(function(a,b){ return a.localeCompare(b); });
  }

  function recipeMatches(r, query, tag){
    var ok = true;
    if(query){
      var q = query.toLowerCase();
      var inTitle = (r.title || '').toLowerCase().indexOf(q) !== -1;
      var inIngr = (r.ingredients || []).some(function(i){ return (i || '').toLowerCase().indexOf(q) !== -1; });
      ok = ok && (inTitle || inIngr);
    }
    if(tag && tag!=='all'){
      ok = ok && (r.tags || []).some(function(t){ return t.toLowerCase() === tag.toLowerCase(); });
    }
    return ok;
    }

  function currentFilteredSorted(){
    var s = getState();
    var list = s.recipes.filter(function(r){ return recipeMatches(r, s.ui.search, s.ui.tagFilter); });
    var sort = s.ui.sort || 'updatedAt_desc';
    list.sort(function(a,b){
      switch(sort){
        case 'title_asc': return a.title.localeCompare(b.title);
        case 'title_desc': return b.title.localeCompare(a.title);
        case 'updatedAt_desc': default: return b.updatedAt - a.updatedAt;
      }
    });
    return list;
  }

  function firstInstructionLine(text){
    if(!text) return '';
    var lines = text.split(/\r?\n/).map(function(l){ return l.trim(); }).filter(function(l){ return l.length>0; });
    return lines[0] || '';
  }

  function exportJSON(){
    var data = JSON.stringify(getState(), null, 2);
    var blob = new Blob([data], {type: 'application/json'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'mykitchen_export.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function(){ URL.revokeObjectURL(url); a.remove(); }, 0);
  }

  function importJSON(file){
    return new Promise(function(resolve, reject){
      var reader = new FileReader();
      reader.onload = function(){
        try{
          var data = JSON.parse(reader.result);
          if(!data || typeof data!=='object'){ reject(new Error('Invalid JSON')); return; }
          var imported = Array.isArray(data.recipes) ? data.recipes : [];
          var replace = confirm('Replace existing data? OK = Replace, Cancel = Merge');
          if(replace){
            setState({ recipes: imported, ui: appState.ui, settings: data.settings || appState.settings });
          } else {
            // Merge by id: replace existing if id matches; otherwise append
            var cur = getState().recipes.slice();
            var idxById = {};
            cur.forEach(function(r, i){ idxById[r.id] = i; });
            imported.forEach(function(r){
              if(r && r.id && idxById.hasOwnProperty(r.id)){
                cur[idxById[r.id]] = r;
              } else if(r){
                cur.push(r);
              }
            });
            setState({ recipes: cur, settings: data.settings || appState.settings });
          }
          resolve(true);
        }catch(e){ reject(e); }
      };
      reader.onerror = function(){ reject(new Error('Read error')); };
      reader.readAsText(file);
    });
  }

  function copyIngredients(id){
    var r = getState().recipes.find(function(x){ return x.id===id; });
    if(!r) return;
    var text = (r.ingredients || []).join('\n');
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(function(){ /* ok */ }).catch(function(){ fallbackCopy(text); });
    } else {
      fallbackCopy(text);
    }
  }
  function fallbackCopy(text){
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch(e){}
    document.body.removeChild(ta);
  }

  function setFormErrors(errors){
    var ids = ['title','ingredients','instructions','tags'];
    ids.forEach(function(f){
      var input = document.getElementById(f);
      var err = document.getElementById('err-' + f);
      if(!input || !err) return;
      if(errors && errors[f]){
        input.classList.add('error');
        err.textContent = errors[f];
      } else {
        input.classList.remove('error');
        err.textContent = '';
      }
    });
    var formError = document.getElementById('formError');
    if(formError){
      var firstErrKey = errors ? Object.keys(errors)[0] : null;
      formError.textContent = firstErrKey ? errors[firstErrKey] : '';
    }
  }

  function resetForm(){
    var form = document.getElementById('recipeForm');
    if(form) form.reset();
    var hid = document.getElementById('recipeId');
    if(hid) hid.value = '';
    setFormErrors(null);
    var t = document.getElementById('title');
    if(t) t.focus();
  }

  function fillForm(r){
    document.getElementById('recipeId').value = r.id;
    document.getElementById('title').value = r.title || '';
    document.getElementById('ingredients').value = (r.ingredients || []).join('\n');
    document.getElementById('instructions').value = r.instructions || '';
    document.getElementById('tags').value = (r.tags || []).join(', ');
  }

  function onSubmitForm(e){
    e.preventDefault();
    var data = {
      title: (document.getElementById('title').value || '').trim(),
      ingredients: document.getElementById('ingredients').value || '',
      instructions: document.getElementById('instructions').value || '',
      tags: document.getElementById('tags').value || ''
    };
    var id = document.getElementById('recipeId').value;
    if(id){
      var resU = updateRecipe(id, data);
      if(!resU.ok){ setFormErrors(resU.errors || {_: resU.error || 'Update failed'}); return; }
      resetForm();
    } else {
      var res = addRecipe(data);
      if(!res.ok){ setFormErrors(res.errors || {_: 'Save failed'}); return; }
      resetForm();
    }
  }

  function renderTagFilter(){
    var sel = document.getElementById('tagFilter');
    if(!sel) return;
    var selected = sel.value || 'all';
    sel.innerHTML = '';
    var optAll = document.createElement('option');
    optAll.value = 'all'; optAll.textContent = 'All tags';
    sel.appendChild(optAll);
    getAllTags().forEach(function(t){
      var o = document.createElement('option');
      o.value = t; o.textContent = t;
      sel.appendChild(o);
    });
    sel.value = selected;
    if(!Array.prototype.some.call(sel.options, function(o){ return o.value===selected; })){
      sel.value = 'all';
    }
  }

  function renderList(){
    var listEl = document.getElementById('recipeList');
    var emptyEl = document.getElementById('emptyState');
    if(!listEl || !emptyEl) return;
    var list = currentFilteredSorted();

    listEl.innerHTML = '';
    if(list.length === 0){
      emptyEl.hidden = false; return;
    }
    emptyEl.hidden = true;

    var showPreview = !!getState().settings.showPreview;

    list.forEach(function(r){
      var li = document.createElement('li');
      li.className = 'item';
      li.setAttribute('data-id', r.id);

      var summary = document.createElement('div');
      summary.className = 'summary';

      var title = document.createElement('div');
      title.className = 'item-title';
      title.textContent = r.title;

      var badges = document.createElement('div');
      badges.className = 'badges';
      (r.tags || []).forEach(function(t){
        var b = document.createElement('span'); b.className = 'badge'; b.textContent = t; badges.appendChild(b);
      });

      summary.appendChild(title);
      if(showPreview){
        var prev = document.createElement('div');
        prev.className = 'item-preview';
        prev.textContent = firstInstructionLine(r.instructions || '');
        if(prev.textContent) summary.appendChild(prev);
      }
      summary.appendChild(badges);

      var actions = document.createElement('div');
      actions.className = 'actions';
      var copyBtn = document.createElement('button');
      copyBtn.className = 'small';
      copyBtn.textContent = 'Copy Ingredients';
      copyBtn.addEventListener('click', function(){ copyIngredients(r.id); });
      var editBtn = document.createElement('button');
      editBtn.className = 'small';
      editBtn.textContent = 'Edit';
      editBtn.addEventListener('click', function(){ fillForm(r); document.getElementById('title').focus(); });
      var delBtn = document.createElement('button');
      delBtn.className = 'small';
      delBtn.textContent = 'Delete';
      delBtn.addEventListener('click', function(){ if(confirm('Delete this recipe?')) deleteRecipe(r.id); });

      actions.appendChild(copyBtn);
      actions.appendChild(editBtn);
      actions.appendChild(delBtn);

      li.appendChild(summary);
      li.appendChild(actions);
      listEl.appendChild(li);
    });
  }

  function renderControls(){
    var s = getState();
    var searchInput = document.getElementById('searchInput');
    var tagFilter = document.getElementById('tagFilter');
    var sortSelect = document.getElementById('sortSelect');
    var showPreviewToggle = document.getElementById('showPreviewToggle');
    if(searchInput) searchInput.value = s.ui.search || '';
    renderTagFilter();
    if(tagFilter) tagFilter.value = s.ui.tagFilter || 'all';
    if(sortSelect) sortSelect.value = s.ui.sort || 'updatedAt_desc';
    if(showPreviewToggle) showPreviewToggle.checked = !!s.settings.showPreview;
  }

  function renderApp(){
    renderControls();
    renderList();
    var yearEl = document.getElementById('year');
    if(yearEl) yearEl.textContent = new Date().getFullYear();
  }

  function bindEvents(){
    var form = document.getElementById('recipeForm');
    if(form) form.addEventListener('submit', onSubmitForm);
    var resetBtn = document.getElementById('resetBtn');
    if(resetBtn) resetBtn.addEventListener('click', resetForm);

    var searchInput = document.getElementById('searchInput');
    if(searchInput) searchInput.addEventListener('input', function(e){
      setState({ ui: Object.assign({}, getState().ui, { search: e.target.value }) });
    });
    var tagFilter = document.getElementById('tagFilter');
    if(tagFilter) tagFilter.addEventListener('change', function(e){
      setState({ ui: Object.assign({}, getState().ui, { tagFilter: e.target.value }) });
    });
    var sortSelect = document.getElementById('sortSelect');
    if(sortSelect) sortSelect.addEventListener('change', function(e){
      setState({ ui: Object.assign({}, getState().ui, { sort: e.target.value }) });
    });
    var showPreviewToggle = document.getElementById('showPreviewToggle');
    if(showPreviewToggle) showPreviewToggle.addEventListener('change', function(e){
      setState({ settings: Object.assign({}, getState().settings, { showPreview: e.target.checked }) });
    });

    var exportBtn = document.getElementById('exportBtn');
    if(exportBtn) exportBtn.addEventListener('click', exportJSON);
    var importInput = document.getElementById('importInput');
    if(importInput) importInput.addEventListener('change', function(e){
      var file = e.target.files && e.target.files[0];
      if(!file) return;
      importJSON(file).then(function(){ e.target.value = ''; }).catch(function(err){
        alert('Import failed: ' + (err && err.message ? err.message : 'Unknown error'));
      });
    });
  }

  loadState();
  subscribe(renderApp);
  document.addEventListener('DOMContentLoaded', function(){
    bindEvents();
    renderApp();
    var t = document.getElementById('title');
    if(t) t.focus();
  });
})();
