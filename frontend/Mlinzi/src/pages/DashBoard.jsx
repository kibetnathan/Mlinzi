import React, { useState } from 'react';

// mock transaction dataset mapped with specific anomaly triggers
const initialTransactions = [
  {
    transaction_id: "TXN1016",
    customer_id: "CUST014",
    customer_name: "Michael Onyango",
    timestamp: "2026-07-01 08:14",
    amount_kes: 1200,
    transaction_type: "Deposit",
    channel: "ATM",
    anomalyType: "Round Number Anomaly",
    severity: "LOW",
    reason: "Even hundred metric matching static automated test deposits.",
    status: "Suspicious"
  },
  {
    transaction_id: "TXN1008",
    customer_id: "CUST009",
    customer_name: "Mercy Wambui",
    timestamp: "2026-07-01 08:46",
    amount_kes: 12000,
    transaction_type: "Transfer",
    channel: "Mobile",
    anomalyType: "Velocity",
    severity: "CRITICAL",
    reason: "High-value transfer followed instantly by secondary routing attempts.",
    status: "Flagged"
  },
  {
    transaction_id: "TXN1007",
    customer_id: "CUST009",
    customer_name: "Mercy Wambui",
    timestamp: "2026-07-01 09:22",
    amount_kes: 2300,
    transaction_type: "Transfer",
    channel: "Agent",
    anomalyType: "Velocity",
    severity: "HIGH",
    reason: "Secondary transfer execution within the same hour block.",
    status: "Flagged"
  },
  {
    transaction_id: "TXN1011",
    customer_id: "CUST011",
    customer_name: "Ruth Nyambura",
    timestamp: "2026-07-01 09:54",
    amount_kes: 15600,
    transaction_type: "Withdrawal",
    channel: "ATM",
    anomalyType: "Repeated Withdrawals",
    severity: "WARNING",
    reason: "Uncharacteristic ATM cash-out pattern relative to user historical limits.",
    status: "Flagged"
  },
  {
    transaction_id: "TXN1006",
    customer_id: "CUST008",
    customer_name: "John Kariuki",
    timestamp: "2026-07-01 10:13",
    amount_kes: 2300,
    transaction_type: "Withdrawal",
    channel: "Mobile",
    anomalyType: "Repeated Withdrawals",
    severity: "WARNING",
    reason: "Consecutive mobile withdrawal requests within minutes.",
    status: "Suspicious"
  },
  {
    transaction_id: "TXN1005",
    customer_id: "CUST008",
    customer_name: "John Kariuki",
    timestamp: "2026-07-01 10:44",
    amount_kes: 5400,
    transaction_type: "Deposit",
    channel: "Agent",
    anomalyType: "Round Number Anomaly",
    severity: "LOW",
    reason: "Rapid cash turnaround pattern - ATM extraction recycled back as Agent Deposit.",
    status: "Suspicious"
  },
  {
    transaction_id: "TXN1001",
    customer_id: "CUST003",
    customer_name: "Grace Njoki",
    timestamp: "2026-07-01 11:14",
    amount_kes: 750,
    transaction_type: "Transfer",
    channel: "Mobile",
    anomalyType: "Velocity",
    severity: "LOW",
    reason: "Micro-transfer clearing validation.",
    status: "Suspicious"
  }
];

function DashBoard() {
  const [transactions, setTransactions] = useState(initialTransactions);
  const [selectedTx, setSelectedTx] = useState(initialTransactions[1]); // Default to first flagged item
  const [activeFilter, setActiveFilter] = useState("ALL");

  // queues based on current level of investigation
  const flaggedQueue = transactions.filter(tx => tx.status === "Flagged" || tx.status === "Investigating");
  const suspiciousWatchlist = transactions.filter(tx => tx.status === "Suspicious");

  //category filter (Velocity, Repeated Withdrawals, Round Numbers) to the flagged queue
  const filteredQueue = flaggedQueue.filter(tx => {
    if (activeFilter === "ALL") return true;
    return tx.anomalyType === activeFilter;
  });

  // Action: suspicious item to the active Flagged Queue
  const promoteToInvestigation = (txId) => {
    setTransactions(prev => prev.map(tx => {
      if (tx.transaction_id === txId) {
        const updated = { ...tx, status: "Flagged", severity: "HIGH" };
        if (selectedTx?.transaction_id === txId) {
          setSelectedTx(updated);
        }
        return updated;
      }
      return tx;
    }));
  };

  // Action: Resolve/Dismiss a flagged item
  const resolveIncident = (txId) => {
    setTransactions(prev => prev.map(tx => {
      if (tx.transaction_id === txId) {
        const updated = { ...tx, status: "Resolved" };
        if (selectedTx?.transaction_id === txId) {
          setSelectedTx(updated);
        }
        return updated;
      }
      return tx;
    }));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Header bar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse"></span>
            Mlinzi Analyst Triage Core
          </h1>
          <p className="text-xs text-slate-400">CSV Monitoring & Threat Detection</p>
        </div>
        <div className="flex gap-4 text-xs font-mono">
          <div className="bg-slate-900 border border-slate-800 px-3 py-1.5 rounded">
            ACTIVE ALERTS: <span className="text-rose-400 font-bold">{flaggedQueue.filter(t => t.status !== "Resolved").length}</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 px-3 py-1.5 rounded">
            SUSPICIOUS WATCHLIST: <span className="text-amber-400 font-bold">{suspiciousWatchlist.length}</span>
          </div>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="flex-1 grid grid-cols-1 xl:grid-cols-3 overflow-hidden divide-y xl:divide-y-0 xl:divide-x divide-slate-800">
        
        {/* Pane 1: Investigation & Flags Queue */}
        <section className="p-4 overflow-y-auto space-y-4 bg-slate-950">
          <div>
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3"> Flagged Queue ({filteredQueue.length})</h2>
            
            {/* Filter Pills based on rules */}
            <div className="flex flex-wrap gap-1 mb-4">
              {["ALL", "Velocity", "Repeated Withdrawals", "Round Number Anomaly"].map(filterVal => (
                <button
                  key={filterVal}
                  onClick={() => setActiveFilter(filterVal)}
                  className={`text-[10px] font-semibold px-2 py-1 rounded transition ${
                    activeFilter === filterVal
                      ? "bg-rose-600 text-white"
                      : "bg-slate-900 text-slate-400 border border-slate-800 hover:border-slate-700"
                  }`}
                >
                  {filterVal === "ALL" ? "All Flags" : filterVal}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {filteredQueue.map(item => (
              <div
                key={item.transaction_id}
                onClick={() => setSelectedTx(item)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
                  selectedTx?.transaction_id === item.transaction_id 
                    ? 'bg-slate-900 border-rose-500 shadow-md shadow-rose-950/20' 
                    : 'bg-slate-900/40 border-slate-900 hover:border-slate-800'
                }`}
              >
                <div className="flex justify-between items-start text-xs font-mono mb-1.5">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    item.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400' : 'bg-amber-950 text-amber-300'
                  }`}>
                    {item.anomalyType}
                  </span>
                  <span className="text-slate-500">{item.transaction_id}</span>
                </div>
                <h3 className="font-semibold text-sm text-slate-200">{item.customer_name}</h3>
                <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-800/40 text-xs">
                  <span className="text-slate-300 font-bold font-mono">KES {item.amount_kes.toLocaleString()}</span>
                  <span className={`font-semibold ${item.status === 'Resolved' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    ● {item.status}
                  </span>
                </div>
              </div>
            ))}
            {filteredQueue.length === 0 && (
              <p className="text-xs text-slate-500 text-center py-8">No current incidents matching this rule.</p>
            )}
          </div>
        </section>

        {/* Suspicious Activity Watchlist */}
        <section className="p-4 overflow-y-auto space-y-4 bg-slate-900/10">
          <div>
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Suspicious Watchlist ({suspiciousWatchlist.length})</h2>
            <p className="text-[11px] text-slate-500">Unflagged transactions holding moderate risk characteristics</p>
          </div>

          <div className="space-y-2">
            {suspiciousWatchlist.map(item => (
              <div
                key={item.transaction_id}
                onClick={() => setSelectedTx(item)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer group ${
                  selectedTx?.transaction_id === item.transaction_id 
                    ? 'bg-slate-900 border-amber-500' 
                    : 'bg-slate-900/20 border-slate-900 hover:border-slate-800'
                }`}
              >
                <div className="flex justify-between items-center text-xs font-mono mb-1.5">
                  <span className="text-amber-400 font-semibold bg-amber-950/40 px-1.5 py-0.5 rounded text-[10px]">
                    {item.anomalyType}
                  </span>
                  <span className="text-slate-500">{item.transaction_id}</span>
                </div>
                <h3 className="font-medium text-sm text-slate-300">{item.customer_name}</h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-1">{item.reason}</p>
                
                <div className="mt-3 pt-2 border-t border-slate-800/40 flex justify-between items-center">
                  <span className="text-xs font-mono text-slate-300 font-bold">KES {item.amount_kes.toLocaleString()}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation(); 
                      promoteToInvestigation(item.transaction_id);
                    }}
                    className="text-[10px] font-bold bg-amber-500/10 hover:bg-amber-500 text-amber-400 hover:text-slate-950 transition-colors px-2 py-1 rounded border border-amber-500/20 group-hover:border-amber-500"
                  >
                    Flag Incident
                  </button>
                </div>
              </div>
            ))}
            {suspiciousWatchlist.length === 0 && (
              <p className="text-xs text-slate-500 text-center py-8">All suspicious transactions have been triaged.</p>
            )}
          </div>
        </section>

        {/*  Workspace / Detailed Inspector */}
        <section className="p-6 bg-slate-900/30 flex flex-col justify-between">
          {selectedTx ? (
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono text-slate-500">TXID: {selectedTx.transaction_id}</span>
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono uppercase">
                    {selectedTx.status}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white">{selectedTx.customer_name}</h3>
                <p className="text-xs text-slate-400 mt-1">Customer Identifier: <span className="text-cyan-400 font-mono">{selectedTx.customer_id}</span></p>
              </div>

              {/* Data Manifest Object */}
              <div className="bg-slate-950 p-4 rounded border border-slate-800 text-xs font-mono space-y-2.5">
                <p className="text-slate-500 border-b border-slate-900 pb-1.5">// Transaction Attributes</p>
                <div><span className="text-slate-400">Timestamp:</span> <span className="text-slate-200">{selectedTx.timestamp}</span></div>
                <div><span className="text-slate-400">Amount:</span> <span className="text-emerald-400 font-bold">KES {selectedTx.amount_kes.toLocaleString()}</span></div>
                <div><span className="text-slate-400">Transaction Type:</span> <span className="text-slate-200">{selectedTx.transaction_type}</span></div>
                <div><span className="text-slate-400">Routing Channel:</span> <span className="text-cyan-400">{selectedTx.channel}</span></div>
                <div className="pt-1.5 border-t border-slate-900">
                  <span className="text-slate-400 block mb-1">Telemetry Reason:</span>
                  <span className="text-slate-300 text-[11px] block leading-relaxed">{selectedTx.reason}</span>
                </div>
              </div>

              {/* Dynamic Actions based on current status */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Triage Procedures</h4>
                
                {selectedTx.status === "Suspicious" ? (
                  <div className="bg-amber-950/20 border border-amber-800/40 p-3 rounded text-xs text-amber-300 space-y-2">
                    <p>This transaction is currently passively watched. Escalating pushes it directly into the active Flagged Queue.</p>
                    <button
                      onClick={() => promoteToInvestigation(selectedTx.transaction_id)}
                      className="w-full bg-amber-500 text-slate-950 font-bold py-2 rounded text-center text-xs hover:bg-amber-400 transition"
                    >
                      Promote to Active Flagged Queue
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => resolveIncident(selectedTx.transaction_id)}
                      disabled={selectedTx.status === "Resolved"}
                      className="flex-1 text-xs font-bold bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 transition py-2.5 rounded text-white"
                    >
                      {selectedTx.status === "Resolved" ? "✓ Incident Resolved" : "Approve & Resolve Ledger"}
                    </button>
                    <button 
                      disabled={selectedTx.status === "Resolved"}
                      className="text-xs font-bold bg-rose-600/10 border border-rose-500/20 hover:bg-rose-600 text-rose-400 hover:text-white disabled:opacity-40 transition px-4 py-2.5 rounded"
                    >
                      Freeze Account
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-600 font-mono my-auto text-xs">
              [Select a transaction log to load details]
            </div>
          )}
        </section>

      </main>
    </div>
  );
}

export default DashBoard;