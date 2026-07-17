import React, { useState, useEffect } from "react";

const API_BASE = import.meta.env.BASE_URL;

function DashBoard() {
  const [transactions, setTransactions] = useState([]);

  // Track selected customer instead of a single transaction
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);

  const [activeFilter, setActiveFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchVelocityFlags() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/velocity`);
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        const data = await res.json();

        const rawTransactions = Array.isArray(data) ? data : [];

        // Normalize transactions
        const normalizedData = rawTransactions.map((tx) => ({
          ...tx,
          anomalyType: tx.anomalyType || "Velocity",
          severity:
            tx.severity || (tx.velocity_count >= 10 ? "CRITICAL" : "HIGH"),
          status: tx.status || "Flagged",
        }));

        if (!cancelled) {
          setTransactions(normalizedData);

          // Auto-select the first customer's ID if available
          if (normalizedData.length > 0) {
            setSelectedCustomerId(normalizedData[0].customer_id);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchVelocityFlags();
    return () => {
      cancelled = true;
    };
  }, []);

  // ==========================================
  // HELPER: GROUP TRANSACTIONS BY CUSTOMER
  // ==========================================
  const groupTransactionsByCustomer = (txList) => {
    const groups = {};
    txList.forEach((tx) => {
      const cid = tx.customer_id;
      if (!groups[cid]) {
        groups[cid] = {
          customer_id: cid,
          customer_name: tx.customer_name,
          transactions: [],
          total_amount: 0,
          highest_severity: "LOW",
          status: "Suspicious",
        };
      }
      groups[cid].transactions.push(tx);
      groups[cid].total_amount += tx.amount_kes || 0;

      if (tx.status === "Flagged" || tx.status === "Investigating") {
        groups[cid].status = "Flagged";
      }

      const severityWeights = { LOW: 1, WARNING: 2, HIGH: 3, CRITICAL: 4 };
      const currentWeight = severityWeights[tx.severity] || 1;
      const existingWeight = severityWeights[groups[cid].highest_severity] || 1;
      if (currentWeight > existingWeight) {
        groups[cid].highest_severity = tx.severity;
      }
    });
    return Object.values(groups);
  };

  const allCustomers = groupTransactionsByCustomer(transactions);

  const flaggedQueue = allCustomers.filter((c) => c.status === "Flagged");
  const suspiciousWatchlist = allCustomers.filter(
    (c) => c.status === "Suspicious",
  );

  const filteredQueue = flaggedQueue.filter((customer) => {
    if (activeFilter === "ALL") return true;
    return customer.transactions.some((tx) => tx.anomalyType === activeFilter);
  });

  const selectedCustomer =
    allCustomers.find((c) => c.customer_id === selectedCustomerId) || null;

  const promoteToInvestigation = (customerId) => {
    setTransactions((prev) =>
      prev.map((tx) => {
        if (tx.customer_id === customerId) {
          return { ...tx, status: "Flagged", severity: "HIGH" };
        }
        return tx;
      }),
    );
  };

  const resolveIncident = (customerId) => {
    setTransactions((prev) =>
      prev.map((tx) => {
        if (tx.customer_id === customerId) {
          return { ...tx, status: "Resolved" };
        }
        return tx;
      }),
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#121212] text-slate-400 flex items-center justify-center font-mono text-xs">
        Loading transaction feed...
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#121212] text-[#E74C3C] flex items-center justify-center font-mono text-xs">
        Error: Failed to reach detection API: {error}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#121212] text-slate-300 flex flex-col font-sans text-xs">
      {/* Header Bar */}
      <header className="border-b border-slate-800 bg-[#181818] px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-base font-bold tracking-tight text-slate-100 uppercase">
            Mlinzi Analyst Triage Core
          </h1>
          <p className="text-[11px] text-slate-400">
            Customer Risk Profiles & Threat Detection
          </p>
        </div>
        <div className="flex gap-4 font-mono">
          <div className="bg-[#1e1e1e] border border-slate-800 px-3 py-1.5 rounded flex items-center gap-2 text-slate-200">
            <span className="text-[#E74C3C] font-bold">ACTIVE ALERTS:</span>
            <span className="text-[#E74C3C] font-bold">
              {flaggedQueue.length}
            </span>
          </div>
          <div className="bg-[#1e1e1e] border border-slate-800 px-3 py-1.5 rounded flex items-center gap-2 text-slate-200">
            <span className="text-amber-500 font-bold">SUSPICIOUS:</span>
            <span className="text-amber-500 font-bold">
              {suspiciousWatchlist.length}
            </span>
          </div>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="flex-1 grid grid-cols-1 xl:grid-cols-3 overflow-hidden divide-y xl:divide-y-0 xl:divide-x divide-slate-800">
        {/* Pane 1: Investigation & Customer Flags Queue */}
        <section className="p-4 overflow-y-auto space-y-4 bg-[#121212]">
          <div>
            <h2 className="font-bold text-slate-400 uppercase tracking-wider mb-3">
              Flagged Customers ({filteredQueue.length})
            </h2>

            {/* Filter Pills */}
            <div className="flex flex-wrap gap-1 mb-4">
              {[
                "ALL",
                "Velocity",
                "Repeated Withdrawals",
                "Round Number Anomaly",
              ].map((filterVal) => (
                <button
                  key={filterVal}
                  onClick={() => setActiveFilter(filterVal)}
                  className={`text-[10px] font-semibold px-2.5 py-1 rounded transition uppercase ${
                    activeFilter === filterVal
                      ? "bg-[#E74C3C] text-white"
                      : "bg-[#1e1e1e] text-slate-400 border border-slate-800 hover:border-slate-700"
                  }`}
                >
                  {filterVal === "ALL" ? "All Flags" : filterVal}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {filteredQueue.map((item) => (
              <div
                key={item.customer_id}
                onClick={() => setSelectedCustomerId(item.customer_id)}
                className={`p-3.5 rounded border transition-all cursor-pointer ${
                  selectedCustomerId === item.customer_id
                    ? "bg-[#181818] border-[#E74C3C] shadow-md shadow-rose-950/10"
                    : "bg-[#181818]/40 border-slate-800/80 hover:border-slate-700"
                }`}
              >
                <div className="flex justify-between items-start font-mono mb-1.5">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                      item.highest_severity === "CRITICAL"
                        ? "bg-red-950/40 text-[#E74C3C]"
                        : "bg-amber-950/40 text-amber-500"
                    }`}
                  >
                    {item.highest_severity} RISK
                  </span>
                  <span className="text-slate-500 text-[10px]">
                    {item.transactions.length} Transactions
                  </span>
                </div>
                <h3 className="font-semibold text-slate-200">
                  {item.customer_name}
                </h3>
                <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-800/40">
                  <span className="text-slate-300 font-bold font-mono">
                    KES {item.total_amount.toLocaleString()}
                  </span>
                  <span className="font-semibold text-[#E74C3C] font-mono text-[10px] uppercase">
                    STATUS: {item.status}
                  </span>
                </div>
              </div>
            ))}
            {filteredQueue.length === 0 && (
              <p className="text-slate-500 text-center py-8">
                No customers matching this risk profile.
              </p>
            )}
          </div>
        </section>

        {/* Pane 2: Suspicious Activity Watchlist */}
        <section className="p-4 overflow-y-auto space-y-4 bg-[#121212]/40">
          <div>
            <h2 className="font-bold text-slate-400 uppercase tracking-wider mb-1">
              Suspicious Watchlist ({suspiciousWatchlist.length})
            </h2>
            <p className="text-[11px] text-slate-500">
              Profiles holding moderate, unflagged anomalies
            </p>
          </div>

          <div className="space-y-2">
            {suspiciousWatchlist.map((item) => (
              <div
                key={item.customer_id}
                onClick={() => setSelectedCustomerId(item.customer_id)}
                className={`p-3.5 rounded border transition-all cursor-pointer group ${
                  selectedCustomerId === item.customer_id
                    ? "bg-[#181818] border-amber-500"
                    : "bg-[#181818]/20 border-slate-800/80 hover:border-slate-700"
                }`}
              >
                <div className="flex justify-between items-center font-mono mb-1.5">
                  <span className="text-amber-400 font-semibold bg-amber-950/20 px-1.5 py-0.5 rounded text-[10px] uppercase">
                    PENDING: {item.transactions.length} Actions
                  </span>
                  <span className="text-slate-500 text-[10px]">
                    ID: {item.customer_id}
                  </span>
                </div>
                <h3 className="font-medium text-slate-300">
                  {item.customer_name}
                </h3>

                <div className="mt-3 pt-2 border-t border-slate-800/40 flex justify-between items-center">
                  <span className="font-mono text-slate-300 font-bold">
                    KES {item.total_amount.toLocaleString()}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      promoteToInvestigation(item.customer_id);
                    }}
                    className="text-[10px] font-bold bg-amber-500/10 hover:bg-amber-500 text-amber-400 hover:text-slate-950 transition-colors px-2 py-1 rounded border border-amber-500/20 uppercase"
                  >
                    Flag Profile
                  </button>
                </div>
              </div>
            ))}
            {suspiciousWatchlist.length === 0 && (
              <p className="text-slate-500 text-center py-8">
                All suspicious customer profiles have been triaged.
              </p>
            )}
          </div>
        </section>

        {/* Pane 3: Workspace / Detailed Customer Inspector */}
        <section className="p-6 bg-[#181818]/30 flex flex-col justify-between overflow-y-auto">
          {selectedCustomer ? (
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-slate-500">
                    ID: {selectedCustomer.customer_id}
                  </span>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono uppercase font-bold ${
                      selectedCustomer.status === "Flagged"
                        ? "bg-red-950/40 text-[#E74C3C]"
                        : "bg-amber-950/40 text-amber-500"
                    }`}
                  >
                    {selectedCustomer.status}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-100">
                  {selectedCustomer.customer_name}
                </h3>
                <p className="text-slate-400 mt-1">
                  Aggregated Profile Value:{" "}
                  <span className="text-cyan-400 font-mono font-bold">
                    KES {selectedCustomer.total_amount.toLocaleString()}
                  </span>
                </p>
              </div>

              {/* Dynamic Transaction Logs Container */}
              <div className="space-y-3">
                <h4 className="font-semibold text-slate-400 uppercase tracking-wider">
                  // TRANSACTION MANIFEST (
                  {selectedCustomer.transactions.length})
                </h4>

                <div className="space-y-3 max-h-[350px] overflow-y-auto pr-1">
                  {selectedCustomer.transactions.map((tx) => {
                    const isResolved = tx.status === "Resolved";
                    const isFlagged = tx.status === "Flagged";
                    return (
                      <div
                        key={tx.transaction_id}
                        className="bg-[#121212] p-4 rounded border border-slate-800 font-mono space-y-2"
                      >
                        <div className="flex justify-between items-center border-b border-slate-800/60 pb-1.5">
                          <span className="text-cyan-400 text-[10px]">
                            TXID: {tx.transaction_id}
                          </span>
                          <span className="text-slate-500 text-[10px]">
                            {tx.timestamp}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <div>
                            <span className="text-slate-500">Amount:</span>{" "}
                            <span className="text-[#2ECC71] font-bold">
                              KES {tx.amount_kes.toLocaleString()}
                            </span>
                          </div>
                          <span
                            className={`text-[10px] font-bold uppercase ${isResolved ? "text-[#2ECC71]" : isFlagged ? "text-[#E74C3C]" : "text-amber-500"}`}
                          >
                            {tx.status}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500">Type:</span>{" "}
                          <span className="text-slate-300">
                            {tx.transaction_type} ({tx.channel})
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500">
                            Telemetry Reason:
                          </span>
                          <span className="text-slate-300 block text-[11px] mt-1 leading-relaxed bg-[#181818] p-1.5 rounded border border-slate-800/60">
                            {tx.reason}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Dynamic Profile Actions */}
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <h4 className="font-semibold text-slate-400 uppercase tracking-wider">
                  Bulk Triage Actions
                </h4>

                {selectedCustomer.status === "Suspicious" ? (
                  <div className="bg-amber-950/20 border border-amber-800/40 p-3 rounded text-amber-300 space-y-2">
                    <p>
                      This profile is unflagged. Escalating will move all nested
                      transactions into the Active Flagged Queue.
                    </p>
                    <button
                      onClick={() =>
                        promoteToInvestigation(selectedCustomer.customer_id)
                      }
                      className="w-full bg-amber-500 text-slate-950 font-bold py-2 rounded text-center hover:bg-amber-400 transition uppercase"
                    >
                      Promote Customer Profile
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() =>
                        resolveIncident(selectedCustomer.customer_id)
                      }
                      disabled={selectedCustomer.transactions.every(
                        (tx) => tx.status === "Resolved",
                      )}
                      className="flex-1 font-bold bg-[#2ECC71] hover:bg-green-400 disabled:bg-slate-800 disabled:text-slate-500 transition py-2.5 rounded text-slate-950 uppercase"
                    >
                      {selectedCustomer.transactions.every(
                        (tx) => tx.status === "Resolved",
                      )
                        ? "Profile Resolved"
                        : "Resolve All Incidents"}
                    </button>
                    <button
                      disabled={selectedCustomer.transactions.every(
                        (tx) => tx.status === "Resolved",
                      )}
                      className="font-bold bg-[#E74C3C]/10 border border-[#E74C3C]/20 hover:bg-[#E74C3C] text-[#E74C3C] hover:text-white disabled:opacity-40 transition px-4 py-2.5 rounded uppercase"
                    >
                      Freeze Account
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-600 font-mono my-auto">
              [Select a customer profile to load transaction logs]
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default DashBoard;

