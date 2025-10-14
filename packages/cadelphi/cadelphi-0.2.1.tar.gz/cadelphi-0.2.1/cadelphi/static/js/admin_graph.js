(function () {
  const config = window.__CADELPHI_GRAPH__;
  if (!config) return;

  const container = document.getElementById('graph-container');
  const metricSelect = document.getElementById('metric-select');
  const summaryRoot = document.getElementById('graph-summary');
  const argumentTable = document.getElementById('argument-table');

  if (!container || !metricSelect || !summaryRoot) {
    return;
  }

  const summaryTable = summaryRoot.querySelector('tbody');
  if (!summaryTable) {
    return;
  }

  const tableBody = argumentTable ? argumentTable.querySelector('tbody') : null;
  const tableHeaders = argumentTable ? Array.from(argumentTable.querySelectorAll('th[data-sort]')) : [];
  const searchInput = document.getElementById('argument-search');
  const exportButton = document.getElementById('argument-export');
  const columnCount = argumentTable ? argumentTable.querySelectorAll('thead th').length : 0;

  let network;
  let tableData = [];
  let currentSort = { key: 'topic', direction: 'asc' };

  async function fetchJson(url) {
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || config.errorMessage || 'Unable to fetch data.');
    }
    return response.json();
  }

  function formatNumber(value) {
    if (value === null || value === undefined || Number.isNaN(value)) {
      return '';
    }
    return Number(value).toFixed(2);
  }

  function renderGraph(data, metric) {
    const nodes = new vis.DataSet(data.nodes || []);
    const edges = new vis.DataSet(
      (data.edges || []).map((edge) => {
        const value = edge[metric] || 0;
        return {
          from: edge.source,
          to: edge.target,
          value,
          width: Math.max(1, value),
          label: value ? (typeof value === 'number' && value.toFixed ? value.toFixed(2) : value) : '',
          arrows: 'to',
        };
      })
    );

    const options = {
      edges: {
        scaling: {
          min: 1,
          max: 8,
        },
        smooth: true,
        color: {
          color: '#2f80ed',
          highlight: '#0f62fe',
        },
      },
      nodes: {
        shape: 'box',
        margin: 12,
        widthConstraint: {
          maximum: 320,
        },
        color: {
          background: '#ffffff',
          border: '#2f80ed',
          highlight: {
            background: '#2f80ed',
            border: '#0b0d17',
          },
        },
        font: {
          multi: true,
        },
      },
      physics: {
        solver: 'forceAtlas2Based',
        stabilization: true,
      },
    };

    if (network) {
      network.destroy();
    }
    network = new vis.Network(container, { nodes, edges }, options);
  }

  function updateHeaderIndicators() {
    if (!tableHeaders.length) return;
    tableHeaders.forEach((header) => {
      header.classList.remove('sort-asc', 'sort-desc');
      if (header.dataset.sort === currentSort.key) {
        header.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
      }
    });
  }

  function getFilteredData() {
    if (!tableData.length) {
      return [];
    }
    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
    if (!query) {
      return [...tableData];
    }
    return tableData.filter((item) => {
      const topic = (item.topic || '').toLowerCase();
      const content = (item.content || '').toLowerCase();
      const matchesVotes = (item.votes || []).some((vote) => {
        const participant = (vote.participant || '').toLowerCase();
        const comment = (vote.comment || '').toLowerCase();
        return participant.includes(query) || comment.includes(query);
      });
      return topic.includes(query) || content.includes(query) || matchesVotes;
    });
  }

  function sortItems(items) {
    const sorted = [...items];
    const { key, direction } = currentSort;
    sorted.sort((a, b) => {
      let valueA;
      let valueB;

      switch (key) {
        case 'argument':
          valueA = (a.content || '').toLowerCase();
          valueB = (b.content || '').toLowerCase();
          return valueA.localeCompare(valueB);
        case 'votes':
          valueA = a.vote_count || 0;
          valueB = b.vote_count || 0;
          break;
        case 'average':
          valueA = typeof a.average === 'number' ? a.average : Number.NEGATIVE_INFINITY;
          valueB = typeof b.average === 'number' ? b.average : Number.NEGATIVE_INFINITY;
          break;
        case 'highest':
          valueA = typeof a.max === 'number' ? a.max : Number.NEGATIVE_INFINITY;
          valueB = typeof b.max === 'number' ? b.max : Number.NEGATIVE_INFINITY;
          break;
        case 'lowest':
          valueA = typeof a.min === 'number' ? a.min : Number.POSITIVE_INFINITY;
          valueB = typeof b.min === 'number' ? b.min : Number.POSITIVE_INFINITY;
          break;
        case 'topic':
        default:
          valueA = (a.topic || '').toLowerCase();
          valueB = (b.topic || '').toLowerCase();
          return valueA.localeCompare(valueB);
      }

      if (valueA < valueB) return -1;
      if (valueA > valueB) return 1;
      return 0;
    });

    if (direction === 'desc') {
      sorted.reverse();
    }
    return sorted;
  }

  function renderVoteDetails(votes) {
    const wrapper = document.createElement('div');
    wrapper.className = 'vote-details';

    votes.forEach((vote) => {
      const entry = document.createElement('div');
      entry.className = 'vote-details-entry';

      const score = document.createElement('strong');
      score.textContent = `${vote.score}/5`;
      entry.appendChild(score);

      const participant = document.createElement('span');
      participant.textContent = `· ${vote.participant}`;
      entry.appendChild(participant);

      wrapper.appendChild(entry);

      if (vote.comment) {
        const comment = document.createElement('div');
        comment.className = 'vote-comment';
        comment.textContent = `${config.voteCommentLabel}: ${vote.comment}`;
        wrapper.appendChild(comment);
      }
    });

    return wrapper;
  }

  function updateTable() {
    if (!tableBody) return;

    const filtered = getFilteredData();
    const sorted = sortItems(filtered);

    tableBody.innerHTML = '';
    updateHeaderIndicators();

    if (!sorted.length) {
      const hasQuery = searchInput && searchInput.value.trim();
      const message = hasQuery ? config.tableNoMatch : config.tableNoData;
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = columnCount || 1;
      td.textContent = message;
      tr.appendChild(td);
      tableBody.appendChild(tr);
      return;
    }

    sorted.forEach((item) => {
      const tr = document.createElement('tr');

      const topicCell = document.createElement('td');
      topicCell.textContent = item.topic || '';
      tr.appendChild(topicCell);

      const argumentCell = document.createElement('td');
      argumentCell.textContent = item.content || '';
      tr.appendChild(argumentCell);

      const votesCell = document.createElement('td');
      const voteSummary = document.createElement('div');
      voteSummary.className = 'vote-summary';
      voteSummary.textContent = item.vote_count || 0;
      votesCell.appendChild(voteSummary);
      if (item.votes && item.votes.length) {
        const details = document.createElement('details');
        const summary = document.createElement('summary');
        summary.textContent = config.voteSummaryLabel.replace('{count}', item.vote_count);
        details.appendChild(summary);
        details.appendChild(renderVoteDetails(item.votes));
        votesCell.appendChild(details);
      }
      tr.appendChild(votesCell);

      const avgCell = document.createElement('td');
      avgCell.textContent = item.average !== null && item.average !== undefined ? formatNumber(item.average) : '';
      tr.appendChild(avgCell);

      const maxCell = document.createElement('td');
      maxCell.textContent = item.max !== null && item.max !== undefined ? item.max : '';
      tr.appendChild(maxCell);

      const minCell = document.createElement('td');
      minCell.textContent = item.min !== null && item.min !== undefined ? item.min : '';
      tr.appendChild(minCell);

      tableBody.appendChild(tr);
    });
  }

  function getTableHeadersText() {
    if (!argumentTable) return [];
    return Array.from(argumentTable.querySelectorAll('thead th')).map((th) => th.textContent.trim());
  }

  function toCsvValue(value) {
    const stringValue = value === undefined || value === null ? '' : String(value);
    if (/[",\n]/.test(stringValue)) {
      return `"${stringValue.replace(/"/g, '""')}"`;
    }
    return stringValue;
  }

  function buildVoteSummary(votes) {
    if (!votes || !votes.length) {
      return '';
    }
    return votes
      .map((vote) => {
        const comment = vote.comment ? ` (${vote.comment})` : '';
        return `${vote.score}/5 ${vote.participant}${comment}`;
      })
      .join(' | ');
  }

  function exportCsv() {
    const filtered = sortItems(getFilteredData());
    if (!filtered.length) {
      return;
    }

    const headers = getTableHeadersText();
    const csvRows = [headers.concat(config.voteCommentLabel).map(toCsvValue).join(',')];

    filtered.forEach((item) => {
      const row = [
        item.topic || '',
        item.content || '',
        item.vote_count || 0,
        item.average !== null && item.average !== undefined ? formatNumber(item.average) : '',
        item.max !== null && item.max !== undefined ? item.max : '',
        item.min !== null && item.min !== undefined ? item.min : '',
        buildVoteSummary(item.votes),
      ];
      csvRows.push(row.map(toCsvValue).join(','));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = config.exportFileName || 'cadelphi_argument_votes.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async function loadTable() {
    if (!tableBody) return;
    const loadingRow = document.createElement('tr');
    const loadingCell = document.createElement('td');
    loadingCell.colSpan = columnCount || 1;
    loadingCell.textContent = config.tableLoading;
    loadingRow.appendChild(loadingCell);
    tableBody.innerHTML = '';
    tableBody.appendChild(loadingRow);

    try {
      const data = await fetchJson(config.tableEndpoint);
      tableData = data.items || [];
      updateTable();
    } catch (error) {
      const message = error.message || config.tableErrorMessage || config.errorMessage;
      tableBody.innerHTML = '';
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = columnCount || 1;
      td.textContent = message;
      tr.appendChild(td);
      tableBody.appendChild(tr);
    }
  }

  async function updateSummary() {
    try {
      const summary = await fetchJson(config.summaryEndpoint);
      summaryTable.innerHTML = '';
      (summary.items || []).forEach((item) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${item.title}</td><td>${item.content}</td><td>${item.value}</td>`;
        summaryTable.appendChild(tr);
      });
    } catch (error) {
      const message = error.message || config.summaryErrorMessage || config.errorMessage;
      summaryTable.innerHTML = `<tr><td colspan="3">${message}</td></tr>`;
    }
  }

  async function load(metric) {
    try {
      const data = await fetchJson(`${config.dataEndpoint}?metric=${metric}`);
      renderGraph(data, metric);
    } catch (error) {
      const message = error.message || config.errorMessage;
      container.innerHTML = `<p class="alert error">${message}</p>`;
    }
  }

  metricSelect.addEventListener('change', (event) => {
    const metric = event.target.value;
    load(metric);
  });

  if (tableHeaders.length) {
    tableHeaders.forEach((header) => {
      header.addEventListener('click', () => {
        const sortKey = header.dataset.sort;
        if (!sortKey) return;
        if (currentSort.key === sortKey) {
          currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
          currentSort = { key: sortKey, direction: 'asc' };
        }
        updateTable();
      });
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      updateTable();
    });
  }

  if (exportButton) {
    exportButton.addEventListener('click', exportCsv);
  }

  load(metricSelect.value);
  updateSummary();
  loadTable();
})();
