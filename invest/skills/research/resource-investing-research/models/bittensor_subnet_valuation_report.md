# Bittensor Subnet Token Valuation Framework

**Based on:** Yuma Subnet Tokens Report (Jan 2026)  
**Date:** April 25, 2026  
**TAO Price:** $249.91 USD  
**Live Subnets:** 129  
**Source:** https://www.yumaai.com/assets/reports/Yuma_Subnet_Tokens_Report_2026.pdf

---

## Executive Summary

The Yuma paper establishes a **fundamental valuation framework** for Bittensor subnet tokens based on a single insight: **subnet tokens are operational expense replacements**, not equities or governance tokens. This reframes valuation from "what is this company worth?" to "what is the cost of the work this subnet replaces?"

**Key formula:**

```
Fundamental Token Value = Daily OpEx Replacement / Daily Miner Emissions
```

**Our adaption:** Most subnets are too early-stage to have observable internal OpEx. We propose a **phased valuation method** that adapts the Yuma framework by maturity:

| Stage | Valuation Method | Example Subnets |
|-------|-----------------|-----------------|
| **Speculative** (no revenue, no identifiable buyers) | Reserve/option value + probability-weighted boundary analysis | SN70 (NexisGen), SN117 (BrainPlay), SN128 (ByteLeap) |
| **Early** (active miners, identifiable use case, no known revenue) | Comparable OpEx proxy + emission schedule | SN2 (DSperse — inference), SN4 (Targon — compute) |
| **Maturing** (known users, visible demand, potential token buybacks) | Yuma's original OpEx replacement model | SN1 (Apex), SN64 (Chutes) |
| **Root** (TAO itself) | Network-wide staking + emission value | SN0 |

---

## Part 1: The Yuma Framework (Paper Summary)

### Core Thesis

Subnet tokens are **vendor agreements** for outsourced compute, inference, data, or specialized labor. They replace internal operational expenses (developer salaries, cloud compute, model training costs) with a tokenized incentive layer.

> "Rational companies will buy the amount of tokens required to incentivize the operational goal at a given time — no more, no less — just as they would treat any other operational cost."
> — Yuma Report

### Valuation Methodology (from the paper)

**Step 1: Forecast OpEx Replacement**
- Bottoms-up analysis, comparable company analysis, or management forecasts
- Example: Company X needs $2M/year on an engineering team for model training

**Step 2: Translate to required emissions value**
```
Daily OpEx Replacement = $2,000,000 / 365 = $5,479/day
Daily Miner Emissions = 7,200 * 0.41 = 2,952 subnet tokens/day
Fundamental Token Value = $5,479 / 2,952 = $1.86/token
```

**Step 3: Apply supply curve (halving schedule)**
- Bittensor subnets have fixed 21M token supply
- Emissions halve over time
- Forward price curve adjusts for declining emissions
- Example 4-year projection: **$18.97/token**

**Step 4: DCF for investor returns**
```
PV = Σ (Required Emissions Value on day t) / (1 + r)^(t/365)
```
- Discount rate: 30% (early-stage spec)
- Miner emissions assumption: what % miners sell daily
- Staking returns reduce required investor purchases

### Critical Insight: Speculative → Fundamental Transition

Yuma identifies a **transition point** where company revenue replaces investor speculation:
- Early: investors buy tokens to fund emissions, subsidizing miner participation
- Late: companies generating revenue from subnet outputs buy tokens to maintain incentives
- The inflection point determines whether a subnet survives or dies

---

## Part 2: Practical Subnet Valuation Framework

Since most subnets do not publicly report revenue or OpEx data, we adapt Yuma's framework using **observable on-chain proxies** and **maturity staging**.

### Stage Classification

| Stage | Criteria | Valuation Approach |
|-------|---------|-------------------|
| **Speculative** | No identifiable product, no visible users, generic description | Probability-weighted boundary analysis (will this subnet ever have buyers?) |
| **Early** | Clear use case, active miners, but no known revenue | Comparable OpEx proxy (what would this cost internally?) |
| **Maturing** | Known users/partners, visible demand, token buybacks likely | Direct OpEx replacement model per Yuma |
| **Root (SN0)** | TAO staking, validator rewards, network security | Traditional staking yield + network growth model |

### Observable On-Chain Metrics

| Metric | Source | What It Tells Us |
|--------|--------|-----------------|
| **Token price (in TAO)** | `subtensor.get_subnet_price()` | Market-implied value relative to TAO |
| **UID fill rate** | `subnetwork_n / max_n` | Miner demand / competition to participate |
| **Burn cost** | `subnet.burn` | Cost to register a UID (signal of entry barriers) |
| **Emission share** | `subnet_emission` | TAO flowing to subnet (proxy for network priority) |
| **Alpha in/out** | `alpha_in`, `alpha_out` | Token supply dynamics, staking activity |
| **Tempo** | `tempo` | Block frequency of updates (higher = more active) |
| **Mechanism count** | `get_mechanism_count()` | Complexity of incentive structure |
| **Price trend** | Historical CSV tracking | Whether price is converging to or diverging from fundamental |

### Valuation Formula by Stage

#### Speculative Stage:
```
Fair Value = Prob(Survival) × Boundary_Value + Prob(Death) × Liquidation_Value

Boundary_Value = max(Comparable_OpEx_Estimate, Token_Reserve_Value)
Prob(Survival) = f(UID_fill, burn_cost, team_track_record, use_case_clarity)
```

#### Early Stage:
```
Fair Value = (Daily_OpEx_Proxy × 365) / (Daily_Emissions × TAO_Price)

OpEx_Proxy examples:
- Inference subnet: Internal OpenAI API spend equivalent
- Compute subnet: AWS/GCP compute cost equivalent  
- Data subnet: Data vendor licensing cost equivalent
- Trading subnet: Prop desk infrastructure cost equivalent
```

#### Maturing Stage:
```
Fair Value = Yuma's original formula

= Daily_OpEx_Replacement / Daily_Miner_Emissions
+ PV of future emissions (investor return component)
- Adjustment for miner sell pressure
- Adjustment for validator take
```

---

## Part 3: Applying the Framework — Concrete Examples

### SN1: Apex (α)

**Description:** Open competitions for algorithmic and agentic optimization  
**Token:** α (alpha)  
**Price:** 0.0111 TAO ($2.77)  
**UIDs:** 256/256 (100% full)  
**Burn:** 0.0031 TAO  
**Tempo:** 99 (~100 blocks per epoch)

**Valuation Assessment:**
- **Stage:** Early → Maturing transition
- **Use case:** Highly specific — algorithmic optimization competitions
- **Comparable OpEx:** Internal quant development / Kaggle-style prize pools
- **Estimated annual OpEx replacement:** $500K-2M (small quant shop prize pool equivalent)
- **Daily emissions:** 2,952 α/day (per Yuma example)
- **Fundamental value estimate:** $0.50-2.00/α
- **Current price:** $2.77
- **Verdict:** Fairly priced to slightly expensive. 100% UID fill and active tempo suggest demand, but limited identifiable revenue buyers.

**Risk:** Niche use case may not scale beyond quant/crypto community.

---

### SN2: DSperse (β)

**Description:** Verifiable and distributed inference on Bittensor  
**Token:** β (beta)  
**Price:** 0.00678 TAO ($1.69)  
**UIDs:** 256/256 (100% full)  
**Burn:** 0.0005 TAO  
**Tempo:** 360

**Valuation Assessment:**
- **Stage:** Early
- **Use case:** Clear and structural — distributed LLM inference
- **Comparable OpEx:** OpenAI API costs, Together AI, Anthropic Claude API
- **Estimated demand proxy:** A single mid-size AI app spending $50K-200K/month on inference
- **Annual OpEx replacement:** $600K-2.4M
- **Daily emissions:** ~2,952 β/day (standard subnet)
- **Fundamental value:** $0.55-2.20/β
- **Current price:** $1.69
- **Verdict:** **Attractive** — within fundamental range, clear use case, high UID fill

**Catalyst:** If DSperse captures even 1% of global inference demand that would otherwise go to OpenAI, this is a 10x+ token.

**Risk:** Inference is commoditizing; rate at which DSperse can maintain quality premium vs centralized APIs.

---

### SN4: Targon (δ)

**Description:** Incentivized Compute Marketplace powered by the Targon Virtual Machine  
**Token:** δ (delta)  
**Price:** 0.05816 TAO ($14.53)  
**UIDs:** 256/256 (100% full)  
**Burn:** 0.0005 TAO  
**Tempo:** 360

**Valuation Assessment:**
- **Stage:** Early → Maturing
- **Use case:** General compute marketplace
- **Comparable OpEx:** AWS EC2, Lambda, Cloudflare Workers, Akash Network
- **Estimated annual OpEx replacement:** $2-10M (if capturing meaningful compute demand)
- **Fundamental value:** $1.85-9.25/δ
- **Current price:** $14.53
- **Verdict:** **Likely expensive** — price implies $15M+/year OpEx replacement assumption

**Why expensive:** Compute marketplaces are crowded (Akash, Golem, Render). Targon needs to differentiate via Bittensor incentives or VM features. At 0.058 TAO, the market is pricing in full maturation.

**Risk:** Compute is commodity; Bittensor overhead may not justify switching from AWS.

---

### SN8: Vanta (θ)

**Description:** Decentralized liquidity and execution engine for prop firms and traders  
**Token:** θ (theta)  
**Price:** 0.03669 TAO ($9.17)  
**UIDs:** 256/256 (100% full)

**Valuation Assessment:**
- **Stage:** Early (financial services are hard to decentralize)
- **Use case:** Prop firm execution / liquidity provision
- **Comparable OpEx:** Tradfi execution infrastructure (FIX engines, co-location, prime brokerage)
- **Annual OpEx proxy:** $1-5M (very rough — prop firm tech stacks are opaque)
- **Fundamental value:** $0.90-4.50/θ
- **Current price:** $9.17
- **Verdict:** **Expensive** — financial service subnets face regulatory + trust barriers

**Risk:** Prop firms are paranoid about execution quality. Decentralized execution is an extremely hard sell.

---

### SN64: Chutes (ش)

**Description:** Decentralized AI inference infrastructure  
**Token:** ش  
**Price:** 0.08283 TAO ($20.70)  
**UIDs:** 256/256 (100% full)

**Valuation Assessment:**
- **Stage:** Maturing
- **Use case:** AI inference at scale — direct competitor to centralized inference APIs
- **Comparable OpEx:** OpenAI + Anthropic + Together AI combined spend for mid-size AI companies
- **Annual OpEx proxy:** $5-20M+ (if Chutes is capturing real demand)
- **Fundamental value:** $4.60-18.50/ش
- **Current price:** $20.70
- **Verdict:** **Premium but justifiable** — this is the highest-priced legitimate subnet because inference is the clearest Bittensor use case

**Catalyst:** If Chutes secures a major AI company as a consumer, $20/token becomes cheap.

**Risk:** Inference commoditization; can decentralized infra match centralized latency/quality?

---

### SN96: Verathos (᚛)

**Description:** Unknown / limited public info  
**Token:** ᚛  
**Price:** 2.96609 TAO ($741.25)  
**UIDs:** 250/256  
**Burn:** 0.0005 TAO

**Valuation Assessment:**
- **Stage:** Speculative / Unknown
- **Price:** **741x the cheapest subnets**
- **Verdict:** **Almost certainly bubble/speculative premium** unless there's a massive undisclosed revenue buyer

This is either:
1. A massive speculative bubble (most likely)
2. A subnet with a whale/pump partner propping up price
3. A genuinely revolutionary subnet with hidden fundamentals

**Risk:** Extreme. At 2.97 TAO, a 50% drawdown is $370/token.

---

### SN0: Root (Τ)

**Description:** TAO root subnet — validator staking, governance, network security  
**Token:** TAO itself  
**Price:** 1.0 TAO ($249.91)  
**UIDs:** 64/64

**Valuation Assessment:**
- This is **not a subnet token** — it's the network token
- Value = present value of all future subnet emissions + staking yield
- Traditional crypto valuation: Metcalfe's Law × network growth + staking yield floor
- At $250, TAO is pricing in significant network growth
- **Verdict:** Fair for a growing AI/crypto network with 129 subnets, but not cheap

---

## Part 4: Live Subnet Market Summary

| NetUID | Name | Symbol | Price (TAO) | Price (USD) | UID Fill | Stage | Fundamental Range (USD) | Verdict |
|--------|------|--------|------------|-------------|----------|-------|------------------------|---------|
| 1 | Apex | α | 0.011 | $2.77 | 100% | Early | $0.50-2.00 | Fair/Expensive |
| 2 | DSperse | β | 0.007 | $1.69 | 100% | Early | $0.55-2.20 | **Attractive** |
| 4 | Targon | δ | 0.058 | $14.53 | 100% | Early→Maturing | $1.85-9.25 | Expensive |
| 8 | Vanta | θ | 0.037 | $9.17 | 100% | Early | $0.90-4.50 | Expensive |
| 15 | ORO | ο | 0.035 | $8.76 | 100% | Early | Unknown | Neutral |
| 34 | BitMind | י | 0.014 | $3.50 | 100% | Early | $0.50-2.00 | Fair |
| 44 | Score | ף | 0.035 | $8.68 | 100% | Early | Unknown | Neutral |
| 51 | lium.io | ת | 0.056 | $13.99 | 100% | Early | Unknown | Neutral |
| 56 | Gradients | ج | 0.022 | $5.43 | 100% | Early | Unknown | Neutral |
| 62 | Ridges | ز | 0.029 | $7.22 | 100% | Early | Unknown | Neutral |
| 64 | Chutes | ش | 0.083 | $20.70 | 100% | Maturing | $4.60-18.50 | Premium/Justifiable |
| 66 | ninja | ض | 0.015 | $3.76 | 100% | Speculative | Unknown | Neutral |
| 68 | NOVA | ظ | 0.017 | $4.20 | 100% | Early | Unknown | Neutral |
| 75 | Hippius | م | 0.024 | $6.12 | 100% | Early | Unknown | Neutral |
| 85 | Vidaio | ᚱ | 0.012 | $3.02 | 100% | Early | Unknown | Neutral |
| 91 | Bitstarter #1 | ᚁ | 0.012 | $2.90 | 100% | Early | Unknown | Neutral |
| 93 | Bitcast | ᚃ | 0.015 | $3.65 | 100% | Early | Unknown | Neutral |
| 95 | nion | ᚅ | 0.028 | $6.91 | 100% | Early | Unknown | Neutral |
| 96 | Verathos | ᚛ | **2.966** | **$741.25** | 97% | Speculative | Unknown | **Bubble Risk** |
| 97 | distil | ა | 0.049 | $12.24 | 100% | Early | Unknown | Neutral |
| 105 | Beam | Գ | 0.010 | $2.49 | 100% | Early | Unknown | Neutral |
| 107 | Minos | ミ | 0.016 | $4.02 | 100% | Early | Unknown | Neutral |
| 114 | SOMA | Ե | 0.010 | $2.43 | 100% | Early | Unknown | Neutral |
| 120 | Affine | ⴷ | 0.072 | $17.90 | 100% | Early | Unknown | Neutral |

**Bottom 20 (all ~0.003-0.004 TAO):** Most are speculative/junk subnets with no clear use case. Price reflects absence of buyers.

---

## Part 5: The Investment Implications for You

### What This Means for a Value Investor

Bittensor subnet tokens are **not value plays** in the traditional sense. They are:
- **Venture-stage options** on AI compute/inference/data use cases
- **Dependent on network effects** — they only work if enough miners participate
- **Illiquid** — thin markets, no order books, subnet-dex only
- **Pre-revenue or early-revenue** — most have no identifiable revenue buyers

**The closest parallel in your framework:** WRN (Western Copper & Gold). Both are pre-production assets where you're betting that:
1. The underlying resource/infrastructure gets built
2. Demand materializes when it does
3. The token value converges to fundamental value

### Applying Rick Rule's "5P" to Subnets

| P | How to Score Subnets |
|---|---------------------|
| **People** | Subnet team's track record, GitHub activity, community engagement. Can they execute? |
| **Property** | Use case defensibility, technical moat, data/process exclusivity. Is the subnet doing something unique? |
| **Politics** | Regulatory risk (finance subnets = SEC risk; data subnets = GDPR risk), Bittensor protocol changes |
| **Phinance** | Token economics: inflation rate, burn mechanisms, validator take, miner sell pressure. Is the token sink sustainable? |
| **Paper** | Token price vs fundamental OpEx replacement value. Is it cheap for what it could be worth if successful? |

### The "Bittensor Basket" Approach

Instead of picking individual subnet winners, consider a **basket allocation**:

| Subnet | Allocation | Rationale |
|--------|-----------|-----------|
| **SN2 (DSperse)**
| 25% | Inference is the clearest Bittensor use case |
| **SN4 (Targon)** | 15% | Compute marketplace, highly competitive but large TAM |
| **SN64 (Chutes)** | 20% | Premium inference, closest to maturing |
| **SN1 (Apex)** | 10% | Niche but active community, algorithmic optimization |
| **TAO (root)** | 30% | Diversified exposure to all subnets via staking |

**Total allocation:** 2-5% of portfolio (speculative / venture bucket)

### What to Track

1. **Subnet revenue buyers:** Which subnets have identifiable companies buying tokens to fund emissions?
2. **UID dynamics:** Subnets losing UIDs = dying; gaining UIDs = thriving
3. **Burn cost trends:** Rising burn = more demand to participate
4. **TAO price correlation:** Subnet tokens generally trade as TAO-leveraged beta
5. **Protocol upgrades:** Bittensor SN1-dymanic (subnet 1) developments

---

## Part 6: Key Risks Specific to Bittensor Subnets

### 🔴 Protocol Risk
Bittensor is a live experiment. Subnet token economics could be changed by governance. The 21M fixed supply per subnet is a protocol rule — but rules can change.

### 🔴 Validator Centralization
Validators control weight setting, which drives miner rewards. A cabal of validators could extract rent or censor subnets. Track validator concentration.

### 🔴 Miner Sell Pressure
Miners incur hardware/power costs and must sell tokens to cover them. If all miners sell 100%, the token price collapses unless external buyers step in. The Yuma model assumes this is the equilibrium.

### 🔴 "White Elephant" Risk
Many subnets ($0.003 tokens) will never attract real users. They exist because registering a subnet is cheap. These are zombie subnets — avoid them entirely.

### 🟡 Regulatory Risk
Finance-focused subnets (SN8 Vanta, SN114 SOMA) could attract SEC/FCA scrutiny. Decentralized = not a free pass.

### 🟡 TAO Dilution
TAO itself inflates at ~7% annually via emissions. Subnet token holders are effectively being diluted by TAO issuance unless subnet token appreciation outpaces it.

---

## Part 7: How to Automate Tracking

### Proposed Integration with Existing Scheduler

Extend the daily resource-investing cron to include Bittensor subnet data:

**New source:** `bittensor_subnets`
- **Periodicity:** Daily 07:30 UTC
- **Method:** `bittensor` Python SDK
- **Data fetched:** Per-subnet token price, UID fill rate, burn cost, emission share
- **Output:** `subnet_prices.csv` in prices_history
- **Alert triggers:** 
  - Price >2x fundamental range (bubble alert)
  - UID fill dropping below 50% (subnet dying)
  - New subnet registration with <0.01 TAO price (screener)

**Implementation:**
```python
from bittensor import Subtensor
subtensor = Subtensor(network='finney')
# Fetch all subnet prices, save to CSV
# Compare to prior day for change_pct
# Flag anomalies
```

---

## Bottom Line

**Bittensor subnets are not value investments** — they're venture-stage options on decentralized AI infrastructure. The Yuma framework provides the right mental model (OpEx replacement), but applying it requires knowing which subnets have real demand buyers.

**For your portfolio:**
- Allocate **2-5% max** to a Bittensor basket
- Focus on **SN2 (inference)** and **SN64 (Chutes)** as the clearest use cases
- Avoid anything priced >0.05 TAO unless you can identify a revenue buyer
- **Avoid SN96** at 2.97 TAO — this is either a bubble or insider game
- Track the migration from speculative to fundamental value — that's your buy signal

**The highest-conviction thesis:** If Bittensor becomes a meaningful alternative to OpenAI/Anthropic for inference, the inference subnets (DSperse, Chutes) are 10-50x from current prices. If it doesn't, most subnet tokens go to zero.

---

*Disclaimer: Subnet tokens are highly speculative, illiquid, and pre-revenue. Most will fail. This framework provides a valuation discipline, not a guarantee of returns. Position size accordingly.*
