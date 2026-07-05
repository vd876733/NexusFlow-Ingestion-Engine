import { useMemo, useState } from 'react'
import {
  Activity,
  ArrowRight,
  BarChart3,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const initialMetrics = [
  { date: '2026-07-05', hour: '12:00', event_type: 'view', total_events: 196, unique_users: 195 },
  { date: '2026-07-05', hour: '12:00', event_type: 'add_to_cart', total_events: 172, unique_users: 172 },
  { date: '2026-07-05', hour: '12:00', event_type: 'click', total_events: 171, unique_users: 171 },
  { date: '2026-07-05', hour: '12:00', event_type: 'purchase', total_events: 171, unique_users: 171 },
]

const badgeStyles = {
  view: 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20',
  click: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
  add_to_cart: 'bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20',
  purchase: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
}

function App() {
  const [metrics] = useState(initialMetrics)

  const chartData = useMemo(
    () =>
      metrics.map((row) => ({
        name: row.event_type.replace('_', ' '),
        events: row.total_events,
        users: row.unique_users,
      })),
    [metrics],
  )

  const totalEventThroughput = metrics.reduce((sum, row) => sum + row.total_events, 0)
  const peakUniqueActiveAudience = Math.max(...metrics.map((row) => row.unique_users))

  const glassCard =
    'bg-slate-900/40 backdrop-blur-xl border border-white/[0.06] rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.3)] transition-all duration-300 hover:border-white/[0.12]'

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 p-4 text-slate-100 antialiased sm:p-6 lg:p-8">
      <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-cyan-500/10 blur-[150px] pointer-events-none" />
      <div className="absolute top-60 right-10 h-[500px] w-[500px] rounded-full bg-indigo-500/10 blur-[180px] pointer-events-none" />

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6">
        <header className={`${glassCard} p-6 sm:p-8`}>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.3em] text-slate-400">
                <Activity className="h-4 w-4 text-emerald-400" />
                <span className="inline-flex items-center gap-2">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_12px_#34d399]" />
                  CORE INGESTION STATE: OPERATIONAL
                </span>
              </div>
              <h1 className="mt-4 text-xl font-extrabold uppercase tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400 sm:text-2xl">
                NEXUSFLOW // STREAMING ENGINE
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
                A hyper-clean control surface for observing the live Gold Medallion pipeline,
                event throughput, and active user reach.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm text-slate-300 shadow-lg backdrop-blur">
              <div className="flex items-center gap-2 font-medium text-slate-200">
                <BarChart3 className="h-4 w-4 text-cyan-400" />
                LIVE PERF. SNAPSHOT
              </div>
              <div className="mt-2 font-mono text-[11px] uppercase tracking-[0.25em] text-slate-500">
                {metrics[0].date} • {metrics[0].hour}
              </div>
            </div>
          </div>

          <div className="mt-8 grid gap-4 lg:grid-cols-2">
            <div className={`${glassCard} p-5 hover:-translate-y-1`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-400">Total Event Throughput</p>
                  <p className="mt-3 font-mono text-3xl font-semibold text-white">{loading ? '—' : totalEventThroughput}</p>
                </div>
                <div className="rounded-2xl bg-cyan-500/10 p-3 text-cyan-400">
                  <Zap className="h-5 w-5" />
                </div>
              </div>
            </div>

            <div className={`${glassCard} p-5 hover:-translate-y-1`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-400">Peak Unique Active Audience</p>
                  <p className="mt-3 font-mono text-3xl font-semibold text-white">{loading ? '—' : peakUniqueActiveAudience}</p>
                </div>
                <div className="rounded-2xl bg-indigo-500/10 p-3 text-indigo-400">
                  <Users className="h-5 w-5" />
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <section className={`${glassCard} p-6`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500">
                  Conversion Landscape
                </p>
                <h2 className="mt-2 text-xl font-semibold text-white">Funnel Performance</h2>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-400">
                <TrendingUp className="h-4 w-4" />
                +12.4% uplift
              </div>
            </div>

            <div className="mt-6 h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="eventsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.45} />
                      <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip
                    cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
                    contentStyle={{
                      background: 'rgba(2,6,23,0.8)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '0.75rem',
                      backdropFilter: 'blur(12px)',
                      color: '#f8fafc',
                    }}
                  />
                  <Area type="monotone" dataKey="events" stroke="#22d3ee" strokeWidth={2.5} fill="url(#eventsGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className={`${glassCard} p-6`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500">
                  Activity Feed
                </p>
                <h2 className="mt-2 text-xl font-semibold text-white">Live Event Mix</h2>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              {metrics.map((row, index) => (
                <div
                  key={`${row.name}-${index}`}
                  className="flex items-center justify-between rounded-2xl border border-white/5 bg-slate-950/40 px-4 py-3 transition-transform hover:scale-[1.01]"
                >
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-slate-800/80 p-2 text-cyan-400">
                      <BarChart3 className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-100">{row.name}</p>
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{loading ? 'syncing' : 'live'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-2.5 py-1 text-xs font-semibold text-cyan-400">
                      {row.users || 0} users
                    </span>
                    <ArrowRight className="h-4 w-4 text-slate-500" />
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className={`${glassCard} overflow-hidden`}>
          <div className="border-b border-slate-800/50 bg-slate-950/40 px-6 py-4">
            <h2 className="text-lg font-semibold text-white">Granular Metrics</h2>
            <p className="mt-1 text-sm text-slate-500">Detailed benchmark rows from the Gold layer</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800/50">
              <thead className="bg-slate-950/40">
                <tr>
                  <th className="px-6 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                    Hour
                  </th>
                  <th className="px-6 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                    Event Type
                  </th>
                  <th className="px-6 py-3 text-right text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                    Total Events
                  </th>
                  <th className="px-6 py-3 text-right text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-500">
                    Unique Users
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 bg-slate-900/20">
                {transactions.map((row) => (
                  <tr key={row.id} className="transition-transform hover:scale-[1.01]">
                    <td className="whitespace-nowrap px-6 py-4 font-mono text-sm text-slate-300">{row.timestamp}</td>
                    <td className="whitespace-nowrap px-6 py-4 font-mono text-sm text-slate-300">{row.userId}</td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                      <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${badgeStyles[row.eventType] || 'bg-slate-500/10 text-slate-300 border-slate-500/20'}`}>
                        {row.eventLabel}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right font-mono text-sm font-semibold text-slate-200">
                      {row.status}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right font-mono text-sm font-semibold text-slate-200">
                      {summary.dlq_error_count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  )
}

export default App
