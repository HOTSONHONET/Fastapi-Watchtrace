import { useCallback, useEffect, useMemo, useState } from "react";
import ReactFlow, { Background, Controls, MiniMap } from "reactflow";
import JsonView from "@uiw/react-json-view";
import { vscodeTheme } from "@uiw/react-json-view/vscode";
import "reactflow/dist/style.css";
import "./App.css";

const PAGE_SIZE = 10;

function formatDateTime(value) {
  if (value == null) return "N/A";

  try {
    const timestamp =
      typeof value === "number" ? value * 1000 : new Date(value).getTime();

    if (Number.isNaN(timestamp)) return "N/A";
    return new Date(timestamp).toLocaleString();
  } catch {
    return "N/A";
  }
}

function formatDuration(value) {
  if (value == null || Number.isNaN(Number(value))) return "N/A";
  return `${Number(value).toFixed(2)} ms`;
}

function normalizeRequestItem(item) {
  return {
    request_id: item.request_id ?? "",
    method: item.method ?? "GET",
    path: item.path ?? "N/A",
    duration_ms: item.duration_ms ?? 0,
    created_at: item.created_at ?? null,
    raw: item,
  };
}

function buildTreeLayout(nodes, edges) {
  if (!nodes.length) return nodes;

  const childrenMap = new Map();
  const indegree = new Map();

  nodes.forEach((node) => {
    childrenMap.set(node.id, []);
    indegree.set(node.id, 0);
  });

  edges.forEach((edge) => {
    if (childrenMap.has(edge.source)) {
      childrenMap.get(edge.source).push(edge.target);
    }
    indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1);
  });

  const roots = nodes
    .filter((node) => (indegree.get(node.id) ?? 0) === 0)
    .map((node) => node.id);

  const levelMap = new Map();
  const queue = [...roots];

  roots.forEach((id) => levelMap.set(id, 0));

  while (queue.length) {
    const current = queue.shift();
    const currentLevel = levelMap.get(current) ?? 0;
    const children = childrenMap.get(current) ?? [];

    children.forEach((childId) => {
      if (!levelMap.has(childId)) {
        levelMap.set(childId, currentLevel + 1);
        queue.push(childId);
      }
    });
  }

  const grouped = new Map();
  nodes.forEach((node) => {
    const level = levelMap.get(node.id) ?? 0;
    if (!grouped.has(level)) grouped.set(level, []);
    grouped.get(level).push(node.id);
  });

  const spacingX = 280;
  const spacingY = 120;

  const positioned = nodes.map((node) => {
    const level = levelMap.get(node.id) ?? 0;
    const idsAtLevel = grouped.get(level) ?? [];
    const indexAtLevel = idsAtLevel.indexOf(node.id);

    return {
      ...node,
      position: {
        x: level * spacingX,
        y: indexAtLevel * spacingY,
      },
    };
  });

  return positioned;
}

function normalizeGraphResponse(graphResponse) {
  const rawNodes = Array.isArray(graphResponse?.nodes) ? graphResponse.nodes : [];
  const rawEdges = Array.isArray(graphResponse?.edges) ? graphResponse.edges : [];

  const nodes = rawNodes.map((node, index) => ({
    id: String(node.id ?? `node-${index}`),
    data: {
      label: (
        <div className="flow-node-content">
          <div className="flow-node-title">
            {node.label ?? node.full_name ?? node.id ?? "Node"}
          </div>
          <div className="flow-node-subtitle">{formatDuration(node.duration)}</div>
        </div>
      ),
      raw: node,
    },
    position: { x: 0, y: 0 },
    style: {
      borderRadius: 16,
      padding: 12,
      border: "1px solid rgba(255,255,255,0.12)",
      minWidth: 220,
      background: "#f8fafc",
      color: "#111827",
      fontWeight: 600,
      boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
    },
  }));

  const edges = rawEdges.map((edge, index) => ({
    id: String(edge.id ?? `edge-${index}`),
    source: String(edge.source),
    target: String(edge.target),
    animated: false,
    style: { stroke: "#94a3b8" },
  }));

  return {
    nodes: buildTreeLayout(nodes, edges),
    edges,
    raw: graphResponse,
  };
}

function shouldHideRequest(path) {
  if (!path) return false;

  return (
    path.startsWith("/__watchtower") ||
    path === "/docs" ||
    path === "/openapi.json" ||
    path === "/favicon.ico"
  );
}

export default function App() {
  const [requests, setRequests] = useState([]);
  const [loadingRequests, setLoadingRequests] = useState(false);
  const [requestsError, setRequestsError] = useState("");

  const [selectedRequest, setSelectedRequest] = useState(null);
  const [selectedDetails, setSelectedDetails] = useState(null);

  const [graphNodes, setGraphNodes] = useState([]);
  const [graphEdges, setGraphEdges] = useState([]);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [graphError, setGraphError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [pathFilter, setPathFilter] = useState("");
  const [methodFilter, setMethodFilter] = useState("");
  const [fromDateTime, setFromDateTime] = useState("");
  const [toDateTime, setToDateTime] = useState("");
  const [page, setPage] = useState(1);

  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);

  const fetchRequests = useCallback(async () => {
    setLoadingRequests(true);
    setRequestsError("");

    try {
      const res = await fetch("/__watchtower/api/requests");
      if (!res.ok) {
        throw new Error(`Failed to fetch requests: ${res.status}`);
      }

      const data = await res.json();
      const list = Array.isArray(data?.requests) ? data.requests : [];
      setRequests(list.map(normalizeRequestItem));
    } catch (err) {
      setRequestsError(err.message || "Failed to load requests");
    } finally {
      setLoadingRequests(false);
    }
  }, []);

  const fetchGraph = useCallback(async (requestId) => {
    if (!requestId) return;

    setLoadingGraph(true);
    setGraphError("");

    try {
      const res = await fetch(`/__watchtower/api/requests/${requestId}/graph`);
      if (!res.ok) {
        throw new Error(`Failed to fetch graph: ${res.status}`);
      }

      const data = await res.json();
      const normalized = normalizeGraphResponse(data);

      setGraphNodes(normalized.nodes);
      setGraphEdges(normalized.edges);
      setSelectedDetails(data);
    } catch (err) {
      setGraphNodes([]);
      setGraphEdges([]);
      setGraphError(err.message || "Failed to load graph");
    } finally {
      setLoadingGraph(false);
    }
  }, []);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  const methods = useMemo(() => {
    return [...new Set(requests.map((r) => r.method).filter(Boolean))];
  }, [requests]);

  const filteredRequests = useMemo(() => {
    return requests
      .filter((req) => !shouldHideRequest(req.path))
      .filter((req) => {
        const q = searchTerm.trim().toLowerCase();
        const p = pathFilter.trim().toLowerCase();

        const matchesSearch =
          !q ||
          req.request_id.toLowerCase().includes(q) ||
          req.path.toLowerCase().includes(q) ||
          req.method.toLowerCase().includes(q);

        const matchesPath = !p || req.path.toLowerCase().includes(p);
        const matchesMethod = !methodFilter || req.method === methodFilter;

        const reqTime = req.created_at ? req.created_at * 1000 : null;
        const fromTime = fromDateTime ? new Date(fromDateTime).getTime() : null;
        const toTime = toDateTime ? new Date(toDateTime).getTime() : null;

        const matchesFrom = !fromTime || (reqTime != null && reqTime >= fromTime);
        const matchesTo = !toTime || (reqTime != null && reqTime <= toTime);

        return matchesSearch && matchesPath && matchesMethod && matchesFrom && matchesTo;
      });
  }, [requests, searchTerm, pathFilter, methodFilter, fromDateTime, toDateTime]);

  const totalPages = Math.max(1, Math.ceil(filteredRequests.length / PAGE_SIZE));

  const paginatedRequests = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredRequests.slice(start, start + PAGE_SIZE);
  }, [filteredRequests, page]);

  useEffect(() => {
    if (page > totalPages) setPage(1);
  }, [page, totalPages]);

  const handleSelectRequest = async (req) => {
    setSelectedRequest(req);
    setSelectedDetails(req.raw);
    await fetchGraph(req.request_id);
  };

  const handleRefreshSelected = async () => {
    if (!selectedRequest?.request_id) return;
    await fetchGraph(selectedRequest.request_id);
  };

  const clearFilters = () => {
    setSearchTerm("");
    setPathFilter("");
    setMethodFilter("");
    setFromDateTime("");
    setToDateTime("");
    setPage(1);
  };

  const onNodeClick = useCallback(
    (_, node) => {
      setSelectedDetails(node?.data?.raw ?? node);
      if (!isRightPanelOpen) {
        setIsRightPanelOpen(true);
      }
    },
    [isRightPanelOpen]
  );

  return (
    <div className="app-shell">
      <aside className="left-sidebar">
        <div className="brand-block">
          <h1>WatchTower</h1>
          <p>Request Catalog</p>
        </div>

        <div className="filter-group">
          <input
            type="text"
            placeholder="Search request id, path, method..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
          />

          <input
            type="text"
            placeholder="Filter by path..."
            value={pathFilter}
            onChange={(e) => {
              setPathFilter(e.target.value);
              setPage(1);
            }}
          />

          <select
            value={methodFilter}
            onChange={(e) => {
              setMethodFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All methods</option>
            {methods.map((method) => (
              <option key={method} value={method}>
                {method}
              </option>
            ))}
          </select>

          <div className="field-label">From datetime</div>
          <input
            type="datetime-local"
            value={fromDateTime}
            onChange={(e) => {
              setFromDateTime(e.target.value);
              setPage(1);
            }}
          />

          <div className="field-label">To datetime</div>
          <input
            type="datetime-local"
            value={toDateTime}
            onChange={(e) => {
              setToDateTime(e.target.value);
              setPage(1);
            }}
          />

          <div className="filter-actions">
            <button onClick={clearFilters}>Clear filters</button>
            <button onClick={fetchRequests}>Refresh list</button>
          </div>
        </div>

        <div className="request-count">
          {loadingRequests ? "Loading requests..." : `${filteredRequests.length} request(s)`}
        </div>

        {requestsError ? (
          <div className="error-box">{requestsError}</div>
        ) : (
          <div className="request-list">
            {paginatedRequests.map((req) => {
              const isActive = selectedRequest?.request_id === req.request_id;
              return (
                <button
                  key={req.request_id}
                  className={`request-card ${isActive ? "active" : ""}`}
                  onClick={() => handleSelectRequest(req)}
                >
                  <div className="request-id">{req.request_id}</div>
                  <div className="request-meta">
                    {req.method} {req.path}
                  </div>
                  <div className="request-submeta">
                    <span>{formatDateTime(req.created_at)}</span>
                    <span>{formatDuration(req.duration_ms)}</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        <div className="pagination-bar">
          <span>
            Page {page} / {totalPages}
          </span>
          <div className="pagination-actions">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      </aside>

      <main className="graph-area">
        <div className="graph-toolbar">
          <button
            onClick={handleRefreshSelected}
            disabled={!selectedRequest || loadingGraph}
          >
            {loadingGraph ? "Refreshing..." : "Refresh selected graph"}
          </button>
        </div>

        {graphError ? (
          <div className="graph-empty-state">{graphError}</div>
        ) : graphNodes.length === 0 ? (
          <div className="graph-empty-state">
            Select a request from the left panel to view its call graph.
          </div>
        ) : (
          <ReactFlow
            nodes={graphNodes}
            edges={graphEdges}
            fitView
            onNodeClick={onNodeClick}
          >
            <Background gap={22} size={1} />
            <MiniMap />
            <Controls />
          </ReactFlow>
        )}
      </main>

      <aside className={`right-sidebar ${isRightPanelOpen ? "open" : "collapsed"}`}>
        <button
          className="toggle-details-btn"
          onClick={() => setIsRightPanelOpen((prev) => !prev)}
          title={isRightPanelOpen ? "Collapse details" : "Expand details"}
        >
          {isRightPanelOpen ? "⟩" : "⟨"}
        </button>

        {isRightPanelOpen && (
          <div className="details-panel">
            <div className="details-header">
              <h2>Request Details</h2>
            </div>

            {selectedRequest && (
              <div className="selected-request-text">
                Selected request: <strong>{selectedRequest.request_id}</strong>
              </div>
            )}

            <div className="json-panel">
              <JsonView value={selectedDetails ?? {}} style={vscodeTheme} />
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}