# Architecture 選型參考：模組化單體、BFF、Web-Queue-Worker、事件驅動、微服務、Serverless 部署拓撲

狀態：Reference only · 核對日期 2026-09-25。本文件提供可評估的架構選項與取捨，不是部署指令、基礎設施採購授權或自動採納規則。任何選項要先落到既有 PRD、Architecture、Runtime、Deployment 與 Integration 文件，才成為專案決策。參考不代表安裝、建立雲端資源或改變 skill 流程。

## 適用範圍與 PRD 提問

架構要回答的不是「哪個名稱較流行」，而是實際旅程如何跨畫面、客戶端、API、權限、資料、外部服務與失敗恢復運作。

沿用既有 reference baseline `architecture.md` 中對應 PRD 的追問，仍需按實際需求覆核：核心旅程是什麼？有哪些角色與租戶？延遲、可用性與資料地區要求為何？哪些工作是長任務？團隊能否維運分散式系統？服務與部署單位的責任人是谁？失敗、重試、部分完成與資料一致性由誰處理？

## 主要比對矩陣

| 選項 | 適合 | 避免/重訪條件 | 架構與整合義務 | 營運與成本面 | 遷移與鎖定 |
| --- | --- | --- | --- | --- | --- |
| 模組化單體 | 單一團隊、產品仍在驗證、領域邊界可先以程式碼模組表達 | 若模組開始互相讀取內部資料表、共享隱藏狀態，或不同領域有衝突發布節奏，應重新審視邊界 | 定義 module ownership、public interface、資料存取邊界、事件邊界與測試邊界；避免以資料夾名稱冒充架構 | 發布、觀測、交易與除錯較簡單；主要成本是持續守住邊界 | 通常最低；拆出服務前應保留模組契約與資料所有權 |
| BFF | 多種客戶端、畫面資料形狀差異大、前端團隊需要貼近其體驗的 API 層 | 若所有介面請求相近、只有一個客戶端，或團隊無法維護多個 API 層，BFF 可能只是重複成本 | 依前端劃定 BFF 責任；共用監控、授權、限流與路由；BFF 不應重造領域規則 | 增加 API 層、部署單位與版本協調；可換取客戶端簡化與故障隔離 | BFF 契約會與前端耦合；共用服務仍需穩定介面 |
| Web-Queue-Worker | 相對清楚的核心領域，但有報表、匯入、通知等長任務 | 若佇列只是把所有同步操作包一層，或 worker 與 web 共用隱藏 schema 而失去解耦，應重審 | web 前端與 worker 透過訊息解耦；記錄佇列語意、重試、死信、冪等、逾時、outbox 與任務狀態查詢 | web 與 worker 可獨立伸縮；需付佇列、觀測、 poison message 與一致性處理成本 | 訊息格式與狀態查詢 API 會形成邊界；佇列服務可替換但語意需保留 |
| 事件驅動 | 多個消費者對同一業務事實反應、近即時整合、解耦外部系統 | 若團隊沒有非同步除錯能力，或流程需要強同步回應，先用 request/response；若事件只是遠端程序呼叫的另一種寫法，重訪設計 | 定義事件、schema 版本、producer/consumer 契約、至少一次、亂序、idempotency、死信、補償與可觀測性；避免事件夾帶過多敏感資料 | 解耦帶來伸縮與新消費者擴充；也帶來最終一致性、時序、重放、測試與故障追蹤成本 | 事件 schema 與 broker 語意是核心契約；消費者獨立演進必須有版本策略 |
| 微服務 | 複雜領域、明確自治邊界、不同服務有獨立伸縮或發布需求 | 若沒有成熟 DevOps、資料一致性與分散式觀測能力，或只是為了「技術先進」，不應啟動 | 每個服務有 bounded context、資料所有權、API/event 契約、部署與回滾策略；閘道、服務發現、追蹤與治理要一起設計 | 獨立部署與伸縮是優點；也增加網路故障、版本協調、基礎設施與跨服務測試成本 | 服務契約、資料副本與平台工具會形成多點耦合；拆分應由可驗證邊界驅動 |
| Serverless 部署拓撲 | 事件觸發、突發負載、低狀態 worker、需要快速最小化維運的部署單位 | 若長連線、極低延遲、長任務、硬體控制或可預測高利用率是核心要求，應先做 workload spike；不應把 serverless 誤當成免維運 | 記錄冷啟動、逾時、併發、狀態存放、佇列整合、身分、網路出口與部署回滾 | 可按使用量與事件規模調整；但觀測、併發限制、跨服務除錯與供應商功能差異會轉成營運成本 | 平台觸發器、身分與限制會耦合；核心邏輯應與部署單位分離 |

部署拓撲與服務分解不互斥。同一產品可以是「模組化單體＋serverless worker」、「微服務＋佇列」，或「BFF＋事件驅動整合」。選擇應依旅程與失敗模型組合，不應因標籤互斥而錯配。

BFF 是依客戶端劃分 API 責任的模式；full-stack 描述應用如何組合 frontend/server 能力。後者的框架選擇見下表，BFF 的單一客戶端重訪條件只適用於 BFF 層。

## 完整應用技術棧候選（2026-10-02 增補）

下表是選型假設，不是固定 starter 或已驗證部署。Cloudflare／Vercel 是部署平台，React 是 UI library，TanStack Start／Next.js／React Router 是應用框架；Supabase／Convex 是後端與資料服務。先選服務邊界，再把需要的層組成可驗證方案。既有可用技術仍是候選。

| 組合與官方入口 | 適合的需求 | 必須另外決定 | 主要取捨／採納前驗證 |
| --- | --- | --- | --- |
| [TanStack Start](https://tanstack.com/start/latest)＋React＋Workers 或 Node host＋所選資料服務 | 型別化路由、SSR、server functions、互動型 Web App | auth、資料庫、jobs、元件、樣式與部署目標 | Start 查核時為 RC；用代表性 SSR、session、mutation、快取與錯誤路由驗證選定 adapter，不能假設全生態同成熟度 |
| [Next.js](https://nextjs.org/docs)＋[Vercel](https://vercel.com/docs/frameworks/nextjs)＋[Supabase](https://supabase.com/docs) | React 全端產品、公開 SEO 與登入後應用混合 | auth/session 邊界、RLS、背景工作、資料與部署地區 | 託管整合方便，但框架、託管與資料服務各有升級、費用及退出責任；可替換部署或資料層 |
| [React Router framework mode](https://reactrouter.com/start/framework/installation)＋Node host＋PostgreSQL | 用 loader/action 組織全端 React、保留服務與 SQL 控制權 | auth、ORM／migration、jobs、觀測與服務維運 | Framework/Data/Declarative mode 分開選；驗證 SSR、表單、session 與目標 host |
| [Astro](https://docs.astro.build/en/concepts/islands/)＋CMS／內容來源＋需要時的 API | 品牌、文件、內容與少量會員／互動島；編輯與前端分開發布 | 草稿／預覽／發布、搜尋、動態表單與 auth；有交易時另選 commerce 邊界 | CMS 不持有即時價格／訂單權威；靜態內容與互動島各有資料邊界；大量應用狀態時重訪 |
| [Nuxt](https://nuxt.com/docs/4.x/guide/concepts/rendering) 或 [SvelteKit](https://svelte.dev/docs/kit/introduction)＋所選 host＋PostgreSQL | Vue 或 Svelte 團隊的 SSR／混合渲染應用 | UI foundation、session、server/data 邊界與 jobs | 各自核對 adapter、元件生態和部署限制；不是 React 元件的直接替代 |
| React＋[Convex](https://docs.convex.dev/quickstarts)＋所選前端 host | 協作、即時更新、TypeScript 後端整合 | auth、權限、函式邊界、排程與資料退出 | 先驗證訂閱、租戶隔離、費用及匯出；不能把服務語意當作通用 SQL |
| React＋[FastAPI](https://fastapi.tiangolo.com/features/)＋PostgreSQL＋queue/worker | Python 資料處理、AI／科學工作、明確 API 邊界 | 契約生成、auth、worker、部署與觀測 | 前後端分開發布與維運；測試 API 版本、重试、取消和 job 狀態 |
| [Rails](https://rubyonrails.org/)／[Django](https://docs.djangoproject.com/en/stable/intro/overview/)／[Laravel](https://laravel.com/docs)＋其原生資料／工作工具 | 業務交易、管理後台；可用 server-driven HTML，如 Django templates＋[htmx](https://htmx.org/docs/)＋PostgreSQL | 完整頁／fragment、session／CSRF、部署與背景工作；或另選獨立 frontend | 依語言、團隊與原生 ORM 選一條路線；驗證部分更新與快取；不要假設一般伺服器框架能直接放入 Workers |
| React／PWA 或已選 App＋client SQLite＋[PowerSync 類同步服務](https://docs.powersync.com/intro/powersync-overview)＋相容主資料庫／API | 離線編輯、跨裝置同步與立即本機回應 | local schema、download scope、upload API、衝突、撤權、附件及各端 SDK | 本機成功不代表伺服器已接受；驗證離線重連與拒絕寫入；只需讀快取時避免增加同步層 |
| React＋Vite＋[Hono](https://hono.dev/docs/guides/rpc)＋PostgreSQL＋所選 auth／jobs | 多端共用業務 API、前後端可分開發布 | REST/OpenAPI 或 TypeScript RPC、輸入驗證、session／token、DB driver、worker 與 host | 型別共享不取代 runtime validation；只有驗證兩個指定目標後才能主張可攜；小型單端 app 不必為此拆服務 |

每個比較方案都要補齊實際適用的 frontend、backend、資料、auth、API、jobs、部署、測試、成本與維護責任，再交現有 Stack Decision Checkpoint。表內組合的產品適配是研究判斷，官方連結只支持各元件定位。TanStack 模組分工見 [Frontend](frontend.md)，Cloudflare 資源組合見 [Cloudflare platform](cloudflare-platform.md)。

## 按需求延伸的架構能力（2026-10-02）

以下六項補充既有組合；租戶隔離與 durable workflow 可套用多種棧，不是新的前端框架。適用、避免、責任和測試是研究判斷。每項官方來源只支持附近的功能定位，沒有替此組合做部署、成本、授權或效能驗證。

### Server-driven HTML 與局部互動

- 適用／避免：表單、後台和伺服器持有主要狀態的交易流程；離線 editor、canvas 或大量持續 client state 先比較其他路線。
- 分層責任：frontend 用語意 HTML 與局部更新；backend 產生頁面／fragment 並驗證操作；SQL transaction、session／CSRF 和授權由 server 負責。真正耗時工作才加 queue/worker；部署 server app 與 assets。
- 最小驗證／退出成本：直接導航、無效表單、重複提交、session 過期、back/forward、fragment 後焦點、完整頁與 fragment 快取分隔；承諾無 JavaScript fallback 時另驗證普通 links/forms。轉換渲染模式需重寫 templates／fragment 邊界，domain service 可保留。
- 來源事實：[htmx](https://htmx.org/docs/) 從 HTML 元素發送請求並通常以 HTML response 更新 DOM。它是互動工具，不自動提供 backend、auth、可及性或離線同步；見 [Frontend](frontend.md)。

### Local-first／離線編輯與同步

- 適用／避免：斷網仍需編輯與跨裝置使用；讀快取已足夠時不加完整同步。庫存、付款等 server-controlled 決定不能由離線 UI 承諾完成。
- 分層責任：frontend 顯示 pending／rejected／conflict；client SQLite、主 DB、附件與同步 metadata 分開。backend upload API 重驗授權與業務約束；auth 控制下載範圍、切帳號、登出／撤權後本機資料；jobs 處理 upload retry／reconciliation。部署 API、sync service 和相容 DB，核對 browser/native SDK 與持久化限制。
- 最小驗證／退出成本：兩端斷網修改、反序重連、重複 upload、撤權後拒絕、schema 升級、刪除傳播及附件失敗。本機 schema、ID、衝突政策、下載分區與全量 resync 都有遷移成本。
- 來源事實：[PowerSync](https://docs.powersync.com/intro/powersync-overview) 提供 in-app SQLite、sync service、按使用者分配資料及 client SDK。這是同步候選；單獨使用 TanStack DB 或 SQLite 不證明上述義務完成。見 [Data](data-storage.md)、[Auth](authentication-and-identity.md) 與 [Frontend](frontend.md)。

### Durable business workflow

- 適用／避免：審批、provisioning 或履約需要外部 callback、timer 與跨重啟恢復；一個冪等 job＋DB 狀態已足夠時沿用 Web-Queue-Worker。
- 分層責任：frontend 顯示進度、等待、取消和人工恢復；API 驗證 workflow 啟動與後續 command；business DB、執行 history、大 payload 分開。worker 執行副作用，engine 保存編排狀態；部署 API、worker 和 engine/service，記錄版本過渡。
- 最小驗證／退出成本：外部副作用已成功但未記錄就 crash、callback 重複、逾時、activity 中取消，以及新部署恢復舊 execution。history 與 workflow definitions 不保證跨 engine 可攜；先定 drain／版本相容／遷移方案。
- 來源事實：[Temporal](https://docs.temporal.io/workflow-execution) 用 event history／replay 恢復 execution；外部 API 副作用仍需冪等或補償，不由 replay 推定 exactly-once。見 [Integrations](integrations.md)、[Deployment](deployment.md) 與既有 [durable runtime 比較](ai-agentic.md)。

### 多租戶資料與部署隔離

- 適用／避免：租戶獨立 restore、資料地區、負載隔離或合約分隔影響架構；只有 org／role 不代表每租戶都需獨立 DB。
- 分層責任：frontend 傳遞 tenant context，但 backend 解析可信 tenant 身分並逐次驗證 membership／role。資料可選 tenant-keyed 共用表、獨立 DB 或有理由的 hybrid；cache／search／files／jobs 都保留租戶邊界。部署記錄 shared／isolated 資源、routing、migration 和責任人。
- 最小驗證／退出成本：跨租戶 API／cache／files／search／job 拒絕、tenant restore、onboarding 失敗、offboarding 和 noisy neighbor。租戶抽離、ID、routing、schema 版本、備份與營運自動化都需遷移計畫。
- 來源事實：[Microsoft 多租戶儲存指南](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data) 比較共享、獨立和混合儲存及其 restore／migration 成本。其一般取捨可參考，Azure 實作不能直接移植。見 [Data](data-storage.md)、[Auth](authentication-and-identity.md)、[Operations](operations.md)。

### Headless 內容與條件式 commerce

- 適用／避免：編輯獨立發布、多通路共用內容，或有理由自訂 storefront；內容檔案或託管店面已足夠時不加 headless 服務。
- 分層責任：frontend 呈現已發布內容與授權 preview；CMS 持有內容，commerce 服務在需要時持有價格／庫存／cart／order／checkout。穩定 ID 串接兩者；editor、preview、customer、operator auth 分開。jobs 處理 invalidation／index 和驗證後的商務 events；前端與 CMS/API 各有部署與 credentials。
- 最小驗證／退出成本：草稿外洩、preview 權限、下架／失效、內容斷鏈、結帳前價格改變、放棄 checkout、重複／亂序 order events。content models、rich text、assets、redirect、customer identity 與 order/payment records 都有退出成本。
- 來源事實：[Payload Live Preview](https://payloadcms.com/docs/live-preview/overview) 用 iframe 與 messages 連接 frontend preview；[Shopify cart/checkout](https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/cart/manage) 提供 cart 操作與 checkout handoff。兩者只是代表性入口，不是已驗證搭配；商務需求仍交 Product Definition 既有 monetization／partner gates。見 [Integrations](integrations.md)。

### 多端共用的獨立 typed API

- 適用／避免：Web、App、desktop 或 partner clients 共用業務 API 與不同發布節奏；不要只為「可攜」拆開一個簡單單端 app。
- 分層責任：frontend 保留渲染與本機 state；API 持有 runtime input validation、授權與 domain operations，DB 存取留在其後。browser session 與 native token 各選策略；jobs 保留 worker interface；frontend/API 按需求分開部署，平台 bindings 明確記錄。
- 最小驗證／退出成本：舊 client 對新 API、不可信輸入、跨租戶拒絕、cookie/token、contract generation、driver/adapter；主張可攜時在兩個指定 host 跑同一代表性 slice。shared types、public schema、平台 bindings、auth callbacks 與 worker 整合仍需遷移。
- 來源事實：[Hono RPC](https://hono.dev/docs/guides/rpc) 從 server type 和 validator 推導 TypeScript client input/output。公開或跨語言 API 另比較 [REST/OpenAPI 與 RPC](api.md)；型別共享不自動成為語言中立的 API 契約。

## 來源事實與研究判斷

來源事實：Azure Architecture Center 將 Web-Queue-Worker 描述為 web 前端、message queue 與後端 worker 的組合，前端處理請求，worker 處理耗時或批次工作，兩者可獨立伸縮，並提醒元件可能長成大型單體。微服務則由自治服務組成，每個服務有明確業務能力與資料自主性，但帶來服務發現、資料一致性與分散式管理複雜度。見 [Architecture styles](https://learn.microsoft.com/en-gb/azure/architecture/guide/architecture-styles/) 與 [Web-Queue-Worker](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/web-queue-worker)。

來源事實：事件驅動架構由 producer、consumer 與 event channel 組成，可使用 pub/sub 或 event stream；Azure 文件提醒 eventual consistency、處理順序、idempotency、錯誤處理與事件 schema 演進。見 [Event-driven architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven)。BFF 是針對特定前端建立後端層，避免所有介面競爭同一通用後端；Azure 也提醒若介面請求相近或只有一個介面，可能不適合。見 [Backends for Frontends](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)。

研究推論與待驗證：模組化單體與 serverless 部署拓撲的完整官方原文未收錄，因此其細節屬於研究層級整理。採納前需以專案實際 Runtime、Deployment 與供應商文件驗證。CQRS 可作為讀寫分離的方法參考，見 [CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)，但只在讀寫負載、安全或資料形狀確實分歧時考慮。

## 三個條件式情境示例

1. 若新產品由單一團隊開發，核心域尚在驗證，但已有 CSV 匯入與報表，可組合模組化單體＋Web-Queue-Worker：核心 API 保持同步，匯入與通知走佇列 worker；先守住模組邊界，不預先拆服務。
2. 若同一業務要支援 Web、行動 App 與外部儀表板，而各端畫面資料形狀差異明顯，可評估針對各前端的小型 BFF，共用領域服務與授權；若各端只是呼叫相同 API，就不要為了模式而增加一層。
3. 若訂單完成會觸發出貨、通知、帳務與分析，且各下游處理速度不同，可評估事件驅動整合；前提是接受最終一致性、至少一次與補償流程，並先建立事件 schema 版本與死信處理。

## 失敗與核對清單

- 旅程：一條核心旅程是否畫出客戶端、API、權限、資料、外部服務與失敗恢復？
- 邊界：模組、服務、BFF、worker 或 serverless 函式的所有權、資料存取與介面是否明確？
- 非同步：佇列與事件是否定義重試、亂序、死信、冪等、補償與查詢進度？
- 一致性：同步回應、最終一致讀取、跨服務補償與遷移期間的過渡狀態是否可測？
- 觀測：跨 web、worker、佇列、事件與外部呼叫是否可追蹤同一請求或任務？
- 恢復：部分失敗、重複處理、下游逾時、部署回滾與資料回補責任是否清楚？
- 相容性：Runtime、訊息工具、serverless 觸發器、身分、網路、SDK 與資料遷移是否逐項核對？

## 採納記錄與文件映射

採納時更新既有 PRD、Architecture、Runtime、Deployment、Integration 與驗收文件，記錄：部署單位、服務或模組邊界、資料所有權、佇列/事件語意、失敗恢復、伸縮假設、替代方案與重訪條件。這是研究記錄，不新增審批關卡，也不授權建立或安裝基礎設施。
