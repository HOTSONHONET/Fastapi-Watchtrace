import { useEffect, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";

const API_BASE = "http://localhost:8000/__watchtower/api";
const PAGE_SIZE = 10;

function formatDuration(value) {
  if (value === null || value === undefined) return "N/A";

  const num = Number(value);
  if (Number.isNaN(num)) return String(value);

  // Request nodes may be in ms, function nodes may be in us.
  if (num > 1000) {
    return `${(num / 1000).toFixed(2)} ms`;
  }
  return `${num.toFixed(2)} ms`;
}

function buildVerticalLayout(graphData) {
  const spacingY = 140;
  const centerX = 320;

  const incomingCount = {};
  graphData.nodes.forEach((node) => {
    incomingCount[node.id] = 0;
  });

  graphData.edges.forEach((edge) => {
    incomingCount[edge.target] = (incomingCount[edge.target] || 0) + 1;
  });

  const roots = graphData.nodes.filter((node) => incomingCount[node.id] === 0);
  const visited = new Set();
  const ordered = [];

  function dfs(nodeId) {
    if (visited.has(nodeId)) return;
    visited.add(nodeId);

    const node = graphData.nodes.find((n) => n.id === nodeId);
    if (node) ordered.push(node);

    const children = graphData.edges
      .filter((e) => e.source === nodeId)
      .map((e) => e.target);

    children.forEach(dfs);
  }

  roots.forEach((root) => dfs(root.id));
  graphData.nodes.forEach((node) => dfs(node.id));

  return ordered.map((node, index) => ({
    id: node.id,
    data: {
      label: node.label,
      meta: node,
    },
    position: { x: centerX, y: index * spacingY },
    style: {
      padding: 12,
      minWidth: 220,
      textAlign: "center",
      borderRadius: 10,
      border: "1px solid #999",
      background: node.type === "request" ? "#ffffff" : "#f7f7f7",
      color: "#111827",
      fontWeight: 500,
    },
    type: "default",
  }));
}

export default function App() {
  const [requestIds, setRequestIds] = useState([]);
  const [selectedRequestId, setSelectedRequestId] = useState("");
  const [graph, setGraph] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const [loadingRequests, setLoadingRequests] = useState(true);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [error, setError] = useState("");

  async function loadRequests() {
    try {
      setLoadingRequests(true);
      setError("");

      const res = await fetch(`${API_BASE}/requests`);
      if (!res.ok) {
        throw new Error(`Failed to fetch requests: ${res.status}`);
      }

      const data = await res.json();
      const ids = data.requests || [];
      setRequestIds(ids);

      if (ids.length > 0 && !selectedRequestId) {
        setSelectedRequestId(ids[0]);
      }
    } catch (err) {
      setError(err.message || "Failed to load requests");
    } finally {
      setLoadingRequests(false);
    }
  }

  async function loadGraphForRequest(requestId) {
    if (!requestId) return;

    try {
      setLoadingGraph(true);
      setError("");
      setSelectedNode(null);

      const res = await fetch(`${API_BASE}/requests/${requestId}/graph`);
      if (!res.ok) {
        throw new Error(`Failed to fetch graph for ${requestId}: ${res.status}`);
      }

      const data = await res.json();
      setGraph(data);
    } catch (err) {
      setError(err.message || "Failed to load graph");
      setGraph(null);
    } finally {
      setLoadingGraph(false);
    }
  }

  useEffect(() => {
    loadRequests();
  }, []);

  useEffect(() => {
    if (selectedRequestId) {
      loadGraphForRequest(selectedRequestId);
    }
  }, [selectedRequestId]);

  const filteredRequestIds = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return requestIds;
    return requestIds.filter((id) => id.toLowerCase().includes(q));
  }, [requestIds, search]);

  const totalPages = Math.max(1, Math.ceil(filteredRequestIds.length / PAGE_SIZE));

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const paginatedRequestIds = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredRequestIds.slice(start, start + PAGE_SIZE);
  }, [filteredRequestIds, page]);

  const nodes = useMemo(() => {
    if (!graph) return [];
    return buildVerticalLayout(graph).map((node) => ({
      ...node,
      data: {
        ...node.data,
        label: (
          <div>
            <div style={{ fontSize: 15, fontWeight: 700 }}>{node.data.meta.label}</div>
            <div style={{ marginTop: 8, fontSize: 13, opacity: 0.85 }}>
              {formatDuration(node.data.meta.duration)}
            </div>
          </div>
        ),
      },
    }));
  }, [graph]);

  const edges = useMemo(() => {
    if (!graph) return [];
    return graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      animated: false,
    }));
  }, [graph]);

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", background: "#0f172a" }}>
      <div
        style={{
          width: 340,
          borderRight: "1px solid #1f2937",
          background: "#111827",
          color: "#e5e7eb",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ padding: 16, borderBottom: "1px solid #1f2937" }}>
          <h2 style={{ margin: 0, fontSize: 22 }}>WatchTower</h2>
          <div style={{ marginTop: 8, fontSize: 13, opacity: 0.8 }}>
            Request Catalog
          </div>
        </div>

        <div style={{ padding: 16, borderBottom: "1px solid #1f2937" }}>
          <input
            type="text"
            placeholder="Search request id..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 8,
              border: "1px solid #374151",
              background: "#0b1220",
              color: "#e5e7eb",
              outline: "none",
            }}
          />
          <button
            onClick={loadRequests}
            style={{
              marginTop: 10,
              width: "100%",
              padding: "10px 12px",
              borderRadius: 8,
              border: "1px solid #374151",
              background: "#1f2937",
              color: "#e5e7eb",
              cursor: "pointer",
            }}
          >
            Refresh request list
          </button>
        </div>

        <div style={{ padding: "10px 16px", fontSize: 13, opacity: 0.8 }}>
          {loadingRequests
            ? "Loading requests..."
            : `${filteredRequestIds.length} request(s)`}
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "0 12px 12px 12px" }}>
          {paginatedRequestIds.map((requestId) => {
            const active = requestId === selectedRequestId;
            return (
              <button
                key={requestId}
                onClick={() => setSelectedRequestId(requestId)}
                style={{
                  width: "100%",
                  textAlign: "left",
                  marginBottom: 8,
                  padding: 12,
                  borderRadius: 10,
                  border: active ? "1px solid #60a5fa" : "1px solid #374151",
                  background: active ? "#1e3a8a" : "#111827",
                  color: "#e5e7eb",
                  cursor: "pointer",
                  wordBreak: "break-all",
                }}
              >
                {requestId}
              </button>
            );
          })}

          {!loadingRequests && paginatedRequestIds.length === 0 && (
            <div style={{ padding: 12, opacity: 0.8 }}>No matching requests.</div>
          )}
        </div>

        <div
          style={{
            borderTop: "1px solid #1f2937",
            padding: 12,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
          }}
        >
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{
              padding: "8px 12px",
              borderRadius: 8,
              border: "1px solid #374151",
              background: page === 1 ? "#111827" : "#1f2937",
              color: "#e5e7eb",
              cursor: page === 1 ? "not-allowed" : "pointer",
            }}
          >
            Prev
          </button>

          <div style={{ fontSize: 13 }}>
            Page {page} / {totalPages}
          </div>

          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            style={{
              padding: "8px 12px",
              borderRadius: 8,
              border: "1px solid #374151",
              background: page === totalPages ? "#111827" : "#1f2937",
              color: "#e5e7eb",
              cursor: page === totalPages ? "not-allowed" : "pointer",
            }}
          >
            Next
          </button>
        </div>
      </div>

      <div style={{ flex: 1, display: "flex" }}>
        <div style={{ flex: 1, position: "relative" }}>
          <div style={{ position: "absolute", top: 12, left: 12, zIndex: 10 }}>
            <button
              onClick={() => selectedRequestId && loadGraphForRequest(selectedRequestId)}
              style={{
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid #374151",
                background: "#ffffff",
                color: "#111827",
                cursor: "pointer",
              }}
            >
              Refresh selected graph
            </button>
          </div>

          {loadingGraph ? (
            <div style={{ color: "#e5e7eb", padding: 20 }}>Loading graph...</div>
          ) : error ? (
            <div style={{ color: "#fca5a5", padding: 20 }}>{error}</div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              fitView
              onNodeClick={(_, node) => setSelectedNode(node.data.meta)}
            >
              <MiniMap />
              <Controls />
              <Background />
            </ReactFlow>
          )}
        </div>

        <div
          style={{
            width: 360,
            borderLeft: "1px solid #1f2937",
            background: "#f8fafc",
            color: "#0f172a",
            padding: 16,
            overflowY: "auto",
            fontFamily: "sans-serif",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Request Details</h2>

          <p>
            <strong>Selected request:</strong><br />
            <span style={{ wordBreak: "break-all" }}>
              {selectedRequestId || "None"}
            </span>
          </p>

          {!selectedNode ? (
            <p>Click a node in the flow to inspect it.</p>
          ) : (
            <>
              <h3>{selectedNode.label}</h3>
              <p><strong>Full name:</strong> {selectedNode.full_name}</p>
              <p><strong>Type:</strong> {selectedNode.type}</p>
              <p><strong>Duration:</strong> {formatDuration(selectedNode.duration)}</p>
              <p><strong>File:</strong> {selectedNode.file_path ?? "N/A"}</p>
              <p><strong>Line:</strong> {selectedNode.line_no ?? "N/A"}</p>
              <p><strong>Route:</strong> {selectedNode.route_path ?? "N/A"}</p>
              <p><strong>Methods:</strong> {(selectedNode.route_methods || []).join(", ") || "N/A"}</p>
              <p><strong>Expandable:</strong> {selectedNode.expandable ? "Yes" : "No"}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}