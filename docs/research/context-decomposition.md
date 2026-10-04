# Context 內容拆分研究

狀態：提案，尚未修改技能的實際載入規則。來源：`codex/harness-flow-modernization`，`fbda025839cfef8a9bbfb51be2911b0c09c62acb`。

先拆 Product Definition 的大型契約，再分開 UI 方向探索與 HiFi 審查，接著把 Harness 的 writer、parent 與 closeout 規則分開。Activation 按實際平台載入完整 profile。檔案變小只有配合階段與角色路由，才會减少 context。

## 量測方法

量測 104 份 Markdown：七個 SKILL、94 份 references、AGENTS 與兩個任務模板。使用原始 UTF-8 bytes，保留換行。父標題包含子段落，不能重複相加。這是來源體積，不是實際 host token 或耗時。

七個 SKILL 共 157,305 bytes；94 份 references 共 1,367,389 bytes。庫存總量不代表每次都讀取整個庫。最大的避免費用来自提前讀後續階段、其他平台與 parent 的協調內容。

## Product Definition

原始 [output-contract.md](../../skills/product-definition-builder/references/output-contract.md) 有 105,112 bytes，可先分成七個連續部分：

| 原文行號 | 建議內容 | bytes | 觸發 |
| --- | --- | ---: | --- |
| 1–69 | 共用入口與權威 | 8,761 | 每次 Product invocation |
| 70–341 | PRD 契約 | 28,240 | 撰寫／審查 PRD |
| 342–479 | Research artifacts | 6,538 | 實際研究任務 |
| 480–574 | Activation seed／Outcome Review | 10,124 | 對應任務；兩者不能混為同一觸發 |
| 575–694 | Architecture | 11,647 | 架構與 Release Targets |
| 695–886 | Stack Checkpoint | 19,591 | 技術選型 |
| 887–1008 | Approval／handoff | 20,211 | 完整性、批准與交接；Implementation Plan 仍須明確要求 |

外部七份預覽已逐位元重組原文，SHA-256 為 `69be65b1aa450efe0ba2a893f39fc93dae0a7336cc24ccbb2f0277291496f815`。Repository 保留這份提案，不另追蹤七份重複全文。預覽不是 installed skill，原有 full-read 規則仍有效。

Product [SKILL](../../skills/product-definition-builder/SKILL.md) 的 `24–48,92–105` 可合成 discovery 階段；`49–87,132–166` 可合成 drafting／approval 階段。入口保留決策沿用、行動邊界、必讀依賴、停止條件與階段表。

[interview-guide.md](../../skills/product-definition-builder/references/interview-guide.md) 的 `1–75,152–201` 保留共同訪談與適用 mode；`76–151` routing table 在 coverage／gap reconciliation 載入。Enhancement 仍須全文閱讀既有權威 package。

[architecture-playbook.md](../../skills/product-definition-builder/references/architecture-playbook.md) 的 `1–76,205–218` 保留共同規則；`77–204` 平台範例按實際 archetype 載入。多平台產品讀全部實際 surface，包含 companion web、backend 與 native distribution。

Release Targets 的格式以 architecture 契約為權威。訪談保留問題，SKILL 保留觸發，checklist 保留 assertion，其他長重述改成精確指向。批准階段仍匯合全部適用要求。

## UI 與 Design System

| 來源 | 建議內容邊界 | 執行者 |
| --- | --- | --- |
| UI SKILL `44–56`、UI pass `34–79`、output `72–204` | intake／方向探索 | frontend author，owner 選擇／混合／修改 |
| output `27–59,64–71` | reviewer shell／token specimens | HiFi 組裝者及 reviewer |
| output `205–266`、UI pass `121–151` | HiFi motion、證據、自查與 review | author 自查後，由獨立 reviewer 審查 |
| output `267–301`、UI pass `152–178` | Visual Approval／Need Gate | owner 與 parent |

來源：[UI output contract](../../skills/ui-design-builder/references/output-contract.md)、[UI pass](../../skills/ui-design-builder/references/ui-design-pass.md)。沿用現有 `HIFI_REVIEWER.template.html`、`REVIEWER_SHARED.css` 與 composition patterns。模板承擔長 HTML/CSS；reference 保留必要結構、資料、限制與驗證。

三個可實測方向、完整 frontend-design、完整適用產品與設計來源、PRD-to-HiFi coverage、自查、獨立 review、owner Visual Approval、所有必要尺寸與中間寬度證據均保留。歷史批准與 legacy Wireframe 保持原語意。

Design System SKILL 與 output contract 合計 30,097 bytes，大多同屬一個 compile 階段，暫不再切碎。重複 digest 說明改成一份權威和短指向；保留完整 Markdown／JSON／HTML、components、tokens、色彩、尺寸、狀態、motion、來源身份與 pair checks。

## Harness 與角色

[execution-state-model.md](../../skills/delivery-harness/references/execution-state-model.md) 分成權威與授權、planning／graph、recovery、capability／dispatch、lock／handoff 等內容邊界。Parent 只在執行相應操作時載入後者；worker packet 保留自己適用的權限與限制。

[verification-gates.md](../../skills/delivery-harness/references/verification-gates.md) 按 `1–137` gate／E2E、`138–216` selection／reuse、`217–313` UI／UX、`314–352` evidence／worker result、`353–370` security、`371–411` failure／closeout 拆分。Failure 規則 writer 也要讀；完整 E2E 由負責該驗證的角色讀。

| 角色 | 必需內容 |
| --- | --- |
| Product researcher | 問題、範圍、適用來源、研究结果契約 |
| Product drafter | discovery 結果、目前產物契約、適用 guides、完整必要產品來源 |
| Frontend author | 任務 packet、必要設計來源、完整 frontend-design、適用 style／motion、UI checks |
| Backend author | 任務 packet、受影響要求與接口、架構／資料／安全限制、focused＋negative checks |
| Integration owner | 接口、mission 結果、全部 actual changed paths、整合差異與跨任務驗證 |
| Frontend／backend reviewer | exact SHA、適用完整變更、契約與證據、未解 findings；writer 不審自己的工作 |
| Security reviewer | 完整實際變更範圍、必要 diff／依賴、威脅邊界、required checks、fresh exact-SHA evidence |
| Activation operator | 固定 release identity、ACTIVATION 全文、action contract、適用完整 profiles、action grants、live readback |
| Release owner | exact candidate、完整 release matrix、分支契約、發布／安裝授權與身份 |

初始 UI-bearing delivery 的整體 UI gate 不能因 backend packet 較小而消失。Host 的工具、模型、fallback、instruction discovery 與 precedence 由有效 host policy 決定，通用 references 不複製本機模型清單。

Worker 不重建 parent 完整 PLAN/RUN 或 dispatch 歷史。Parent 從既有資料 render 任務 packet，包含 checkout、scope、接口、授權、驗證、atomic commit 與結果契約。同一 mission 的小任務沿用一位 writer；獨立 mission 使用 sibling 與隔離 checkout。`fork_turns:none` 只省略聊天繼承，不代表 AGENTS 或工具說明不再注入。

## Activation、SEO 與工具輸出

Activation 保留共同 closed profile IDs、完整 surface inventory、overlay 觸發與責任分離，之後讀每個適用平台的完整 profile。Web 要包含 `profile-catalog.md:19–67` 的 Feature Overlays，加上 `1–18,177–195` 共同規則。帶 backend／agent／native companion 的產品再讀相應分支。不能因沒讀到某個 profile 就把它當成不適用。

完整 activation contract、現有 ACTIVATION、外部行動授權、live readback、blocked／deferred 和 closeout 不變。不能只產文件就宣告外部設定完成。

SEO 將來源與 baseline／traffic-drop／saved lifecycle 分開。使用 Ads、Keyword Planner、第三方來源或 saved lifecycle 時補讀對應完整分支。Source identity、時間、metric、權限與connector boundary 保留。

Review packet 現在取得整份 `base..head` 再截到預設 50,000 bytes，scope 沒有參與 diff 選擇。非 security review 可聚焦 surface 與整合接縫，但保留全量 name-status、unexpected paths、base/head、mission SHA 和 findings。只有可證明已審且未變的其他內容才能引用外置；不能盲目 scope-filter。Security 保持完整覆蓋。

超出 packet 預算時分段讀完整 artifact，記錄還沒讀到的部分。截斷不是 review 完成。Test log、probe、document-sync、validation 留完整 artifact，向對話回傳 bounded summary；失敗按 finding 補讀。先改善顯示，不順手更改 RUN fingerprints、schema 或 proof。

## 可重現的來源縮減估算

After 使用以下完整列出的行區間，各檔內重疊行只計一次。新增入口及 conditional dependencies 尚未計入，所以不是實際 runtime 節省。

| 路線／來源集合 | before bytes | after bytes | 少讀 |
| --- | ---: | ---: | ---: |
| Product discovery：SKILL、output、interview、architecture playbook | 223,407 | 60,696 | 72.8% |
| Product draft／approval：SKILL、output、architecture playbook | 196,486 | 145,734 | 25.8% |
| UI direction：SKILL、output、UI pass | 99,144 | 60,912 | 38.6% |
| 非 UI writer：verification reference | 56,559 | 22,057 | 61.0% |
| UI writer：verification reference | 56,559 | 37,636 | 33.5% |
| Web Activation：profile catalog，含 feature overlays | 22,432 | 10,103 | 55.0% |
| baseline SEO：source catalog、review method | 21,133 | 16,542 | 21.7% |

精確 after 行區間：

- Product discovery：SKILL `1–48,88–131`；output `1–69`；interview `1–75,152–201`；architecture playbook `1–76,205–218`。
- Product draft／approval：SKILL `1–21,49–166`；output `1–341,575–890,941–1008`；architecture playbook `1–89,205–218`。
- UI direction：SKILL `1–98`；output `1–26,72–220`；UI pass `1–120`。
- 非 UI writer：verification `1–99,138–201,314–352,371–385`；UI writer 再加 `217–313`。
- Web Activation：profile catalog `1–67,177–195`。
- baseline SEO：source catalog `1–57,66–80,87–119`；review method `1–117`。

百分比不能相加。未计入 host instructions/tools、聊天、AGENTS、產品文件、code、pixels、packet 與 domain guides。Research、付費、AI、安全、額外平台、Outcome、optional plan 或 HiFi review 觸發後加回相應內容。批准者本來需要較多交叉核對，節省較小是合理的。

## 實作與驗證拆解

| Atomic task | Write ownership | 必要驗證 |
| --- | --- | --- |
| CTX-01 | Product partition／entry | coverage、links、full-read dependencies、Product／cross-skill contracts |
| CTX-02 | Product interview／architecture routing | new／enhancement、多平台、native distribution、gap negatives |
| CTX-03 | frontend：UI stage refs／templates | full frontend-design、directions、coverage、motion、required browser checks |
| CTX-04 | runtime：role／verification refs、existing-field packet | authorization、scope、join、graph、golden path |
| CTX-05 | Activation profiles | 多 surface、overlays、missing profile、external actions、closeout |
| CTX-06 | runtime：review packet／compact output | unexpected paths、rename／delete、merge、truncation、exact SHA、security no-exclusion |
| CTX-07 | SEO routing／dedupe | baseline、traffic-drop、saved lifecycle、missing source |

每個 task 含自己的文檔與測試，使用獨立 atomic commit。CTX-01/02 及 CTX-04/06 各自順序執行；接口固定後 UI 與 Activation 可在不同 checkout 並行。Parent 逐個整合。

正式實作同步各 SKILL Reference Routing、受影響 full-read 條文、四語 README、workflow、Epic、skill-contract／cross-skill／golden tests。移動模板時保留一份權威，不靠刪除 assertion 讓測試綠。AGENTS 深度搬移暫緩，不能要求 host 忽略有效治理。

Document-sync 仍每次 invocation 檢查。Same-session reuse 要 bytes 未變、全文仍在 context 且適用規則／階段相同；compaction 只剩摘要則重讀必需源。Hash 相同不證明閱讀，也不授予 action。

## 研究結果與剩餘工作

兩個獨立 code explorers 分別研究產品／設計與 runtime／治理，使用 FlashX／max，沒有完整聊天繼承。104 份來源 hash 無漂移，七份預覽重組與本地報告連結通過。研究沒有修改技能，因此沒有重跑產品完整套件；研究結果不是 final implementation 或 security PASS。

原有 frontend correction、fresh independent review、最終 candidate matrix、remote protection 與正式 release 維持待辦。明確要求的工作分支安裝是 development 安裝，不會把上述待辦改成完成，也不把 0.59 candidate 轉為 formal release。
