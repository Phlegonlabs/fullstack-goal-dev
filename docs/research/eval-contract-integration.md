# Eval rubric、pass rate 與交付包如何接入 Harness

研究日期：2026-10-03。狀態：提案，尚未成為正式 skill 合約。
研究 branch：`codex/eval-contract-research`。
基準：`bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61`，source Harness `0.58.0`。
本機安裝版為 `0.59.0`；session 啟動時載入的 digest 不可觀測。
本輪沒有執行產品 eval，也沒有交付可執行的 eval runner。

## 建議

把這套做法加入未來項目的三個既有位置：

1. **Product Definition 定義成功。** 在 PRD 寫清 rubric、樣本、分母、
   重跑方式、pass rate、關鍵失敗和交付物；對應必要 `TEST-*`。
2. **Delivery Harness 執行驗收。** 凍結具體 eval contract，執行項目自己的
   runner，再用 checker 重算結果；沿用現有 verifier、acceptance 和 exact-SHA gates。
3. **交付時留下重跑能力。** runner、測試資料、評分器、鎖定的依賴、
   結果證據和操作 runbook 一起交付。接手人從乾淨 checkout 能照文件重跑。

要寫死的是每個項目批准的驗收條件。`95%` 不是所有項目的統一預設值。
通過率的單位和算法也要先決定，不能交付時才挑最好看的數字。

## 現有機制與缺口

| 現有位置 | 已有能力 | 本次需要補的部分 |
| --- | --- | --- |
| [Product Definition SKILL](../../skills/product-definition-builder/SKILL.md) | 產品決策與 TEST obligations 由 Product Definition 擁有；Harness 擁有執行與證據 | 明確的 eval applicability、policy 與交付義務 |
| [PRD output contract](../../skills/product-definition-builder/references/output-contract.md)，AI evaluation / NFR / Test Obligations | AI gate 已要求代表性 eval set、thresholds、failure classes；TEST 有 stable ID 和 expected signal | 分母、rubric anchors、critical cases、repeats、grader 與樣本版本的結構化規則 |
| [Product package checker](../../skills/product-definition-builder/scripts/check_product_package.py) | 檢查 AI-EVALUATION trace、Must/NFR 對應必要 TEST、批准狀態 | 驗證 eval 欄位及引用的資料／rubric，而非只接受文字描述 |
| [Product approval digest](../../skills/product-definition-builder/scripts/contract_utils.py) | digest 涵蓋 PRD、architecture、stack 原文 | PRD 裏的一條路徑不會自動凍結該路徑的 bytes；需明確 hash 和檢查 |
| [Delivery acceptance](../../skills/delivery-harness/references/delivery-acceptance-contract.md) | 預先凍結情境；每個必要 TEST／assertion 都須 pass；核對 committed evidence 與 candidate | eval 樣本級評分、rate 計算和跨類別門檻須由 eval checker 執行 |
| [PLAN template](../../skills/delivery-harness/assets/templates/HARNESS_PLAN.template.md) 與 [verifier runtime](../../skills/delivery-harness/scripts/verifier_runtime.py) | 額外 frozen source、always-run gate、exit code、execution evidence、exact HEAD guards | 把 eval runner／checker 接成現有 verifier，檢查必要 gate 不可漏掉 |
| [MISSION_RUNBOOK](../../skills/delivery-harness/assets/templates/MISSION_RUNBOOK.template.md) | managed RUN 狀態模板 | 另外交付產品 eval 操作文件；狀態模板不能代替它 |

定位依據：output contract 第 224–229、283、829 行；Product checker 第
1880、1924、2328、2667 行；approval digest 第 86 行；acceptance checker
第 341、353、390、418 行。以上是研究基準版本的行號。

四語 README 的 delivery-acceptance 說明一致：必要測試不可跳過，過期 build、
mock 替代 real auth 或把 blocker 延後，都不能算 PASS。

## 哪些項目需要這套規則

每個新項目都做一次 applicability 判定，記在現有產品文件：

- **一般軟件：** 沿用 deterministic unit／integration／E2E。把既有測試和
  重跑文件交付即可；不要求另買 eval 平台或用 LLM 評分。
- **AI 輸出或 agent 行為影響產品結果：** 要有 rubric、代表性資料集、
  重複試驗規則、不可發生的結果和可重跑 harness。
- **涉及工具操作的 agent：** 驗證實際資料／副作用，例如是否真的建立預約、
  是否跨租戶讀取資料。最終回答聲稱成功不足以證明成功。

用現有 AI gate 判定適用性，非 AI 項目可記有理由的 not applicable。
這是新項目的提案，不自動改寫舊批准、舊 PLAN/RUN 或歷史結果。

## 在 Product Definition 階段凍結什麼

| 合約項目 | 要回答的問題 |
| --- | --- |
| 業務結果與 TEST trace | 哪個 `PRD-*`／`NFR-*` 要由哪個必要 `TEST-*` 證明？ |
| Rubric | 每個維度怎樣評分？每個分數有什麼可判斷的例子？單題何時算 pass？ |
| 樣本 manifest | 固定哪些 case ID、類別、語言、邊界題和 critical 題？資料來自哪裏？ |
| 門檻 | 總 rate、各類別最低 rate、critical fail 規則分別是什麼？ |
| 分母與 repeats | rate 按 case 還是 trial？跑幾次？全部成功、平均或其他哪個批准算法？ |
| Grader | deterministic assertions、人工或 model judge？judge rubric／prompt／版本如何校準？ |
| 執行邊界 | 測哪個 platform、auth、environment、build/config？哪些外部依賴是真實的？結果的有效時間窗？ |
| 預算與停止 | timeout、呼叫／費用上限、重試和修復次數？何時回報 blocked？ |
| 交付與維護 | 誰接手？重跑指令、依賴、證據路徑、資料權限、失敗排查和更新觸發點？ |

PRD 放批准的規則與 stable IDs。architecture 放 runner、grader、隔離及
資料流責任；stack decisions 的既有 Evaluation/output-validation row 放工具選擇。
完整 Chinese review copies 按既有 bilingual contract 同步。

建議給一個必要 TEST 驗證 eval policy，再給一個必要 TEST 驗證重跑交付包。
具體編號沿用目標項目的 ID inventory，不在本研究 invent 正式 requirement ID。

**批准時不要求 runner 已經寫好。** 先批准成功條件、樣本／rubric 和交付義務；
runner 在實作階段完成。Product checker 驗證已存在的批准輸入，未完成的交付物
由後續 TEST 管理，不把不存在的 runner hash 當成已凍結證據。

## 如何接到現有 acceptance

維持 `delivery-acceptance/1` 和 `delivery-results/1` 的語義：所有必要情境與
assertion 都要 PASS。不要讓登入、權限或 native coverage 被平均分數掩蓋。

把 eval 樣本放在項目的 eval contract／report；把品質驗收放在既有 acceptance
的一個必要 scenario。它的 assertions 包括：

- `eval-inputs-match`：rubric、case manifest、grader/config 與批准輸入一致。
- `eval-complete`：每個固定 case 的每個預定 trial 均有唯一且有效的結果。
- `eval-rate`：重算的總 pass rate 達到批准門檻。
- `eval-slices`：每個必要類別達標，樣本量符合批准要求。
- `eval-critical`：沒有任何 critical fail 或禁止結果。
- `eval-handoff`：runner、依賴、資料、runbook 可用，乾淨 checkout 重跑成功。

以上 assertions 必須全部 pass。若合約批准 100 題中至少 95 題合格，
5 題 noncritical 品質失敗可以保留在 eval report；它們不是被隱藏的必要
TEST failure。必要 TEST 的成功條件正是「完整試驗達到 95/100 並且其他條件全過」。
關鍵功能的每一條必要 TEST 仍須通過。

| 方案 | 判斷 |
| --- | --- |
| 直接給 delivery-acceptance v2 加通用 pass_policy，允許必要 scenario 失敗 | 不採用。會改動既有 all-required-pass 規則，也混淆功能驗收與品質抽樣 |
| 保留 delivery schema；獨立 eval contract/report＋小型 checker，輸出上述 assertions | 建議。現有 verifier 執行 checker；同一 acceptance register 接證據 |
| 另外建立 scheduler、agent framework 或 eval 狀態資料庫 | 不需要。PLAN sources、verifier evidence 和 RUN 已能承接 |

兩個 explorer 提供了前兩種方案。父 agent 選擇第二種，原因是保留現有
功能驗收與歷史 schema，同時能機器重算 rate。新增的是評分輸入／報告格式，
不是第二個批准來源、排程器或 RUN schema。

## Pass rate 的具體規則

以下只是示例 policy，數值尚未批准：100 個 case、每題 3 個 trial，
單題的 3 次結果全部達到 rubric 才算 case pass；總 case pass rate ≥ 95%，
每個批准 slice ≥ 90%，critical 題及禁止結果檢查每次都須通過。

```text
expected_trials = frozen_case_count * frozen_trials_per_case
case_pass = every planned trial satisfies the frozen case rubric
pass_rate = passing_cases / frozen_case_count
PASS = complete_and_valid_execution
       AND exact_input_and_candidate_identity
       AND pass_rate >= frozen_threshold
       AND every_required_slice_passes
       AND zero_critical_failures
       AND reproducible_handoff
```

runner 對完整執行輸出結構化結果；checker 自行重算，不相信 report 裏寫的
`PASS` 或百分比。品質 fail 保留在分母。missing、skipped、timeout、grader error、
duplicate 或 invalid 結果使本次驗收不能 PASS；不能刪掉這些題後重新算。
如果允許重試，事前寫清次數、替代規則並保留原始失敗；未知副作用先 read back。

使用整數比較，避免四捨五入把 94.95% 變成 95% 通過。切片允許重疊時也要
事先定義，不把切片的分母相加當作總樣本數。空 dataset／空必要 slice 不可通過。

| 示範結果 | 品質 gate 判斷 |
| --- | --- |
| 95/100 case 合格；300 trials 完整；slices、critical 與其他 assertions 全過 | PASS |
| 96/100；其中一題 critical 失敗 | FAIL |
| 總 rate 96%；一個必要語言 slice 只有 85% | FAIL |
| 95 題合格、5 題 timeout，刪掉 timeout 後報 100% | FAIL：執行不完整 |
| 100 題、每題三次，只挑各題最好的一次 | FAIL：不符合批准的 repeats 算法 |
| 190 次成功／200 次 trial，但應有 300 次 | FAIL：不能把實際跑過的數量改成分母 |
| runner exit 0，但 report 的 hashes 或候選版本不同 | FAIL |
| 用不同 judge 重評後達標，沿用舊批准和舊 PASS | FAIL：輸入／評分 policy 已變 |

這裏的 case-all-trials rate 是樣本內的觀測值，不是未來每次使用都成功的保證。
是否增加樣本數、信賴區間門檻或多批次要求，由項目的風險與產品合約決定。
探索用 capability suite 和阻擋交付的 acceptance／regression suite 分開標示。

## 未來項目要留下的檔案

下列是建議路徑，採用時列入該項目的 DOCUMENTS、write scope 和 Git policy：

```text
docs/product/PRD.md + PRD.zh-TW.md       # 批准的規則和 TEST obligations
docs/verification/eval-contract.json    # 從 PRD 派生、執行前凍結的 policy
evals/cases.jsonl                       # case IDs、split、slice、critical 標記
evals/rubric.json                       # 評分 anchors、單題規則、禁止結果
evals/runner.* + evals/graders/*         # 項目工具鏈中的實作，不預設特定語言
<existing lockfile>                     # 可重建的依賴
docs/verification/EVAL_RUNBOOK.md        # 給接手人的操作文件
docs/verification/delivery-results.json # 既有 acceptance register
docs/verification/evidence/eval/*       # 被 register 列出、hash 綁定的報告／證據
```

開發題可以用來 debug；held-out 驗收題和答案不提供給受測系統的 prompt、
retrieval index 或 tuning。runner 當然需要讀取驗收 fixtures，但它們不應洩漏
給被評估的 agent。資料 split、來源、使用權限與是否曾用於開發要可追溯。
私人資料不因「要交付 harness」而自動進 Git；記錄受控取得方式和版本，
用可分享的 synthetic／redacted fixtures 驗證交付能力。不可取得的必要資料仍是 gap。

**eval-contract 的最低內容**：對應 TEST、PRD digest、dataset/rubric digests、
唯一 case manifest、各 slice／critical 集合、分數轉 pass 規則、分母、重複算法、
門檻、適用 build/config、grader 設定、有效時間窗、預算／timeout、失敗／重試規則、交付清單。
受測 model 和 model judge 是不同 identity，兩者都要記；provider 只提供 alias 時
記實際觀測值、日期和不可鎖定的限制，不虛構 snapshot。

**eval report 的最低內容**：candidate/build/config、contract/dataset/rubric/
grader 身分、指令／runner 版本、時間與 environment、每個 case/trial 的狀態／
分數／assertion／失敗原因、工具結果、成本／耗時和證據 hash。
彙總數值要能由這些 row 重算，不能只交一張 dashboard 截圖。

PRD 可引用 dataset／rubric 的 digest；派生 eval contract 再綁 PRD digest。
PRD 不反過來存 eval contract digest，避免互相 hash 的循環。
runner 和 grader 的最終 bytes 綁到受測 candidate/config，實作修正後需重跑。

## 接到 candidate 與交付的順序

1. Product Definition 批准 rubric、門檻、資料和 TEST。Harness 凍結具體
   eval contract 與上游資料；managed 用 PLAN sources，direct 用任務記錄。
2. 實作 runner、graders、fixtures、runbook 和驗證器。合約先有，結果後產生。
   model judge 以人工標註樣本校準；能 deterministic 判斷的條件用程式檢查。
3. 在產品 candidate **H1** 執行完整驗收。事前設好 register／evidence 路徑的
   `-text -filter` attributes，保留 byte-identical evidence。
4. parent 把 register 和被列出的 redacted eval evidence 一起做 evidence-only
   commit 得 **H2**。必要 per-case 報告放既有 evidence root；不能另存到未受
   現有 acceptance 規則允許的結果路徑後假稱 H1/H2 等價。
5. 在乾淨 H2 上跑 exact-head review、eval checker、delivery acceptance 與
   其他 final gates。受測 product bytes 是 H1；H2 的合法差異由既有 checker 證明。
   RUN 保存 verifier execution key，register 指向 report；不把所有 eval rows 複製入 RUN。
6. 修正產品、runner 或 grader 後形成新 candidate，舊 gate 失效。
   H2 之後的 managed repair 遵守既有 formal PLAN revision／authorization 規則；
   不能憑「再跑一次」跳過它或重寫舊結果。
7. local-only closeout、archive、publication 和 promotion 保持既有分開授權。
   若驗收目標是 hosted build，核對實際部署 SHA／artifact/config，不能只用 local SHA。
   production 驗證按另行批准的安全子集執行，activation／商業成效另行證明。

H1/H2 的 Git 等價不能證明 live model、外部資料或 hosted config 一直未變。
對這些可變依賴，gate 還要檢查批准的有效時間窗及當前 readback；漂移後重跑。
改 judge 後不能只重評原答案就聲稱新版產品已驗收；依批准 policy 重跑完整試驗。

eval checker 可沿用現有 always-run verifier node；graph 顯式把它放在 acceptance／
closeout 之前。`exit 0` 加有效 report 才能滿足該 gate，不能只看其中一項。
沒有 eval gate 的 applicable 新計畫要在 readiness 被拒絕，而不是靠作者記得加。
現有 legacy PLAN validator 尚未自動強制 acceptance gate，這是實作要補的缺口。

## Runbook 至少要回答什麼

| 接手問題 | 必須留下的內容 |
| --- | --- |
| 如何從零開始？ | 支援環境、依賴／版本、乾淨 checkout 的安裝和 fixture setup 指令 |
| 跑哪個指令？ | 項目自己的 quick-check 與 full-acceptance 指令；quick-check 不能冒充完整 gate |
| 要哪些權限？ | environment 變數名稱、test account／資料取得方式、費用上限；只交 placeholders |
| 怎樣知道結果有效？ | 正確 target/build/config、contract hashes、預期 trials、exit code、report 路徑 |
| 失敗如何排查？ | 品質、critical、infra、grader、資料／版本漂移的分別；如何重播單題及查 redacted trace |
| 如何收尾？ | 僅本輪 fixture 的 owned IDs、setup／cleanup 權限與 readback；不自動清掉未知資料 |
| 何時重跑？ | code、prompt、model、tools、retrieval、rubric、judge 或資料變動後；依現有合約換 candidate |
| 如何更新門檻？ | acceptance 改動回 Product Definition；新批准／新版本／新結果，保留舊歷史 |

handoff TEST 由接手者或隔離的乾淨環境照 runbook 安裝並執行完整指令，驗證報告
可重算且符合 policy。model eval 的「可重跑」不等於每次輸出逐 byte 相同。
對外呼叫、付費 judge、帳號建立和 production 副作用仍需對應的現有 action authority。

## 對 Harness bundle 的最小實作次序

本輪只研究；下面是建議的下一輪 atomic outcomes，不是已建立的 PLAN：

| 步驟 | 主要受影響 source | 完成條件 |
| --- | --- | --- |
| 1. Product contract | Product Definition SKILL、interview/output contracts、package checker/tests | applicable 判定與完整 eval policy；缺分母／rubric／critical 規則不能批准 |
| 2. Eval verification | 新的窄範圍 eval contract/report templates、checker/tests；既有 acceptance reference | 自行重算；缺題、重複、換 judge、threshold 邊界與 critical fail 都被拒絕；不放寬 delivery/1 |
| 3. Harness wiring | PLAN template、readiness validator、verification references/tests | applicable 新計畫必有 frozen sources 與必要 verifier；stale SHA 和 gate omission 失敗；RUN schema 不另加 eval rows |
| 4. Handoff | 獨立 EVAL_RUNBOOK template、delivery handoff TEST 與 fixtures | 在目標項目工具鏈上由乾淨 checkout 重跑；register/evidence bytes 與 Git attributes 正確 |
| 5. Release adoption | 四語 README、VERSION/package、Epic、正式 installer | 完整 required suites 和獨立 review；另行授權的 publication／promotion／tag／installation |

第一個 adopter 用既有項目測試工具實作小型 runner／checker，驗證這個 contract
足夠描述實際工作，再把共用的資料／評分檢查收斂入 bundle。首輪不指定 eval SaaS。
新強制規則須有版本邊界；legacy pins 保留原規則，已批准項目只在明確的下一輪 scope
採用。增加正式規則時四語 README 一起改，本研究不改 published behavior 或版本。

implementation 最少需要 regression cases：空樣本、唯一 IDs、slice 分母、
threshold 上下邊界、critical override、缺／重複／額外 trials、nonzero/timeout、
假的 summary、換 rubric／judge／config、stale candidate、未凍結 contract、
漏掉 required gate、evidence path／hash／Git attributes 和乾淨環境重跑。

## 開放決定與版本差異

未來每個項目需在 Product Definition 決定實際百分比、單題 scoring anchors、
trial 算法、必要 slices／樣本量、grader、資料權限和費用。這些不能由本次研究替 owner 批准。

實作前要先選定真正目標 source／release。此 worktree 的 `0.58.0` 和 installed
`0.59.0` 不相同；已觀察到 installed template 新增 `ui-design/3`／`design-system/4`
及 ordinary dual-branch flow。source repo 明確保留 main-only Git Flow 作本地選擇。
本研究不移植新 UI／branch 規則，也不把 disk digest 當成 session loaded digest。
semantic audit：相同 shared rules 保留；新 design contract 差異需下一輪以對應 source
核對；main-only 是現有 source-specific policy，不是研究授權改動的內容。
沒有 fetched／live remote HEAD 或 release activation 證據。

## 外部研究依據

[OpenAI Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
建議先定義目標、資料和評分，再持續評估，並以人工回饋校準自動評分。
查閱日期：2026-10-03。上述 contract 與 gate 欄位是本研究的接入提案。

[Anthropic Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
區分 task、trial、grader 與真實 outcome，也區分至少成功一次和每次都成功的可靠度。
因此本提案要求先凍結 repeats 算法，並保留工具終態與失敗。
發布日期：2026-01-09；查閱日期：2026-10-03。

研究分工、檢查與未完成義務見
[EPIC-eval-contract-research](../epics/EPIC-eval-contract-research.md)。
