(function () {
  const config = window.__CADELPHI_GRAPH__;
  if (!config) return;

  const container = document.getElementById('graph-container');
  const metricSelect = document.getElementById('metric-select');
  const summaryRoot = document.getElementById('graph-summary');
  if (!container || !metricSelect || !summaryRoot) {
    return;
  }
  const summaryTable = summaryRoot.querySelector('tbody');
  let network;

  async function fetchJson(url) {
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || config.errorMessage || 'Unable to fetch data.');
    }
    return response.json();
  }

  function renderGraph(data, metric) {
    if (!container) return;
    const nodes = new vis.DataSet(data.nodes || []);
    const edges = new vis.DataSet(
      (data.edges || []).map((edge) => {
        const value = edge[metric] || 0;
        return {
          from: edge.source,
          to: edge.target,
          value,
          width: Math.max(1, value),
          label: value ? value.toFixed ? value.toFixed(2) : value : '',
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

  load(metricSelect.value);
  updateSummary();
})();
