<div align="center">

# 🧠 Navam Invest

**AI-Powered Investment Intelligence for Retail Investors**

[![PyPI version](https://badge.fury.io/py/navam-invest.svg)](https://badge.fury.io/py/navam-invest)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/navam-invest)](https://pepy.tech/project/navam-invest)

Institutional-grade portfolio intelligence powered by specialized AI agents
Built on [LangGraph](https://langchain-ai.github.io/langgraph/) • Powered by [Anthropic Claude](https://www.anthropic.com/claude)

[Quick Start](#-quick-start) •
[Features](#-key-features) •
[AI Agents](#-specialized-ai-agents) •
[Documentation](#-documentation) •
[Examples](#-example-workflows)

</div>

---

## 🎯 What is Navam Invest?

**Replace $1,000-$10,000/year wealth management fees with AI agents that research, analyze, and explain investment decisions in plain English.**

Navam Invest is an **open-source AI investment advisory platform** designed for retail investors managing $50K-$1M portfolios. Instead of paying 1% AUM fees, you get a **team of 9 specialized AI agents** that collaborate through multi-agent workflows—all running locally with your API keys, using free public data.

### Why Choose Navam Invest?

<table>
<tr>
<td width="50%">

**🏦 Institutional Intelligence, Retail Access**
- 9 specialized AI agents (equity research, earnings analysis, risk management, tax optimization)
- Multi-agent workflows that combine bottom-up + top-down analysis
- Same frameworks used by professional analysts

</td>
<td width="50%">

**💰 Zero Lock-In, Maximum Value**
- Core features work with 100% free APIs (Yahoo Finance + SEC EDGAR)
- No subscriptions, no recurring fees
- Your data stays yours—runs completely locally

</td>
</tr>
<tr>
<td width="50%">

**🔍 Transparent & Explainable**
- Watch AI agents reason in real-time
- Full audit trails of tool calls and data sources
- Educational explanations, not black-box recommendations

</td>
<td width="50%">

**⚡ Production-Ready Today**
- Interactive terminal UI (TUI) with real-time streaming
- 32 tools across 9 APIs (3 require zero setup)
- Auto-save reports, multi-agent orchestration

</td>
</tr>
</table>

---

## ✨ Key Features

### 🤖 9 Specialized AI Agents

Each agent is purpose-built with curated tools and expert system prompts:

| Agent | Purpose | Tools | Use Case |
|-------|---------|-------|----------|
| **[Quill](#-quill---equity-research-analyst)** | Deep fundamental research | 36 | "Analyze AAPL with DCF valuation and insider activity" |
| **[Earnings Whisperer](#-earnings-whisperer---earnings-specialist)** | Earnings surprise analysis | 14 | "Find post-earnings drift opportunities in NVDA" |
| **[Screen Forge](#-screen-forge---equity-screener)** | Systematic stock screening | 15 | "Screen for stocks with 3+ consecutive earnings beats" |
| **[Macro Lens](#-macro-lens---market-strategist)** | Top-down macro analysis | 13 | "What's the current economic regime for tech stocks?" |
| **[News Sentry](#-news-sentry---real-time-event-monitor)** | Real-time event detection | 13 | "Alert me to material 8-K filings and insider trades" |
| **[Risk Shield](#-risk-shield---portfolio-risk-manager)** | Portfolio risk management | 18 | "Calculate VAR and analyze concentration risks" |
| **[Tax Scout](#-tax-scout---tax-optimization-specialist)** | Tax-loss harvesting | 12 | "Identify tax-loss harvesting opportunities" |
| **Atlas** | Strategic asset allocation | 12 | "Create an IPS for $200K portfolio" |
| **Portfolio/Research** | Legacy general-purpose | 24/10 | Backward compatibility (will be phased out) |

### 🔀 Multi-Agent Workflows

**Agents don't just answer questions—they collaborate:**

```bash
/analyze MSFT

# 1. Quill performs bottom-up fundamental analysis
#    → Financial health, valuation, earnings trends
# 2. Macro Lens validates with top-down regime analysis
#    → Economic cycles, sector positioning, yield curve
# 3. Final synthesis combines both perspectives
#    → BUY/HOLD/SELL with confidence level and reasoning
```

**Result**: Institutional-quality investment analysis in seconds, not hours.

### 📊 Free & Premium Data Sources

**32 tools across 9 APIs** (3 completely free, 6 with generous free tiers):

| Data Source | Coverage | Free Tier | Cost |
|-------------|----------|-----------|------|
| **Yahoo Finance** 🆓 | Real-time quotes, earnings, analyst ratings, ownership | Unlimited | **FREE** |
| **SEC EDGAR** 🆓 | Corporate filings (10-K, 10-Q, 8-K), insider transactions | Unlimited | **FREE** |
| **U.S. Treasury** 🆓 | Yield curves, treasury rates | Unlimited | **FREE** |
| **Tiingo** | 5-year historical fundamentals | 50 symbols/hr | Optional |
| **Finnhub** | News/social sentiment, insider trades | 60 calls/min | Optional |
| **Alpha Vantage** | Stock prices, company overviews | 25-500 calls/day | Optional |
| **FRED** | Economic indicators (GDP, CPI, unemployment) | Unlimited | Optional |
| **NewsAPI.org** | Market news, headlines | 1,000 calls/day | Optional |
| **Anthropic Claude** | AI reasoning engine (Sonnet 4.5) | Pay-as-you-go | **Required** |

**💡 80% of functionality works with just Yahoo Finance + SEC EDGAR (no API keys needed!)**

### 💬 Modern Terminal UI

**Built with Textual framework** for a responsive, beautiful CLI experience:

- ✅ **Real-time streaming**: Watch agents think and reason live
- ✅ **Smart input management**: Auto-disabled during processing (no accidental duplicate queries)
- ✅ **Tool execution tracking**: See exactly which data sources agents are calling
- ✅ **Multi-agent progress**: Visual workflow transitions with status updates
- ✅ **Markdown rendering**: Tables, code blocks, syntax highlighting
- ✅ **Auto-save reports**: All responses >200 chars saved to `reports/` directory
- ✅ **Keyboard shortcuts**: `Ctrl+C` (clear), `Ctrl+Q` (quit)

---

## 🚀 Quick Start

### Installation

**Requirements**: Python 3.9+ and an Anthropic API key

```bash
# Install from PyPI
pip install navam-invest

# Start the interactive terminal
navam invest
```

### 5-Minute Setup

**1. Create environment file:**

```bash
cp .env.example .env
```

**2. Add your Anthropic API key** (required):

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your free key at [console.anthropic.com](https://console.anthropic.com/)
💰 **Cost**: ~$3-15/month for typical usage (pay-as-you-go)

**3. Optional: Add free-tier API keys** (recommended for full features):

```bash
# Optional - all have generous free tiers
FRED_API_KEY=your_key_here          # Unlimited economic data
TIINGO_API_KEY=your_key_here        # 50 symbols/hr historical data
FINNHUB_API_KEY=your_key_here       # 60 calls/min sentiment data
NEWSAPI_API_KEY=your_key_here       # 1,000 calls/day news
ALPHA_VANTAGE_API_KEY=your_key_here # 25-500 calls/day quotes
```

[Get free API keys →](docs/user-guide/getting-started.md#get-free-api-keys)

**4. Verify setup:**

```bash
navam invest
> /api
# Shows status table: ✅ working / ❌ failed / ⚪ not configured
```

### First Query

```bash
navam invest

# Try multi-agent investment analysis
> /analyze AAPL

# Or ask specific agents
> /quill
> Analyze Microsoft's earnings trends and institutional ownership

> /macro
> What's the current economic regime for tech stocks?

> /risk
> Calculate VAR for my portfolio and identify concentration risks

> /tax
> Identify tax-loss harvesting opportunities before year-end
```

**🎓 New to Navam Invest?** Check the [Getting Started Guide](docs/user-guide/getting-started.md) for detailed walkthroughs.

---

## 🤖 Specialized AI Agents

### ⭐ Quill - Equity Research Analyst

**Deep fundamental analysis & investment thesis development**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Quill Does**:
- 📊 **DCF Valuation**: Discounted cash flow models with sensitivity analysis
- 📈 **5-Year Trends**: Revenue growth, margins, ROIC, FCF, debt ratios
- 💰 **Earnings Analysis**: Historical beats, estimates, surprise patterns
- 🎯 **Analyst Coverage**: Consensus ratings, price targets, upgrades/downgrades
- 🏢 **Ownership Tracking**: Institutional holders, insider transactions (Form 4)
- 📋 **SEC Filings**: 10-K/10-Q deep-dives, 8-K material events, XBRL data
- 💵 **Dividend Analysis**: Yield, payout sustainability, history
- 📰 **News Validation**: Company-specific news with sentiment

**Tools**: 36 specialized tools across Yahoo Finance, SEC EDGAR, Tiingo, Finnhub, NewsAPI

**Example Query**:
```
/quill
Analyze NVDA with focus on:
- Recent earnings momentum vs estimates
- Institutional ownership changes (13F filings)
- Material events from 8-K filings
- DCF valuation vs current price
```

**Expected Output**: 5-section investment thesis with BUY/HOLD/SELL recommendation, fair value range, key catalysts, and risk factors.

</details>

### 📊 Earnings Whisperer - Earnings Specialist

**Earnings surprise analysis & post-earnings drift detection**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Earnings Whisperer Does**:
- 🎯 **Historical Tracking**: 4-8 quarter earnings surprise analysis
- 📈 **Drift Detection**: 1-3 day post-earnings momentum patterns
- 🔄 **Analyst Revisions**: Estimate changes post-earnings
- ✅ **Quality Assessment**: Revenue vs EPS beats, non-recurring items
- 📅 **Calendar Monitoring**: Upcoming earnings with probability scoring
- 🏆 **Pattern Recognition**: Consistent beaters, accelerating growth, quality issues
- 💹 **Trading Signals**: BUY/HOLD/SELL based on drift probability

**Tools**: 14 specialized tools across Yahoo Finance, SEC, Finnhub

**Example Query**:
```
/earnings
Analyze META's last 6 quarters of earnings:
- Average beat percentage (EPS and revenue)
- Post-earnings drift patterns (1-day, 3-day returns)
- Analyst estimate revision trends
- Is there a drift opportunity for next earnings?
```

**Expected Output**: Earnings momentum scorecard with drift probability, pattern analysis, and trading recommendation.

</details>

### 🔍 Screen Forge - Equity Screener

**Systematic stock discovery & idea generation**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Screen Forge Does**:
- 📐 **Multi-Factor Screening**: Value, growth, quality, momentum factors
- 🎯 **Systematic Discovery**: Weekly watchlist generation with ranking
- 📈 **Earnings Momentum**: Filter for consistent earnings beaters
- ⬆️ **Analyst Activity**: Upgrade/downgrade-based screening
- 💬 **Sentiment Validation**: News and social sentiment checks
- 🔗 **Seamless Handoff**: Passes top candidates to Quill for deep-dive

**Tools**: 15 specialized tools across Yahoo Finance, Finnhub, Alpha Vantage

**Example Query**:
```
/screen
Screen for stocks meeting these criteria:
- Market cap > $10B
- 3+ consecutive quarterly earnings beats
- Average surprise > 5%
- Analyst upgrades in last 30 days
- Positive news sentiment
```

**Expected Output**: Ranked table of 10-20 candidates with screening criteria, key metrics, and suggested next steps.

</details>

### 🌍 Macro Lens - Market Strategist

**Top-down economic analysis & regime identification**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Macro Lens Does**:
- 🔄 **Economic Cycles**: 4-phase regime analysis (early/mid/late expansion, recession)
- 📈 **Yield Curve**: Interpretation and recession signal detection (inversions)
- 🏭 **Sector Allocation**: Macro-driven positioning guidance
- 📊 **Factor Recommendations**: Value vs growth, size, volatility tilts
- 📉 **Macro Tracking**: Inflation, GDP, employment, Fed policy
- 📊 **Market Indices**: S&P 500, Nasdaq, VIX correlation analysis
- 💹 **Interest Rates**: Fed funds, treasury rates, credit spreads

**Tools**: 13 specialized tools across FRED, U.S. Treasury, Yahoo Finance, NewsAPI

**Example Query**:
```
/macro
Given current macro conditions:
- What's the economic regime? (early/mid/late expansion, recession)
- Is the yield curve signaling recession?
- Which sectors should I overweight/underweight?
- Value vs growth positioning?
```

**Expected Output**: Regime assessment with sector allocation matrix, factor positioning, and macro risk scenarios.

</details>

### 🗞️ News Sentry - Real-Time Event Monitor

**Material event detection & breaking news alerts**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What News Sentry Does**:
- 📋 **8-K Monitoring**: Material corporate events (M&A, management changes, bankruptcy)
- 📝 **Form 4 Tracking**: Insider buying/selling by officers and directors
- 📰 **Breaking News**: Real-time company-specific news with sentiment
- 📊 **Analyst Actions**: Rating changes, price target updates
- 🎯 **Event Prioritization**: CRITICAL/HIGH/MEDIUM/LOW urgency scoring
- ⚡ **Rapid Response**: Detect market-moving events as they happen

**Tools**: 13 specialized tools across SEC EDGAR, NewsAPI, Finnhub, Yahoo Finance

**Example Query**:
```
/news
Monitor TSLA for:
- Any 8-K filings in last 7 days
- Insider transactions (Form 4) by executives
- Breaking news with negative sentiment
- Analyst downgrades
- Prioritize by market impact
```

**Expected Output**: Prioritized event list with urgency levels, event details, and recommended actions.

</details>

### 🛡️ Risk Shield - Portfolio Risk Manager

**Comprehensive risk analysis & exposure monitoring**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Risk Shield Does**:
- 📊 **Concentration Analysis**: Sector, geographic, single-stock exposures
- 📉 **Drawdown Metrics**: Historical drawdowns, peak-to-trough, recovery periods
- 💹 **VAR Calculations**: Value at Risk (95%, 99% confidence levels)
- 🎲 **Scenario Testing**: Stress tests against historical crises (2008, 2020)
- 🔗 **Correlation Analysis**: Diversification quality, correlation matrices
- 📈 **Volatility Metrics**: Portfolio vol, beta, Sharpe, Sortino ratios
- ⚠️ **Limit Breach Detection**: Position size, sector concentration thresholds
- 🛠️ **Risk Mitigation**: Hedging strategies, rebalancing recommendations

**Tools**: 18 specialized tools across market data, fundamentals, macro indicators, treasury data

**Example Query**:
```
/risk
Analyze my portfolio risk:
- Calculate VAR at 95% and 99% confidence
- Identify sector concentration risks (>30% any sector)
- Stress test against 2008 financial crisis scenario
- Recommend risk mitigation strategies
```

**Expected Output**: Risk scorecard (1-10 scale), concentration analysis, VAR metrics, stress test results, and actionable mitigation recommendations.

</details>

### 💰 Tax Scout - Tax Optimization Specialist

**Tax-loss harvesting & wash-sale compliance**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Tax Scout Does**:
- 💸 **Tax-Loss Harvesting**: Identify positions with unrealized losses
- ⏰ **Wash-Sale Compliance**: 30-day rule monitoring (IRS Section 1091)
- 🔄 **Replacement Candidates**: Find substantially different securities
- 📊 **Capital Gains Analysis**: Short-term vs long-term tracking
- 📅 **Year-End Planning**: Strategic positioning before Dec 31 deadline
- ⚖️ **Tax-Efficient Rebalancing**: Minimize gains during portfolio adjustments
- 📋 **Lot-Level Analysis**: FIFO, LIFO, specific lot identification

**Tools**: 12 specialized tools for portfolio data, market pricing, fundamentals

**Example Query**:
```
/tax
Analyze my portfolio for tax optimization:
- Identify positions with unrealized losses >5%
- Check for wash-sale violations in last 30 days
- Suggest replacement securities for harvested positions
- Calculate potential tax savings ($X at my tax bracket)
- Year-end planning recommendations
```

**Expected Output**: TLH opportunities table with tax savings estimates, wash-sale violations, replacement candidates, and year-end action plan.

</details>

### 🗺️ Atlas - Investment Strategist

**Strategic asset allocation & portfolio construction**

<details>
<summary><b>View Capabilities & Examples</b></summary>

**What Atlas Does**:
- 📋 **IPS Development**: Investment Policy Statement creation
- 🎯 **Asset Allocation**: Strategic allocation frameworks (stocks/bonds/alternatives)
- 📊 **Risk Profiling**: Conservative/Moderate/Aggressive tolerance assessment
- 🔄 **Tactical Tilts**: Macro-driven portfolio adjustments
- ⚖️ **Rebalancing Strategies**: Threshold-based, calendar-based, tax-aware
- 🏗️ **Portfolio Construction**: Building with constraint optimization

**Tools**: 12 specialized tools across all data sources

**Example Query**:
```
/atlas
Create an Investment Policy Statement for:
- Portfolio value: $200,000
- Time horizon: 20 years (retirement)
- Risk tolerance: Moderate
- Income needs: None currently
- Tax considerations: Taxable account
```

**Expected Output**: Complete IPS document with asset allocation targets, rebalancing rules, and risk constraints.

</details>

---

## 💡 Example Workflows

### Multi-Agent Investment Analysis

**Command**: `/analyze <SYMBOL>`

**What Happens**:

1. **Quill** performs bottom-up fundamental analysis
2. **Macro Lens** validates with top-down economic context
3. **Synthesis** combines both perspectives into final recommendation

<details>
<summary><b>Example: /analyze MSFT (click to expand)</b></summary>

```
You: /analyze MSFT

Investment Analysis Workflow: Starting multi-agent analysis...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: FUNDAMENTAL ANALYSIS (Quill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quill (Equity Research):
  → Calling get_quote(symbol=MSFT)
  ✓ MSFT: $420.45, +0.8%, P/E 31x, Market Cap $3.1T

  → Calling get_earnings_history(symbol=MSFT)
  ✓ 4 consecutive earnings beats, avg +4.2% surprise

  → Calling get_analyst_recommendations(symbol=MSFT)
  ✓ 89% buy ratings, mean target $475 (+13% upside)

  → Calling get_financials(symbol=MSFT)
  ✓ Revenue +15% YoY, 42% gross margin, $87B FCF

**Fundamental Assessment**: STRONG
- Exceptional profitability (42% ROE)
- Consistent earnings outperformance
- Strong analyst conviction
- Reasonable valuation (31x P/E vs 15% growth)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: MACRO VALIDATION (Macro Lens)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Macro Lens (Market Strategist):
  → Calling get_key_macro_indicators()
  ✓ GDP +2.4%, CPI +3.1%, Unemployment 3.7%

  → Calling get_treasury_yield_curve()
  ✓ 10Y-2Y inverted -0.54% (recession warning)

  → Calling get_market_indices()
  ✓ S&P 500 +12% YTD, Nasdaq -8% from highs, VIX 14.2

**Macro Context**: LATE EXPANSION with CAUTION
- Inverted yield curve signals recession risk (12-18 month window)
- Tech sector vulnerability (Nasdaq off highs)
- But Microsoft has defensive characteristics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: FINAL SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RECOMMENDATION: BUY (Dollar-Cost Average)
📊 Confidence Level: MEDIUM

**Key Reasoning**:

Microsoft shows exceptional fundamental quality:
- 42% ROE, $87B annual FCF (best-in-class capital efficiency)
- Strong competitive moats (Azure cloud, enterprise software lock-in)
- Consistent earnings beats (+4.2% avg surprise, 4 quarters)
- 89% analyst buy ratings, $475 mean target (+13% upside)

However, macro timing suggests staged entry:
- Late expansion phase (GDP slowing from 2.8% to 2.4%)
- Inverted yield curve (-0.54%) signals 70% recession probability
- Tech sector vulnerable (Nasdaq -8% from highs)

**Suggested Action**:

Instead of full position immediately, dollar-cost average over 3-6 months:
- Tranche 1: 40% now (defensive exposure to quality)
- Tranche 2: 30% if MSFT dips below $390 (-7% from current)
- Tranche 3: 30% if macro deteriorates (recession confirmed)

Microsoft's defensive characteristics (enterprise subscriptions,
recurring revenue) position it to outperform cyclical tech peers
in downturn.

**Risk Warnings**:

1. **Fundamental**: Azure growth deceleration below 25% YoY would
   weaken investment thesis
2. **Valuation**: Recession could compress P/E to 24-26x (historical
   trough), implying 15-20% downside
3. **Macro**: If yield curve steepens rapidly, indicates imminent
   recession—pause accumulation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Report saved to: reports/MSFT_analysis_20251008_143022.md
```

</details>

---

## 📚 Documentation

### User Guides

- 🚀 **[Getting Started](docs/user-guide/getting-started.md)** - Installation, setup, first queries, troubleshooting
- ❓ **[FAQ](docs/faq.md)** - 100+ answered questions covering all features
- 🤖 **[Agents Guide](docs/user-guide/agents.md)** - Complete reference for all 9 specialized agents
- 🔀 **[Multi-Agent Workflows](docs/user-guide/multi-agent-workflows.md)** - Agent collaboration patterns
- 🛠️ **[API Tools](docs/user-guide/api-tools.md)** - Data sources and tool capabilities

### Developer Resources

- 📦 **[PyPI Package](https://pypi.org/project/navam-invest/)** - Latest releases and version history
- 🔧 **[GitHub Repository](https://github.com/navam-io/navam-invest)** - Source code, issues, pull requests
- 🏗️ **[Architecture](docs/architecture/about.md)** - System design and technical overview
- 📝 **[Release Notes](backlog/)** - Detailed changelog for each version
- 📖 **[LangGraph Guide](refer/langgraph/)** - Multi-agent patterns & best practices

### API Documentation

- **[Anthropic Claude](https://docs.anthropic.com/)** - AI reasoning engine
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - Agent orchestration framework
- **[Yahoo Finance (yfinance)](https://github.com/ranaroussi/yfinance)** - Free market data library
- **[SEC EDGAR](https://www.sec.gov/edgar/sec-api-documentation)** - Corporate filings API
- **[Alpha Vantage](https://www.alphavantage.co/documentation/)** - Stock market data
- **[Tiingo](https://www.tiingo.com/documentation/)** - Historical fundamentals
- **[Finnhub](https://finnhub.io/docs/api)** - Alternative data & sentiment
- **[FRED](https://fred.stlouisfed.org/docs/api/fred/)** - Economic indicators

---

## 🗺️ Roadmap

### Current Release: v0.1.34 (In Development)

**Latest Features**:
- ✅ **Tax Scout Agent**: Tax-loss harvesting, wash-sale compliance, year-end planning
- ✅ **Risk Shield Agent**: Portfolio risk management, VAR, drawdown analysis (v0.1.33)
- ✅ **News Sentry Agent**: Real-time 8-K monitoring, insider tracking, breaking news (v0.1.32)
- ✅ **Enhanced Documentation**: Reorganized docs with FAQ, getting started guide
- ✅ **Smart Input Management**: Auto-disable during processing, clear status feedback
- ✅ **Auto-Save Reports**: All responses >200 chars saved to `reports/`

**Planned for v0.1.35** (Q1 2025):
- [ ] **Hedge Smith Agent**: Options strategies, protective puts, covered calls
- [ ] **API Caching Layer**: DuckDB-based caching to reduce API calls
- [ ] **Enhanced Workflows**: Parallel agent execution, conditional branching

### Future Releases

**v0.2.0+** (Q2 2025):
- [ ] **Backtesting Engine**: Test investment strategies on historical data
- [ ] **Web UI**: Browser-based interface (in addition to TUI)
- [ ] **State Persistence**: PostgreSQL checkpointer for LangGraph
- [ ] **Cloud Deployment**: LangGraph Cloud integration
- [ ] **Custom Agents**: User-defined agent templates and tools
- [ ] **Python SDK**: Programmatic API for third-party integrations

### Recent Releases

<details>
<summary><b>v0.1.33 (Oct 9, 2025) - Risk Shield Agent</b></summary>

- ✅ Portfolio risk management (VAR, drawdown, concentration)
- ✅ 18 specialized tools across market data and macro indicators
- ✅ Comprehensive system prompt with risk assessment frameworks
- ✅ TUI integration with `/risk` command

[Full Release Notes](backlog/release-0.1.33.md)

</details>

<details>
<summary><b>v0.1.32 (Jan 12, 2025) - News Sentry Agent</b></summary>

- ✅ Real-time 8-K monitoring and insider tracking
- ✅ Event prioritization (CRITICAL/HIGH/MEDIUM/LOW)
- ✅ 13 specialized tools for event detection
- ✅ TUI integration with `/news` command

[Full Release Notes](backlog/release-0.1.32.md)

</details>

<details>
<summary><b>v0.1.31 (Jan 10, 2025) - UX Improvements</b></summary>

- ✅ Enhanced input management (auto-disable during processing)
- ✅ Increased max_tokens to 8192 (no more truncated responses)
- ✅ Automatic report saving for all agent responses
- ✅ Live footer status updates ("Processing..." → "Ready")

[Full Release Notes](backlog/release-0.1.31.md)

</details>

---

## 🤝 Contributing

We welcome contributions! Navam Invest is built by retail investors, for retail investors.

### Ways to Contribute

- 🐛 **[Report Bugs](https://github.com/navam-io/navam-invest/issues)** - Submit detailed bug reports
- 💡 **[Suggest Features](https://github.com/navam-io/navam-invest/issues)** - Share ideas for new agents or workflows
- 📝 **[Improve Docs](https://github.com/navam-io/navam-invest/pulls)** - Make documentation clearer
- 🔧 **[Submit PRs](https://github.com/navam-io/navam-invest/pulls)** - Code contributions for bugs or features

### Development Workflow

1. **Fork and clone**: `git clone https://github.com/your-username/navam-invest.git`
2. **Create branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with tests and documentation
4. **Run quality checks**:
   ```bash
   black src/ tests/        # Format code
   ruff check src/ tests/   # Lint
   mypy src/                # Type check
   pytest                   # Run tests
   ```
5. **Commit**: `git commit -m "feat: Add amazing feature"`
6. **Push and create PR** with detailed description

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

**Key Points**:
- ✅ Free for personal and commercial use
- ✅ Modify and distribute as you wish
- ✅ No warranty provided

---

## 🙏 Acknowledgments

### Core Technologies

- **[Anthropic](https://www.anthropic.com/)** - Claude AI reasoning engine (Sonnet 4.5)
- **[LangChain](https://www.langchain.com/)** - Agent framework ecosystem (LangGraph orchestration)
- **[Textual](https://textual.textualize.io/)** - Modern terminal UI framework

### Data Providers

- **[Yahoo Finance](https://finance.yahoo.com/)** - Free real-time quotes, earnings, analyst ratings
- **[SEC EDGAR](https://www.sec.gov/edgar)** - Corporate filings (10-K, 10-Q, 8-K, Form 4)
- **[U.S. Treasury](https://home.treasury.gov/)** - Yield curves, treasury rates
- **[Alpha Vantage](https://www.alphavantage.co/)** - Stock market data
- **[Tiingo](https://www.tiingo.com/)** - Historical fundamentals
- **[Finnhub](https://finnhub.io/)** - Alternative data & sentiment
- **[FRED](https://fred.stlouisfed.org/)** - Federal Reserve economic data
- **[NewsAPI.org](https://newsapi.org/)** - Market news & headlines

---

<div align="center">

**Built with ❤️ for retail investors**

[![Star on GitHub](https://img.shields.io/github/stars/navam-io/navam-invest?style=social)](https://github.com/navam-io/navam-invest)
[![Follow on Twitter](https://img.shields.io/twitter/follow/navam_io?style=social)](https://twitter.com/navam_io)

[⬆ Back to Top](#-navam-invest)

</div>
