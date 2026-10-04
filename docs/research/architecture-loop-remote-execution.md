# 架構方法、Loop 與遠端執行整合

狀態：方向已接受；技能原始碼整合、遠端執行及試點尚未完成。

2026-10-04，owner 同意前述整合方向，並選擇 Mac Mini 作為第一個遠端試點。這份文件記錄該決定及後續工作；它不取代產品 PRD、architecture、PLAN/RUN 或 action grants。

## 基準與本輪範圍

- Repository：`product-delivery-harness`。
- 分支：`codex/harness-flow-modernization`。
- 原始碼基準：`1782fa000b107396fd36787c7df7fad8a2141c82`，觀察時工作樹乾淨。
- 觀察時間：2026-10-04 02:39 UTC-7。
- 原始碼與觀察到的 installed Harness：`0.60.0`；session 載入身份未知。
- pstack 參考固定在 [cursor/plugins@e43c7ee2](https://github.com/cursor/plugins/commit/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a)。這是參考來源，不是待安裝套件。
- 本輪寫入僅限這份文件、配套 Epic 和 `docs/DOCUMENTS.md`。UI impact：`none`；直接工作，不建立 PLAN/RUN。

## 責任分工

| 層次 | 責任與既有權威 | 整合方向 |
| --- | --- | --- |
| Product Definition | 批准的 PRD、architecture、stack，以及中文審閱副本 | 補強概念上的狀態限制、資料寫入者和恢復行為；具體程式簽名不成為產品必填欄位。 |
| 實作架構 | `code_architect` 的衍生任務交付 | 先展示呼叫方式，再推導介面、型別及模組；結果不能自行批准產品或技術決策。 |
| Harness execution | Parent 的直接任務/Epic 或 PLAN/RUN、selector、attempt、lease 和 evidence | 保留單一執行狀態及累積修復預算。 |
| Automation / loop | 已授權範圍內的喚醒及改善方法 | 喚醒後先觀察、對帳及選擇工作；不自行建立新任務或擴張權限。 |
| 遠端執行 | 未來版本化 adapter 的任務/結果邊界 | 在指定機器執行有界工作，回傳可核對證據；Parent 保留協調、驗收記錄和整合。 |

產品自身的排程、agent workflow 與 durable execution 仍屬於產品 architecture。讓 agent 定期回訪 repository 則屬於 Harness host 的操作能力；兩者不互相授權。

## Core architecture 第一輪

先整合到既有 `code_architect`、任務與 reviewer packet；Product Definition 僅補充產品層級的設計指引。現有產品架構 packet 已涵蓋 ownership、重試、重複效果及恢復，不重複建立另一份規格。

1. 寫出真實呼叫例，再推導介面、型別與模組責任。
2. 指明每份可變狀態的擁有者、讀取方式、不可成立的狀態，以及外部資料的驗證邊界。
3. 在耦合、耐久性、信任或遷移選擇尚未解決時，比較結構不同的方案。局部修正沿用有效決策，不強制開方案競賽。
4. 對有副作用的操作列出重複執行及中途失敗的結果，連接既有 TEST 與 verifier。
5. 同一前提下重複失敗時，記錄前提及可重跑的觀測。Actor census 適用於角色、負載或並行失衡，不套用到每個編譯錯誤。

設計重整不重置修復次數，不授權整個產品重寫。工具或環境失敗須獨立分類，不能直接當成架構錯誤。

第一輪不增加強制產品欄位，不改 `check_product_package.py` 的 schema，不遷移歷史批准或 pinned RUN。若日後接受新的必填契約，另做版本化驗證及相容性工作。

## 有界 loop 方法

執行前固定範圍、可用動作、輸入版本、量測方法、基準、成功條件、退化限制，以及適用的時間/次數/成本上限。量測須先證明能辨識真實差異；不以任意固定最低迭代次數延長已有效達標的工作。

每輪只處理一個可檢驗假設：觀察現況 → 修改 → 用固定方法量測及回歸驗證 → 記錄結果 → 下一輪或停止。保留每次候選、失敗、量測、scope 和 SHA；拒絕假設不代表自動 reset、刪除工作或清除證據。

喚醒先尊重 pause/cancel/completion，再核對 live attempt、Git、實際能力和既有授權。操作結果不確定時先查證，不盲目重複執行。成功、耗盡預算、無法驗證或需要範圍決策，均留下明確結果；不為取得 PASS 降低門檻。

方法接到既有 graph、RUN 和 receipts。第一輪不引入第二個 scheduler、進度資料庫或 canonical decision log，也不建立實際排程。

## Cloud Agent 與 Mac Mini 試點

Cloud Agent 指遠端執行節點，可位於 Mac Mini、其他電腦或雲端伺服器。機器身份、agent runtime 與 model provider 分別觀察，按實際能力分派任務。

現有 [runtime adapter](../../skills/delivery-harness/references/runtime-adapters.md) 有 native/bridge、能力及結果核對契約，但沒有任意跨機器派工。[Serialized Same-Repository Host Handoff](../../skills/delivery-harness/references/execution-state-model.md#serialized-same-repository-host-handoff) 明確要求未來 schema 先定義 portable workspace identity 和 evidence transport。相同 repository 路徑不能當成已存在的跨機器能力。

未來 remote boundary 至少要能核對：

| 項目 | 必須觀察的事實 |
| --- | --- |
| 執行身份 | 機器/worker/session 的實際身份、role、runtime、model 及適用工具能力；未知不能當成已驗證。 |
| 任務身份 | 唯一 assignment/attempt、批准的範圍、固定 source SHA、必要檔案 hashes、build/config 和 acceptance-contract 身份。 |
| 工作區 | 可攜身份、實際 source fingerprint、獨立 fixture/結果位置，以及檔案、網路、帳號和程序的邊界。 |
| Skills | 觀察 installed 與實際讀取/採納的契約；child 自行核對所需 digest，不照抄 parent 的身份宣告。 |
| 結果來源 | 驗證 transport/host/session 的來源；hash 只能證明檔案 bytes，不能獨自證明結果真實。 |
| 程序與恢復 | 明確的開始、完成、取消、期限和 partial-result 行為；斷線不是終止證據。 |
| 證據 | 實際 command/exit/assertion、平台與環境、適用圖片/影片及 redacted logs；父端保留並核對 hashes。 |

這些是待實作概念，不是已存在的 RUN 欄位。版本化 schema、probes、派工、身份驗證及結果 admission 必須一起生效；舊 pins 保留原語義。

### 兩種初始工作

| Profile | 工作 | 結果與邊界 |
| --- | --- | --- |
| Error report 檢測 | 收集、去重、分類，在固定版本嘗試重現 | 已重現/未重現/受阻、步驟和觀測證據。修復另沿用既有寫入範圍、角色與審查。 |
| 新功能技術驗收 | 跑批准的 PRD/TEST 案例及固定 acceptance matrix | 實際 assertion、build/config、環境與證據。結果不代替 owner 或 Visual Approval。 |

Mac Mini 只有在所需 Xcode、Simulator/device 和專案 runner 已觀察時，才接相應 native 工作；Web/API/CLI 依各自工具能力分派。不能用瀏覽器投影代替 native 驗收。

遠端證據由 Parent 核對來源、任務及 candidate，匯入既有 [delivery acceptance](../../skills/delivery-harness/references/delivery-acceptance-contract.md)。驗收案例跑於 H1；僅記錄/證據的 parent-local commit 形成 H2，再跑 H2 的既有 gate 與必要 review。單獨的遠端成功訊息不能取得 PASS。

### 已選目標與待確認資料

- 已選：Mac Mini。
- Codex project inventory 本次僅觀察到 `hostId: local`，未見已連接的 Mac Mini；這不是對其他連線方式的全機掃描。
- Owner 指定 Tailscale 作為連線方式。本機 Tailscale 為 `Running`，peer inventory 顯示一台名稱符合的 Mac Mini，OS 為 `macOS`，`Online: true`。這是本次觀測，不是持續在線保證。
- 裝置 DNS/IP 留在當次連線資訊，不寫入公開原始碼文件。Tailscale 連線不等於已存在 remote agent、SSH 權限或可用驗收工具。
- 未知：遠端執行通道、runtime、工作區、工具能力及目標產品案例。
- 不讀取或複製 credential/.env；連線識別與工具能力也不等於副作用權限。

首個 transport smoke 可用本 repository 固定 SHA 的有限 source check，驗證派工及結果往返；那只證明傳輸，不算新功能驗收。真正的產品試點再選一個已有可執行 runner 的有界案例。沒有執行通道及能力證據前，不啟動遠端工作或安裝工具。

## 後續原子工作

| 順序 | 最小工作 | 驗證 |
| --- | --- | --- |
| T1 | 記錄接受的分工、Mac Mini 選擇、試點與未解依賴 | 文件連結、scope/status 和 Git diff 檢查。 |
| T2 | Core architecture 的任務交付、適用觸發及 review 方法 | 初次架構、enhancement、小修正及批准邊界案例；既有結果 schema 不變。 |
| T3 | 有界 loop 方法與既有狀態/預算的映射 | pause/cancel、未知效果、預算耗盡及 changed-SHA 的負面案例。 |
| T4 | 版本化 remote contract、transport binding、能力與 result admission | 重複/未知 attempt、錯版本、skills mismatch、偽造來源、斷線及相容性案例。 |
| T5 | 一台 Mac Mini、一個固定版本的往返試點 | 真實身份、有限工作、原始結果、停止/恢復及證據保留。 |
| T6 | 一個 error-report 案例與一個產品技術驗收案例，各自交付 | 真實觀測、平台相符及現有 acceptance gate；不以 transport smoke 代替。 |
| T7 | 在遠端任務可靠後接入選定 host 的 automation 喚醒方式 | 喚醒不授權新操作；不重複派工；僅在有意義的變化時通知。 |

每個實作結果獨立驗證及 commit。技能/規則/flow 真正變更時，同步四份 README；release、安裝、publication 和 protected-branch promotion 保留各自邊界。T1 文件不授權其他列的動作。

## 來源與審查

- [pstack architect](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/architect/SKILL.md)：使用例、介面草圖及結構方案。
- [設計 red flags](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/architect/references/design-red-flags.md)：責任分散、資訊洩漏及重複來源。
- [Hillclimb](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/poteto-mode/playbooks/hillclimb.md)：單假設、固定量測及改善方法；其 reset/autonomy 不照搬。
- [Harness graph](../../skills/delivery-harness/references/graph-orchestration.md)、[bounded enhancement](../../skills/delivery-harness/references/bounded-enhancement.md)：現有執行權威及累積修復預算。
- [Product agentic runtime](../../skills/product-definition-builder/references/agentic-runtime-selection.md)：產品自身 workflow/runtime 的責任。

前述只讀調查與 Astra 架構評估支持此分工。Sol reviewer 要求明確保留「未知效果先對帳」及「拒絕假設不清除工作」；本稿已納入。這些是 source/提案審查，沒有實作 diff、遠端執行或 release PASS。
