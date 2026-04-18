// app.js — AI Concepts Visual Dataset UI
(function () {
  'use strict';

  let concepts = window.CONCEPTS.map(c => Object.assign({}, c));
  let selectedId = null;

  const $ = id => document.getElementById(id);

  // ---- Stats ----
  function renderStats(data) {
    const total = data.length;
    const good = data.filter(c => c.label === 'good').length;
    const bad = data.filter(c => c.label === 'bad').length;
    const pending = data.filter(c => c.label === 'pending').length;

    $('count-badge').textContent = `${total} entries`;
    $('stats-row').innerHTML = `
      <div class="stat-card">
        <span class="stat-n">${total}</span>
        <span class="stat-l">Total concepts</span>
      </div>
      <div class="stat-card">
        <span class="stat-n" style="color:var(--good)">${good}</span>
        <span class="stat-l">Good design</span>
      </div>
      <div class="stat-card">
        <span class="stat-n" style="color:var(--bad)">${bad}</span>
        <span class="stat-l">Bad design</span>
      </div>
      <div class="stat-card">
        <span class="stat-n" style="color:var(--pending)">${pending}</span>
        <span class="stat-l">Pending review</span>
      </div>`;
  }

  // ---- Filter & Sort ----
  function filtered() {
    const q = $('search').value.toLowerCase();
    const cat = $('cat-filter').value;
    const lbl = $('label-filter').value;
    const sort = $('sort-by').value;

    let data = concepts.filter(c => {
      const matchQ = !q ||
        c.title.toLowerCase().includes(q) ||
        c.summary.toLowerCase().includes(q) ||
        c.tags.some(t => t.toLowerCase().includes(q));
      const matchC = !cat || c.category === cat;
      const matchL = !lbl || c.label === lbl;
      return matchQ && matchC && matchL;
    });

    data.sort((a, b) => {
      if (sort === 'title') return a.title.localeCompare(b.title);
      if (sort === 'category') return a.category.localeCompare(b.category);
      return a.id.localeCompare(b.id);
    });

    return data;
  }

  // ---- Badge HTML ----
  function badgeHtml(label) {
    const map = { good: 'Good', bad: 'Bad', pending: 'Pending' };
    return `<span class="badge badge-${label}">${map[label] || label}</span>`;
  }

  // ---- Grid ----
  function renderGrid() {
    const data = filtered();
    renderStats(data);

    if (data.length === 0) {
      $('grid').innerHTML = `<div class="empty">No concepts match your filters.</div>`;
      return;
    }

    $('grid').innerHTML = data.map(c => `
      <div class="card${selectedId === c.id ? ' active' : ''}" data-id="${c.id}" role="button" tabindex="0">
        <div class="card-top">
          <span class="card-title">${c.title}</span>
          ${badgeHtml(c.label)}
        </div>
        <div class="card-cat">${c.category} · ${c.metadata.complexity}</div>
        <div class="card-summary">${c.summary.slice(0, 90)}${c.summary.length > 90 ? '…' : ''}</div>
        <div class="card-footer">
          <span class="card-tag">${c.tags[0]}</span>
          <span class="card-id">#${c.id}</span>
        </div>
      </div>`).join('');

    $('grid').querySelectorAll('.card').forEach(el => {
      el.addEventListener('click', () => openDetail(el.dataset.id));
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openDetail(el.dataset.id); });
    });
  }

  // ---- Detail Panel ----
  function openDetail(id) {
    const c = concepts.find(x => x.id === id);
    if (!c) return;
    selectedId = id;

    const relatedHtml = (c.metadata.related_concepts || []).map(rid => {
      const rel = concepts.find(x => x.id === rid);
      return rel ? `<span class="related-chip" data-id="${rid}">#${rid} ${rel.title}</span>` : '';
    }).join('');

    const notesHtml = c.metadata.annotation_notes
      ? `<dt>Annotation notes</dt><dd>${c.metadata.annotation_notes}</dd>` : '';

    const lbtn = lbl => `<button class="lbtn ${c.label === lbl ? 'active-' + lbl : ''}" data-label="${lbl}" data-id="${c.id}">${
      { good: 'Good design', bad: 'Bad design', pending: 'Pending' }[lbl]
    }</button>`;

    const panel = $('detail-panel');
    panel.setAttribute('aria-hidden', 'false');
    $('detail-inner').innerHTML = `
      <div class="detail-header">
        <div>
          <div class="detail-title">${c.title}</div>
          <div class="detail-sub">${c.category} &nbsp;·&nbsp; #${c.id} &nbsp;·&nbsp; ${c.metadata.complexity}</div>
        </div>
        <button class="btn btn-close" id="close-btn">✕ Close</button>
      </div>
      <dl class="detail-grid">
        <dt>Summary</dt><dd>${c.summary}</dd>
        <dt>Source</dt><dd>${c.metadata.source || '—'}</dd>
        <dt>Tags</dt><dd><div class="tags-list">${c.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div></dd>
        <dt>Quality label</dt><dd><div class="label-row">${lbtn('good')}${lbtn('bad')}${lbtn('pending')}</div></dd>
        ${relatedHtml ? `<dt>Related</dt><dd><div class="related-list">${relatedHtml}</div></dd>` : ''}
        ${notesHtml}
      </dl>
      <div class="visual-block">${c.visual_description}</div>
      <div class="actions">
        <a class="btn" href="https://www.google.com/search?q=${encodeURIComponent(c.title + ' machine learning')}" target="_blank" rel="noopener">Search paper ↗</a>
        <button class="btn" id="copy-entry-btn">Copy JSON</button>
      </div>`;

    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Events
    $('close-btn').onclick = closeDetail;
    $('copy-entry-btn').onclick = () => {
      navigator.clipboard.writeText(JSON.stringify(c, null, 2));
      $('copy-entry-btn').textContent = 'Copied!';
      setTimeout(() => { $('copy-entry-btn').textContent = 'Copy JSON'; }, 1500);
    };

    panel.querySelectorAll('.lbtn').forEach(btn => {
      btn.addEventListener('click', () => {
        const entry = concepts.find(x => x.id === btn.dataset.id);
        if (entry) { entry.label = btn.dataset.label; }
        renderGrid();
        openDetail(id);
      });
    });

    panel.querySelectorAll('.related-chip').forEach(chip => {
      chip.addEventListener('click', () => openDetail(chip.dataset.id));
    });

    renderGrid();
  }

  function closeDetail() {
    selectedId = null;
    $('detail-panel').setAttribute('aria-hidden', 'true');
    $('detail-inner').innerHTML = '';
    renderGrid();
  }

  // ---- Event Listeners ----
  $('search').addEventListener('input', renderGrid);
  $('cat-filter').addEventListener('change', renderGrid);
  $('label-filter').addEventListener('change', renderGrid);
  $('sort-by').addEventListener('change', renderGrid);

  // ---- Init ----
  renderGrid();
})();
