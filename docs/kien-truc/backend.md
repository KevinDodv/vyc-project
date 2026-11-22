# Kiến trúc backend Django

Phạm vi: thư mục `backend/` của monorepo. Căn cứ: [thiet-ke-chi-tiet.md](../thiet-ke-chi-tiet.md) mục 2 (vai trò), 3–4 (dữ liệu), 9 (API), 10 (BR), 11 (phi chức năng); quyết định #666, #671 (theo phản biện #657). Phần Docker, Caddy, CI, sao lưu nằm ở [van-hanh.md](van-hanh.md); phần Astro và SEO ở `frontend-seo.md`.

Mục 9 cuối tài liệu liệt kê các chỗ backend **bổ sung hoặc lệch** so với thiết kế chi tiết, để sếp duyệt một chỗ.

## 0. Phiên bản và thư viện

| Thành phần | Chọn | Ghi chú |
| --- | --- | --- |
| Python | 3.13 | Khớp image `python:3.13-slim` ở van-hanh.md |
| Django | 5.2 LTS | Hỗ trợ tới 4/2028, phủ hết GĐ1–3 |
| API | django-ninja 1.x | Không dùng DRF (#671 b) |
| DB driver | psycopg 3 (`psycopg[binary]`) | |
| Hash mật khẩu | argon2-cffi | `Argon2PasswordHasher` đứng đầu `PASSWORD_HASHERS` (mục 11) |
| Ảnh | Pillow ≥ 11.3 | Có sẵn AVIF và WebP |
| Chạy prod | gunicorn | 3 worker sync (van-hanh.md) |
| Dev | pytest, pytest-django, ruff, mypy, django-stubs, import-linter | Quản lý bằng uv |
| Markdown công khai | markdown, nh3 | Render và làm sạch `story_md`, `usage_md`, `site_page.body_md` cho DTO công khai (mục 8) |

Không thêm: Redis, Celery, DRF, factory_boy, django-environ. Lý do ở từng mục bên dưới.

## 1. Cấu trúc thư mục và app

### 1.1 Cây thư mục

```
backend/
  pyproject.toml        # phụ thuộc, cấu hình ruff, mypy, pytest, import-linter
  uv.lock
  .python-version       # 3.13
  manage.py
  conftest.py           # fixture chung: owner, workshop, client đã đăng nhập
  openapi/
    v1.json             # sinh từ api_v1, commit vào repo
    public.json         # sinh từ api_public, commit vào repo
  config/
    settings.py         # một file, đọc biến môi trường
    urls.py             # /api/v1/, /api/public/, /api/health
    api.py              # tạo api_v1, api_public, gắn router và exception handler
    wsgi.py
  core/                 # hạ tầng dùng chung, không có nghiệp vụ
    models.py           # TimeStampedModel (abstract), AuditLog, Setting, CodeCounter, ThrottleHit
    errors.py           # ApiError, BusinessError, mã lỗi chung
    handlers.py         # exception handler cho Ninja
    audit.py            # record(), snapshot()
    codes.py            # next_no(), format_code() theo BR-20
    clientip.py         # ClientIPMiddleware
    throttle.py         # hit() + decorator throttle
    pagination.py       # Page[T], paginate()
    roles.py            # Role (TextChoices), Actor (Protocol)
    permissions.py      # RoleAuth, OWNER_ONLY, ANY_STAFF, pick_out()
    images.py           # sinh AVIF/WebP lúc upload
    markdown.py         # render_public_markdown(): markdown + nh3, nơi duy nhất render Markdown (mục 8)
    schemas.py          # SafeHttpUrl, SafeMediaPath, ImageRef, BuyLink (mục 8)
    timeutil.py         # today_vn(), period_yymmdd() ...
    logging.py          # formatter JSON, gửi 5xx về webhook
    migrations/
    tests/
  accounts/
    models.py           # User (bảng app_user); role dùng core.roles.Role
    services.py         # login (khoá 15 phút), logout, tạo tài khoản
    api.py              # /auth/*, /users
    management/commands/create_owner.py
    migrations/  tests/
  catalog/              # PH1 Danh mục
    models/             # area.py, goods.py, supplier.py, product.py, recipe.py ...
    services/           # products.py, suppliers.py, prices.py, recipes.py ...
    api/                # products.py, suppliers.py ... ; api/schemas/<nhóm>.py
    migrations/  tests/
  operations/           # PH4 Nhập/xuất + PH2 Sản xuất, truy xuất
    models/             # receiving.py, production.py, labels.py, sales.py, scent.py
    services/           # cùng cách chia, thêm trace.py, inventory.py, reports.py
    api/                # cùng cách chia ; api/schemas/<nhóm>.py
    migrations/  tests/
  website/              # PH3: nội dung web và API công khai
    models.py           # SitePage
    services.py         # dựng DTO công khai, ghi lượt quét qua operations
    api/                # pages.py (/api/v1/site-pages), public.py (/api/public/*)
    migrations/  tests/
```

App không nằm trong package cha (`backend/catalog`, không phải `backend/apps/catalog`): đường import ngắn, import-linter khai báo thẳng tên app. Một app nhỏ (core, accounts, website) dùng file `models.py`, `services.py`; app lớn (catalog, operations) dùng package `models/`, `services/`, `api/` chia theo nhóm màn hình.

Không dùng `django.contrib.admin`: trang quản lý là Astro (#671 a). Vẫn dùng `contrib.auth` (hasher, session auth), `contrib.contenttypes`, `contrib.sessions`.

### 1.2 App nào sở hữu bảng nào

Tên bảng giữ đúng mục 4 bằng `Meta.db_table`. "Sở hữu" nghĩa là model khai báo trong app đó và chỉ service của app đó được ghi.

| App | Phân hệ | Bảng (mục 4) |
| --- | --- | --- |
| core | hạ tầng | audit_log, setting, code_counter; thêm throttle_hit (kỹ thuật, mục 5.2). Không có bảng cho vai, nhưng enum `Role` và Protocol `Actor` nằm ở `core/roles.py` (mục 4.3) |
| accounts | xác thực | app_user (cùng django_session của Django) |
| catalog | PH1 | area, goods_type, material, grade, price, supplier, plot, farm_log, customer, product, slug_redirect, certificate, ingredient, recipe, recipe_item |
| operations | PH4 + PH2 | receipt, material_lot, ingredient_receipt, ingredient_lot, production_order, production_ingredient, product_lot, retained_sample, scent_trial, scent_trial_sample, scent_trial_reading, scent_trial_score, label_roll, serial, scan_event, buyer, issue, issue_line |
| website | PH3 | site_page |

Lý do một số chỗ không hiển nhiên:

- **ingredient, recipe, recipe_item ở catalog**: là danh mục OWNER quản lý (mục 2 "Công thức, danh mục phụ liệu"). Lô và phiếu phụ liệu là chứng từ kho nên ở operations.
- **slug_redirect ở catalog**: service đổi slug của product ghi bảng này trong cùng giao dịch (mục 8.1). website chỉ đọc.
- **scan_event ở operations**: báo cáo `GET /reports/scans` (OWNER) nằm ở operations, nếu bảng ở website thì operations phải import ngược lên. website ghi lượt quét bằng cách gọi `operations.services.labels.record_public_scan()`.
- **Gộp PH2 và PH4 vào operations** (#671 c): các FK vòng `material_lot → production_order / issue_line`, `ingredient_lot → production_order` (mục 4, dòng cuối DDL) nằm gọn trong một app. Django tự tách bước thêm FK trong migration, không cần viết tay.
- **audit_log ở core trỏ tới app_user**: FK khai báo bằng chuỗi `settings.AUTH_USER_MODEL`, không import Python từ accounts. Code trong core gõ kiểu người dùng bằng `core.roles.Actor` và dùng `core.roles.Role`, nên contract import-linter ở mục 1.3 xanh. Migration của core phụ thuộc migration đầu của accounts; accounts không có FK về core nên không có vòng.

### 1.3 Luật phụ thuộc một chiều

```
core  ←  accounts  ←  catalog  ←  operations  ←  website
```

App bên phải được import app bên trái, không có chiều ngược lại. `config` được import mọi app.

Trong mỗi app, lớp đi một chiều `api → services → models` (mục 2). `api` của app A được gọi `services` của app B ở bên trái; không gọi `api` của app khác.

Kiểm tự động bằng **import-linter**, khai báo trong `pyproject.toml`, chạy ở CI cùng ruff:

```toml
[tool.importlinter]
root_packages = ["config", "core", "accounts", "catalog", "operations", "website"]

[[tool.importlinter.contracts]]
name = "App phụ thuộc một chiều"
type = "layers"
layers = ["website", "operations", "catalog", "accounts", "core"]

[[tool.importlinter.contracts]]
name = "Trong app: api -> services -> models"
type = "layers"
containers = ["core", "accounts", "catalog", "operations", "website"]
layers = ["(api)", "(services)", "(models)"]
```

Dấu ngoặc đánh dấu lớp tuỳ chọn (core không có `api`). Bên trong operations không đặt luật giữa các nhóm (receiving, production, labels, sales): chúng là một phân hệ, chia file cho dễ đọc.

## 2. Lớp xử lý: api → services → models

| Lớp | Làm | Không làm |
| --- | --- | --- |
| `api` (router Ninja + schema) | Nhận request, khai vai bằng `auth=` (mục 4.3), gọi một hàm service, chọn schema output theo vai | Không chứa BR, không gọi ORM ghi, không mở transaction |
| `services` | Mọi BR của mục 10, mở `transaction.atomic`, khoá hàng, sinh mã, ghi audit_log | Không biết tới `request`, schema Ninja hay HTTP |
| `models` | Cột, ràng buộc DB (CHECK, UNIQUE, index của mục 4), property tính toán thuần | Không gọi service, không ghi bảng khác trong `save()` |

Quy tắc cho service:

- Hàm module, tham số keyword-only, nhận `actor: User` thay vì `request`. Không dùng class service hay signals.
- **Mọi hàm ghi** có `@transaction.atomic` và gọi `audit.record(...)` trước khi trả (mục 9, BR-19). Không bật `ATOMIC_REQUESTS`: giao dịch phải nằm ở service để test service chạy đúng như qua API.
- BR vi phạm thì `raise BusinessError(...)`; cảnh báo không chặn (BR-04, BR-09, BR-27 c) trả trong kết quả, không raise.
- Không xoá cứng (BR-19, mục 1 quy ước): service không gọi `.delete()` trên bảng nghiệp vụ. Ngoại lệ có trong mục 9: xoá dòng `production_ingredient` và bỏ lô quế khỏi lệnh khi lệnh còn DRAFT, vẫn ghi audit_log với `after = null`.

Ví dụ hình dạng một service (BR-07, BR-08):

```python
@transaction.atomic
def add_material_lot(*, order_id: int, lot_code: str, actor: User) -> MaterialLot:
    order = ProductionOrder.objects.select_for_update().get(pk=order_id)
    if order.status != OrderStatus.DRAFT:
        raise BusinessError("ORDER_NOT_DRAFT", f"Lệnh {order.code} đã bắt đầu ủ, không thêm lô được", rule="BR-27")
    lot = MaterialLot.objects.select_for_update().get(code=lot_code)
    before = audit.snapshot(lot)
    if lot.stream != Stream.CONTROLLED:
        raise BusinessError("LOT_GENERAL_STREAM", "Lô hàng chung, chỉ dùng xuất bán quế khô", rule="BR-08")
    # ... kiểm IN_STOCK, đổi RESERVED, gắn production_order
    audit.record(actor, lot, "UPDATE", before=before)
    return lot
```

Chữ ký `core.audit`:

```python
def snapshot(obj: models.Model, fields: Iterable[str] | None = None) -> dict[str, Any]: ...
def record(actor: Actor, obj: models.Model, action: AuditAction, *,
           before: dict[str, Any] | None = None, reason: str | None = None) -> AuditLog: ...
```

`record` tự lấy `after = snapshot(obj)` (trừ khi action là xoá dòng), `entity = obj._meta.db_table`, `entity_id = obj.pk`. JSON hoá Decimal thành chuỗi, date/datetime thành ISO 8601.

## 3. API

### 3.1 Hai NinjaAPI

| | `api_v1` | `api_public` |
| --- | --- | --- |
| Đường dẫn | `/api/v1/` | `/api/public/` |
| Xác thực | cookie phiên qua `RoleAuth`; mặc định `auth=OWNER_ONLY` cho mọi route, route mở cho xưởng khai `ANY_STAFF` (mục 4.3) | không |
| Phương thức | GET, POST, PATCH, PUT, DELETE | **chỉ GET** |
| Output | schema theo vai (mục 4.3) | DTO công khai theo BR-17, mục 8.4 |
| Giới hạn tần suất | không | có, mục 5.2 |
| OpenAPI | `openapi/v1.json` | `openapi/public.json` |

Ngoài hai API trên chỉ có `GET /api/health` (view Django thường, không auth, không throttle): trả `{"status": "ok"}` sau khi chạy `SELECT 1`. van-hanh.md dùng cho healthcheck và smoke test.

Router chia theo nhóm ở bảng mục 9: `catalog/api/products.py` có `router = Router(tags=["Danh mục"])`, `config/api.py` gắn vào `api_v1.add_router("/products", ...)`. Tên path, query, body theo đúng mục 9; trường JSON viết snake_case, giống tên cột.

Quy ước output chung:

- Tiền là số nguyên VND; số cân, gram là **chuỗi** thập phân (`"120.50"`) để không mất chính xác của `numeric` (mục 1 quy ước). Frontend định dạng lại khi hiển thị.
- Thời điểm trả ISO 8601 có múi giờ UTC; ngày (`date`) trả `YYYY-MM-DD`, đã tính theo giờ VN ở server.
- Lệnh ghi có cảnh báo không chặn thì response có `warnings: [{code, message}]` (mục 9, dòng "Lệnh SX: phụ liệu"). Không có cảnh báo thì mảng rỗng.

### 3.2 Lỗi

Mọi lỗi, kể cả 401, 403, 404, 422 của Ninja, đều trả đúng dạng mục 9:

```json
{"code": "LOT_GENERAL_STREAM", "message": "Lô hàng chung, chỉ dùng xuất bán quế khô", "details": {"rule": "BR-08", "lot_code": "NL-2611-0045"}}
```

`core/errors.py`:

```python
class ApiError(Exception):
    status = 400
    def __init__(self, code: str, message: str, *, status: int | None = None, **details: Any) -> None: ...

class BusinessError(ApiError):          # vi phạm BR hoặc sai trạng thái
    status = 409
    def __init__(self, code: str, message: str, *, rule: str, status: int = 409, **details: Any) -> None: ...
```

- `code`: chữ hoa gạch dưới, nêu đúng việc sai (`CURE_NOT_READY`, `TRACE_TOO_DEEP`, `LOT_NOT_IN_STOCK`). Mã đã có trong mục 9 thì dùng nguyên.
- `details.rule`: mã BR (mục 10: "Mã BR dùng làm mã lỗi và tên test"). Frontend tìm lỗi theo `code`; người đọc log tìm theo `rule`.
- `message`: câu tiếng Việt xưởng đọc hiểu, có mã chứng từ cụ thể (mục 9).

Exception handler đăng ký ở `config/api.py` cho cả hai API (`core/handlers.py`):

| Exception | HTTP | `code` |
| --- | --- | --- |
| `ApiError`, `BusinessError` | theo `status` | theo `code` |
| `ninja.errors.ValidationError` | 400 (mục 9 dùng 400, không dùng 422) | `VALIDATION_ERROR`, `details.errors = [{field, message}]` |
| `ninja.errors.AuthenticationError` | 401 | `UNAUTHENTICATED` |
| `django.core.exceptions.PermissionDenied` | 403 | `FORBIDDEN` |
| CSRF sai | 403 | `CSRF_FAILED` |
| `Http404`, `ObjectDoesNotExist` | 404 | `NOT_FOUND` |
| `Throttled` (core.throttle) | 429 | `RATE_LIMITED` hoặc `LOGIN_LOCKED` |
| `ninja.errors.HttpError` (Ninja tự raise, vd 405) | theo `status_code` | `HTTP_<mã>`, message lấy từ exception |
| Exception khác | 500 | `INTERNAL_ERROR`, message chung, chi tiết chỉ vào log |

### 3.3 Phân trang

Tự viết mỏng (#666), không dùng `@paginate` mặc định vì nó trả `count` thay cho đủ thông tin trang:

```python
class Page(Schema, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

def paginate(qs: QuerySet[M], page: int = 1, page_size: int = 50) -> tuple[list[M], int]: ...
```

Query `?page=1&page_size=50`, `page_size` tối đa 200. Áp cho danh sách chứng từ và báo cáo. Danh sách nhỏ cố định (`/materials`, lưới nút `/suppliers?recent=12`) trả mảng thường.

### 3.4 OpenAPI → TypeScript

1. `uv run python manage.py export_openapi_schema --api config.api.api_v1 --output openapi/v1.json --indent 2` (lệnh có sẵn của Ninja), tương tự cho `api_public`.
2. Frontend chạy `openapi-typescript` trên hai file này để sinh kiểu (cách gọi và chỗ đặt file sinh: xem `frontend-seo.md`).
3. CI chạy lại bước 1 rồi `git add -N backend/openapi/ && git diff --exit-code backend/openapi/` (khớp van-hanh.md 9.1; `add -N` để file mới chưa track cũng bị tính là lệch): ai đổi schema mà quên sinh lại thì CI đỏ. Hai file JSON là contract giữa backend và frontend; review PR nhìn diff của chúng.

Trang docs Swagger chỉ bật khi `DEBUG=1` (`docs_url=None` ở prod).

## 4. Xác thực và phân quyền

### 4.1 Tài khoản và phiên

- Custom user `accounts.User(AbstractBaseUser)`, `db_table = "app_user"`, `AUTH_USER_MODEL = "accounts.User"`. Cột `password` map vào `password_hash`, `last_login` map vào `last_login_at` bằng `db_column` để giữ đúng tên mục 4. Không dùng `PermissionsMixin` (không có superuser hay group).
- `role`: `Role.OWNER | Role.WORKSHOP` (TextChoices + CHECK). PUBLIC là người không đăng nhập, không có bản ghi. `Role` khai ở `core/roles.py`, không ở accounts, để core dùng được mà không import ngược (mục 1.3); `accounts.User.role` dùng `choices=Role.choices`.
- Mật khẩu: argon2id (`Argon2PasswordHasher`), mục 11.
- Phiên: `django.contrib.sessions` lưu DB. `SESSION_COOKIE_AGE = 12 * 3600`, `HttpOnly`, `Secure` (prod), `SameSite=Lax` (mục 11). `SESSION_SAVE_EVERY_REQUEST = False` nên phiên hết hạn 12 giờ sau đăng nhập, không kéo dài theo thao tác.
- Đăng nhập sai 5 lần thì khoá 15 phút (mục 9). Chỉ lần **sai** mới được đếm, bằng `core.throttle` (mục 5.2), cộng các dòng 1 phút trong 15 phút gần nhất (cửa sổ trượt). Có hai khoá:
  - `login:u:<sha256(username viết thường, cắt 150 ký tự)>|<ip_hash>`: 5 lần sai / 15 phút thì khoá **cặp tài khoản + IP đó**. Người ngoài sai 5 lần từ IP của họ không khoá được OWNER đang ở xưởng.
  - `login:ip:<ip_hash>`: 20 lần sai / 15 phút với mọi username thì khoá IP đó. Chặn dò mật khẩu nhiều tài khoản từ một máy.
  - Khoá dùng băm nên username do client gửi dài bao nhiêu thì khoá cũng cố định độ dài; username dài quá 150 ký tự bị 400 trước khi đếm.
  - Đăng nhập đúng thì xoá dòng của khoá `login:u:` tương ứng. Khoá trả 429 `LOGIN_LOCKED` "Sai mật khẩu 5 lần, thử lại sau 15 phút". Không thêm cột vào app_user.
  - Khoá theo cặp tài khoản + IP là cách hiểu chặt hơn câu "khoá 15 phút sau 5 lần sai" của mục 9, ghi ở mục 9 tài liệu này để sếp duyệt.
- Tài khoản OWNER đầu tiên tạo bằng `manage.py create_owner --username ...` (mật khẩu nhập tay hoặc lấy từ biến môi trường lúc dựng). Không để mật khẩu trong migration seed.

Endpoint (mục 9): `GET /auth/csrf` (đặt cookie `csrftoken`, trả 204), `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` → `{id, username, full_name, role}`.

### 4.2 CSRF và ai gọi API ghi

- CSRF kiểm trong `RoleAuth` (mục 4.3, lớp con của `ninja.security.SessionAuth`): gọi `ninja.utils.check_csrf(request)` cho phương thức ghi, sai thì tự raise `ApiError("CSRF_FAILED", "Phiên làm việc đã cũ, tải lại trang rồi thử lại", status=403)`. Không để Ninja tự raise `HttpError(403, "CSRF check Failed")`, vì như vậy handler phải dò chữ trong message mới biết là lỗi CSRF. Khi dựng khung, kiểm lại hành vi CSRF thật của bản Ninja đang dùng bằng test `test_csrf_required_on_write`. Request ghi phải có cookie `csrftoken` và header `X-CSRFToken` cùng giá trị. `CSRF_COOKIE_HTTPONLY = False` để JS đọc được; `CSRF_TRUSTED_ORIGINS = [SITE_ORIGIN]`.
- `POST /auth/login` không có auth nên Ninja không tự kiểm; hàm gọi `ninja.utils.check_csrf(request)` ở đầu (chống login CSRF).
- **Contract với frontend:** mọi request ghi vào `/api/v1` đi thẳng từ trình duyệt, qua Caddy, cùng origin. Astro SSR chỉ gọi **GET** `/api/v1` (chuyển tiếp header `Cookie` của người dùng) và GET `/api/public`. Lý do: Django kiểm Origin/Referer với request HTTPS; request server-to-server từ Astro không có hai header đó nên sẽ bị chặn, và chuyển tiếp chúng là chỗ dễ sai.
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`: an toàn vì backend không mở cổng ra ngoài, chỉ Caddy và Astro gọi được (van-hanh.md).

### 4.3 Phân quyền theo vai (mục 2)

Kiểm ở API, không dựa vào việc ẩn nút (mục 2). **Mặc định từ chối:** `api_v1` khai `auth=OWNER_ONLY`, nên route nào quên khai vai thì chỉ OWNER vào được, không bao giờ mở nhầm cho WORKSHOP. Route mở cho xưởng phải khai rõ `auth=ANY_STAFF`.

```python
# core/roles.py
class Role(models.TextChoices):
    OWNER = "OWNER", "Chủ doanh nghiệp"
    WORKSHOP = "WORKSHOP", "Xưởng"

class Actor(Protocol):                 # core gõ kiểu người dùng qua Protocol, không import accounts
    pk: Any
    role: str
    is_authenticated: bool

# core/permissions.py
class RoleAuth(SessionAuth):
    def __init__(self, *roles: Role) -> None: ...
    def authenticate(self, request: HttpRequest, key: str | None) -> Actor | None: ...
    # chưa đăng nhập → None → 401; đăng nhập nhưng sai vai → raise PermissionDenied → 403

OWNER_ONLY = RoleAuth(Role.OWNER)
ANY_STAFF = RoleAuth(Role.OWNER, Role.WORKSHOP)
```

```python
@router.get("/material-lots", auth=ANY_STAFF, response=list[MaterialLotOwnerOut | MaterialLotOut])
@router.post("/production-orders", response=ProductionOrderOut)        # không khai → OWNER_ONLY
```

Test ma trận vai × route (`core/tests/test_role_matrix.py`): bảng `ROUTE_ROLES` trong test ghi vai được phép của từng route theo mục 2 và mục 9. Test duyệt mọi route của `api_v1` (lấy từ `api_v1.urls`), gọi bằng WORKSHOP và bằng người chưa đăng nhập, khẳng định 403/401 đúng bảng. Route có trong API mà không có trong bảng thì test đỏ, nên thêm route mới buộc phải khai vai.

Ngoài router, `core` gõ kiểu người dùng bằng `Actor` (hàm `audit.record`, `pick_out`); service ở catalog, operations, website dùng thẳng `accounts.models.User` vì các app đó được import accounts. Quyền phụ thuộc dữ liệu (BR-05: WORKSHOP chỉ sửa phiếu của mình trong ngày, giờ VN) kiểm trong **service**, vì đó là BR và có test BR-05; service raise `ApiError("RECEIPT_EDIT_FORBIDDEN", "Chỉ chủ doanh nghiệp được sửa phiếu ngày trước", status=403, rule="BR-05")` khớp AC-05.

**Ẩn giá với WORKSHOP.** Mỗi entity có trường giá có hai schema output; schema WORKSHOP là lớp cha, không có trường giá, schema OWNER kế thừa và thêm trường giá:

```python
class MaterialLotOut(Schema):            # WORKSHOP: không có unit_price, amount
    id: int; code: str; weight_kg: Decimal; grade_id: int; stream: str; status: str

class MaterialLotOwnerOut(MaterialLotOut):
    unit_price: int
    amount: int

def pick_out(actor: Actor, owner: type[S], workshop: type[S], obj: Any, *, own_draft: bool = False) -> S: ...
```

Endpoint khai `response=MaterialLotOwnerOut | MaterialLotOut` và trả `pick_out(...)`. Trường giá gồm: đơn giá, thành tiền, tổng tiền, giá vốn, input_cost, unit_cost, giá mua/bán của bảng giá trong báo cáo (mục 2).

Ngoại lệ "trừ chính phiếu người đó đang lập" (mục 2) được hiểu cụ thể: phiếu nhập hoặc phiếu xuất có `created_by = actor`, `status = SAVED`, ngày lập là hôm nay giờ VN, tức đúng khoảng WORKSHOP còn sửa được theo BR-05. Khi đó API dùng schema OWNER cho **phiếu đó** (`own_draft=True`); danh sách, báo cáo, tồn kho vẫn ẩn giá. `GET /prices` mở cho cả hai vai theo mục 9 vì form lập phiếu cần đơn giá mặc định (BR-04).

Test bắt buộc: với mỗi endpoint trả entity có trường giá, một test gọi bằng WORKSHOP và khẳng định JSON không có khoá giá nào (`test_ws_no_price_<nhóm>`).

## 5. IP thật của khách và giới hạn tần suất

### 5.1 Lấy IP

Hai nơi gọi Django: Caddy (request `/api/*` từ trình duyệt) và Astro SSR (lúc render trang). Caddy **ghi đè** `X-Forwarded-For` bằng IP kết nối tới nó (van-hanh.md, Caddyfile); Astro gửi tiếp nguyên giá trị `X-Forwarded-For` nhận từ Caddy khi gọi Django.

`core.clientip.ClientIPMiddleware` đặt `request.client_ip`:

1. `REMOTE_ADDR` thuộc một dải trong `TRUSTED_PROXY_CIDRS` → duyệt `X-Forwarded-For` **từ phải sang trái**, bỏ các IP thuộc `TRUSTED_PROXY_CIDRS`, lấy IP đầu tiên không thuộc dải. Với contract hiện tại (Caddy ghi đè, Astro gửi nguyên) header chỉ có một phần tử là IP khách; cách duyệt này vẫn đúng nếu Astro lỡ nối thêm IP của Caddy. Header trống, không có IP hợp lệ, hoặc mọi IP đều thuộc dải → `request.client_ip = None` (**không** lấy `REMOTE_ADDR`: đó là IP của container Astro/Caddy, dùng làm khoá thì mọi khách chung một khoá). Cách xử lý `None` ở mục 5.2.
2. Ngoài dải → bỏ qua header, dùng `REMOTE_ADDR`.

Kiểu: `request.client_ip: str | None`. Chỉ trường hợp 1 mới ra `None`; trường hợp 2 luôn có giá trị.

**Dải được tin:**

| Môi trường | `TRUSTED_PROXY_CIDRS` |
| --- | --- |
| staging, production | subnet cố định của mạng compose, khai ở `networks.default.ipam.config.subnet`. Giá trị đề xuất `172.28.0.0/24`, Lan3 chốt trong compose; Django đọc từ biến môi trường, không hard-code |
| dev (runserver + astro dev trên máy) | `127.0.0.1/32,::1/128` |

Biến trống thì không tin header nào (an toàn mặc định). Không tin cả dải private `10/8`, `172.16/12`, `192.168/16`: VPS có thể có mạng private khác của nhà cung cấp.

IP chỉ dùng trong bộ nhớ cho throttle và để băm. Không ghi IP gốc vào DB hay log (mục 11): `scan_event.ip_hash = sha256(ip + IP_HASH_SALT)`, `IP_HASH_SALT` là biến môi trường bí mật. Throttle cũng dùng bản băm làm khoá.

### 5.2 Giới hạn tần suất

Bảng kỹ thuật trong core, mỗi dòng là số lần trong một phút (`window_start` làm tròn xuống đầu phút):

```sql
CREATE TABLE throttle_hit (
  key text NOT NULL,                 -- 'pub:<ip_hash>', 'trace:<ip_hash>', 'login:u:<hash>|<ip_hash>', 'login:ip:<ip_hash>'
  window_start timestamptz NOT NULL,
  hits int NOT NULL,
  PRIMARY KEY (key, window_start)
);
```

```python
# core/throttle.py — đều chạy autocommit, ngoài giao dịch nghiệp vụ
def hit(key: str) -> None: ...                       # UPSERT +1 vào dòng của phút hiện tại
def count(key: str, minutes: int) -> int: ...        # SUM(hits) WHERE key = %s AND window_start > now() - minutes
def check(key: str, *, limit: int, minutes: int, code: str = "RATE_LIMITED") -> None: ...  # count() >= limit → raise Throttled
def reset(key: str) -> None: ...                     # xoá mọi dòng của key
```

- Giới hạn theo phút (`/api/public`): `check(key, limit=N, minutes=1)` rồi `hit(key)`. Cửa sổ 1 phút làm tròn đầu phút: lúc giáp ranh khách có thể gọi tối đa 2N trong 60 giây, chấp nhận được với mục đích chống lạm dụng.
- Khoá đăng nhập (mục 4.1): trước khi kiểm mật khẩu gọi `check(..., limit=5, minutes=15, code="LOGIN_LOCKED")` cho khoá `login:u:` và `check(..., limit=20, minutes=15, ...)` cho khoá `login:ip:`; sai mật khẩu thì `hit()` cả hai khoá. Cộng 15 dòng phút là cửa sổ trượt thật, không có lỗ giáp ranh như cửa sổ 15 phút cố định. Index khoá chính `(key, window_start)` phục vụ đủ câu SUM. Đăng nhập đi thẳng từ trình duyệt qua Caddy nên luôn có IP; nếu vẫn gặp `client_ip is None` thì chỉ kiểm khoá `login:u:<hash>|none`, bỏ khoá `login:ip:`, và ghi log `client_ip_missing` như dưới.

Vượt ngưỡng thì 429 kèm header `Retry-After`.

**Astro quên gửi `X-Forwarded-For` (`request.client_ip is None`, mục 5.1):** nếu lấy IP container làm khoá thì mọi khách chung một khoá và cả website dính 429. Vì vậy với `/api/public`, khi `client_ip is None` thì **bỏ qua throttle**, ghi log WARNING `client_ip_missing` (gộp, tối đa một dòng mỗi phút) và không băm IP vào scan_event (`ip_hash = null`). Chọn để hở thay vì chặn: mất giới hạn tần suất một lúc ít hại hơn website trả lỗi cho mọi khách và Googlebot (#648). Frontend có test kiểm Astro gửi header (frontend-seo.md G1), smoke test sau deploy kiểm thêm một lần. Lệnh `manage.py purge_throttle` xoá dòng cũ hơn 1 ngày; chạy bằng cron hằng đêm cùng lịch sao lưu (báo Lan3).

Ngưỡng:

| Endpoint | Ngưỡng mỗi IP |
| --- | --- |
| `GET /api/public/trace/{code}` | 60 lượt/phút (mục 9) |
| `GET /api/public/products*`, `/pages/*` | 300 lượt/phút |
| `POST /api/v1/auth/login` | 5 lần sai / 15 phút theo tài khoản + IP; 20 lần sai / 15 phút theo IP (mục 4.1, mục 9) |

Trang sản phẩm là SSR, mỗi lượt xem gọi `/api/public/products/{slug}` với IP của người xem. Googlebot và AdsBot có thể duyệt nhanh hơn 60 trang/phút từ một IP; 429 lúc đó thành trang lỗi và hại SEO, Google Ads (#648). Vì vậy ngưỡng 60 giữ cho trace (có ghi DB, là chỗ mục 9 ghi giới hạn), còn trang nội dung nới lên 300.

Không chọn: throttle bằng cache trong bộ nhớ (mỗi worker gunicorn đếm riêng, ngưỡng thật thành 3×); Redis (thêm một dịch vụ trên VPS 4 GB chỉ để đếm, ở quy mô 100 lượt quét/phút của mục 11); plugin rate-limit của Caddy (phải build Caddy riêng, van-hanh.md đã bỏ).

### 5.3 BR-18: lượt quét của người nội bộ

`GET /api/public/trace/{code}` không yêu cầu đăng nhập, nhưng `AuthenticationMiddleware` vẫn đọc cookie phiên nếu có. Astro gọi API này **phải chuyển tiếp header `Cookie`** của người mở `/q/<serial>`; `request.user.is_authenticated` thì không ghi scan_event và không tăng scan_count (BR-18, mục 8.4). Response trace luôn có `Cache-Control: no-store`.

## 6. PostgreSQL, migration và các điểm khoá dữ liệu

### 6.1 Model và migration

- PostgreSQL 16, `ENGINE = django.db.backends.postgresql`, `CONN_MAX_AGE = 60`, `USE_TZ = True`, `TIME_ZONE = "Asia/Ho_Chi_Minh"` (lưu UTC, "trong ngày" theo giờ VN: mục 1). Mọi so sánh "hôm nay" đi qua `core.timeutil.today_vn()`.
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"` (id bigint, mục 1).
- Mọi model nghiệp vụ kế thừa `core.models.TimeStampedModel` (`created_at`, `updated_at`, mục 4).
- Ánh xạ kiểu: `numeric(10,2)` → `DecimalField(max_digits=10, decimal_places=2)`; tiền → `BigIntegerField`; `jsonb` → `JSONField`; `text` → `TextField`; `varchar(70)` → `CharField(max_length=70)`.
- Enum: `TextChoices` + `CheckConstraint(condition=Q(status__in=...))` để DB cũng chặn (mục 4 "text + CHECK"). Các CHECK nhiều cột của mục 4 (vd `issue_line`, `ingredient_lot` một nguồn) viết thành `CheckConstraint`; "một phiên bản ACTIVE mỗi recipe.code" là `UniqueConstraint(fields=["code"], condition=Q(status="ACTIVE"))`. Index bắt buộc của mục 4 khai đủ trong `Meta.indexes`.
- DDL mục 4 là nguồn chuẩn: khi viết model, so `manage.py sqlmigrate <app> 0001` với mục 4 theo từng bảng.
- Migration có phiên bản, commit cùng code; CI chạy `makemigrations --check --dry-run`. Không sửa migration đã vào `main`, chỉ thêm migration mới. Deploy chạy `migrate` tự động ở entrypoint (mục 11, van-hanh.md).
- Seed danh mục cố định của mục 4 (material, grade, area 1 tỉnh + 9 xã, ingredient, recipe/recipe_item theo sổ tay) là **data migration** trong catalog, có hàm ngược `noop`. Tài khoản OWNER không seed (mục 4.1).

### 6.2 Khoá hàng: `SELECT … FOR UPDATE`

| Chỗ | Khoá gì | Căn cứ |
| --- | --- | --- |
| Đưa lô quế vào lệnh, bỏ ra; xuất quế khô | dòng `production_order` rồi các dòng `material_lot` | BR-07, BR-08 |
| Thêm, sửa, xoá dòng `production_ingredient` | dòng `production_order` rồi dòng `ingredient_lot` | BR-07, BR-27 a |
| Bắt đầu ủ, hoàn thành, huỷ lệnh | dòng `production_order` | BR-09, BR-28 |
| Gán đoạn tem | các dòng `serial` trong đoạn (`roll_id`, `seq BETWEEN`), rồi dòng `product_lot` | BR-12 |
| Xuất, huỷ phiếu xuất thành phẩm | các dòng `serial` đã quét | BR-06, BR-13 |
| Huỷ, sửa phiếu nhập | dòng `receipt` rồi các `material_lot` của nó | BR-05 |

`select_for_update()` đi kèm `select_related()` qua FK cho phép NULL (vd `material_lot.production_order`, `serial.issue`) sinh LEFT JOIN, và Postgres báo lỗi "FOR UPDATE cannot be applied to the nullable side of an outer join". Quy tắc: luôn viết `select_for_update(of=("self",))` khi có `select_related`. Như vậy cũng chỉ khoá đúng bảng cần khoá, không khoá lan sang bảng cha.

Quy tắc chống deadlock: luôn khoá **chứng từ cha trước, dòng con sau**; nhiều dòng cùng loại thì `order_by("id")` (serial theo `seq`). Gán 1.000 tem (mục 11, < 2 giây) làm bằng một câu khoá cả đoạn và một câu `UPDATE … WHERE id IN (...)`, không lặp từng serial.

Có test chạy hai luồng song song (`@pytest.mark.django_db(transaction=True)`, hai thread) cho BR-07: hai máy quét cùng đưa một lô quế vào hai lệnh, đúng một lệnh thành công; hai lần múc cùng lô phụ liệu không làm `remaining_g` âm.

### 6.3 Bộ đếm mã nghiệp vụ (BR-20)

Một câu UPSERT, khoá hàng `code_counter (prefix, period)` tới khi giao dịch nghiệp vụ commit; giao dịch rollback thì số cũng trả lại, không thủng số. Không dùng `MAX()+1` (BR-20).

```python
def next_no(prefix: str, period: str) -> int:
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO code_counter (prefix, period, last_no, created_at, updated_at)
               VALUES (%s, %s, 1, now(), now())
               ON CONFLICT (prefix, period)
               DO UPDATE SET last_no = code_counter.last_no + 1, updated_at = now()
               RETURNING last_no""",
            [prefix, period],
        )
        return cur.fetchone()[0]
```

Phải gọi bên trong `transaction.atomic` của service (hàm assert `connection.in_atomic_block`). `core.codes` có một hàm dựng mã cho mỗi mẫu của bảng BR-20, ví dụ `receipt_code(d: date) -> str` trả `PN-261120-001`; số NN vượt 99 tự thành 3 chữ số (BR-20 ghi chú). Kỳ đếm (`period`) tính theo ngày giờ VN.

Serial (BR-16) không dùng bộ đếm: 10 ký tự Crockford Base32 từ `secrets`, sinh theo lô cho cả cuộn, lọc trùng với DB bằng một câu `WHERE code IN (...)`, sinh bù phần trùng rồi `bulk_create`. UNIQUE trên `serial.code` là chốt cuối. Hàm chuẩn hoá mã khi tra (hoa, bỏ gạch, O→0, I/L→1) nằm ở `operations.services.labels.normalize_serial()`, dùng chung cho API nội bộ và công khai.

### 6.4 Truy xuất đệ quy (BR-31)

`operations/services/trace.py` tìm các lệnh liên quan bằng một câu `WITH RECURSIVE` qua `production_ingredient` và `ingredient_lot.production_order_id`, có mảng đường đi để chống lặp và giới hạn 12 tầng (mục 9, BR-31 d). Chiều ngược (up):

```sql
WITH RECURSIVE up(order_id, depth, path) AS (
  SELECT %(order_id)s::bigint, 0, ARRAY[%(order_id)s::bigint]
  UNION ALL
  SELECT il.production_order_id, up.depth + 1, up.path || il.production_order_id
  FROM up
  JOIN production_ingredient pi ON pi.production_order_id = up.order_id
  JOIN ingredient_lot il ON il.id = pi.ingredient_lot_id
  WHERE il.production_order_id IS NOT NULL
    AND il.production_order_id <> ALL(up.path)
    AND up.depth < 13
)
SELECT order_id, depth FROM up;
```

Có dòng `depth = 13` thì raise `BusinessError("TRACE_TOO_DEEP", ..., rule="BR-31")`. Chiều xuôi (down) đảo hướng join. Sau khi có tập lệnh, các nút (lô quế, phiếu, người bán, serial, phiếu xuất, người mua) lấy bằng ORM theo lô, dựng cây `{type, code, children, end?}` đúng mục 9. Hai index `production_ingredient(ingredient_lot_id)`, `ingredient_lot(production_order_id)` của mục 4 là bắt buộc cho câu này.

API công khai dùng cùng hàm truy ngược nhưng đi qua `website.services.public_trace()`, hàm này chỉ chép ra các trường mục 8.4 (xã/thôn, năm trồng, ảnh đồi, tên hộ khi `public_consent`, chứng nhận còn hiệu lực) và **bỏ toàn bộ nhánh phụ liệu** (BR-17, AC-31, AC-33). Mã đúng mẫu lô phụ liệu hay lô thành phẩm gửi vào `/api/public/trace/{code}` được xử lý như mã không tồn tại, cùng response, để không lộ đó là mã lô (AC-33).

### 6.5 Ảnh: sinh AVIF/WebP lúc upload

- `core.images.store_image(file) -> ImageRef`: kiểm loại (JPEG, PNG, WebP, HEIC nếu Pillow đọc được), tối đa 10 MB, tối đa 40 triệu điểm ảnh (đọc `img.size` ngay sau `Image.open`, trước khi giải nén; đặt `Image.MAX_IMAGE_PIXELS = 40_000_000` và coi `DecompressionBombWarning` là lỗi), vượt thì 400 `IMAGE_TOO_LARGE`, xoay theo EXIF rồi bỏ EXIF (ảnh đồi có toạ độ GPS), sinh các bề rộng 480, 960, 1440 px ở cả AVIF và WebP. Ảnh nhỏ hơn bề rộng nào thì bỏ bề rộng đó.
- Tên file theo băm nội dung: `MEDIA_ROOT/img/<2 ký tự đầu>/<sha256>-<w>.<avif|webp>`. Tên không đổi theo nội dung nên Caddy cache `immutable` được (van-hanh.md).
- Phần tử của `product.images`, `plot.photo_urls` (jsonb) có dạng sau. `url` và `alt` giữ đúng mục 4; các khoá còn lại là phần thêm để frontend dựng `srcset` và đặt `width`/`height` chống CLS:

```json
{"url": "/media/img/3f/3fa9…-1440.webp", "alt": "Tinh dầu quế 10 ml", "key": "3f/3fa9…", "w": 1440, "h": 1080, "widths": [480, 960, 1440]}
```

- Ảnh OG 1200×630 (mục 8.2) sinh thêm một bản JPEG khi ảnh được chọn làm ảnh đầu của sản phẩm.
- Upload: `POST /api/v1/images` (multipart, OWNER) trả `ImageRef`; sau đó PATCH entity với mảng ảnh mới. Ảnh nội bộ (chứng từ, COA, giấy chứng nhận không công khai) **không** lưu dưới `/media/` công khai (van-hanh.md); để `MEDIA_PRIVATE_ROOT`, tải qua endpoint có auth. Chi tiết endpoint này làm ở GĐ khi có màn tương ứng.
- Xử lý đồng bộ trong request: 6 bản ảnh mất khoảng 1–3 giây với ảnh điện thoại, chấp nhận được cho thao tác OWNER thỉnh thoảng làm; không cần hàng đợi.

## 7. Test, lint, kiểu, công cụ

### 7.1 Test

- pytest + pytest-django, chạy trên **PostgreSQL 16 thật** (DB trong compose dev; CI dùng `services: postgres:16`). Không dùng SQLite: các BR dựa vào `FOR UPDATE`, partial unique index, `WITH RECURSIVE`, UPSERT. Chạy `--reuse-db` khi dev.
- **Mỗi BR ít nhất một test ở tầng service**, đặt tên theo mã BR (mục 10, mục 11): file `operations/tests/test_br08_material_lot_stream.py`, hàm `test_br08_rejects_general_lot()`. Một BR nhiều ý thì nhiều hàm cùng tiền tố (`test_br27b_rejects_expired_lot`, `test_br27c_warns_gram_off`).
- Test API mỏng hơn: quyền (401/403 theo mục 2), hình dạng lỗi, ẩn giá WORKSHOP (mục 4.3), DTO công khai (BR-17: so tập khoá JSON với danh sách cho phép, và chuỗi response không chứa mã lô phụ liệu hay `vendor_name`).
- 8 luồng tích hợp của mục 11 và các AC của mục 12 là test qua HTTP với `django.test.Client`, ở `backend/tests/integration/test_ac01_receipt_controlled.py`… đặt tên theo mã AC.
- Dữ liệu test dựng bằng hàm trong `conftest.py` và `<app>/tests/factories.py` (hàm Python thường trả model). Không thêm factory_boy: dữ liệu ít loại, hàm thường đủ và dễ đọc.
- Mục tiêu phủ: 100% file `services/` có test; không đặt ngưỡng % toàn repo ở khung ban đầu.

### 7.2 Lint và kiểu

- **ruff** cho lint và format (thay black, isort, flake8): `line-length = 100`, `select = ["E", "F", "W", "I", "B", "UP", "DJ", "SIM", "RUF", "S"]`, bỏ `S101` trong test.
- **mypy + django-stubs** để kiểm kiểu. Chọn mypy thay pyright vì code này chủ yếu là ORM Django: plugin của django-stubs suy ra kiểu của field, manager, quan hệ ngược, `QuerySet[Model]`; pyright không có plugin nên các chỗ đó thành `Any` hoặc báo lỗi giả. Cái giá: mypy chậm hơn (vài giây với repo này, chấp nhận được). Cấu hình: `plugins = ["mypy_django_plugin.main"]`, `disallow_untyped_defs = true` cho `*/services/*`, `*/api/*`, `core/*`; migrations bỏ qua.
- **import-linter** (mục 1.3).

### 7.3 Lệnh (chạy trong `backend/`)

| Việc | Lệnh |
| --- | --- |
| Cài phụ thuộc | `uv sync` (CI: `uv sync --frozen`) |
| Thêm thư viện | `uv add <gói>` / `uv add --dev <gói>` |
| Chạy dev | `uv run python manage.py runserver 8000` |
| Migration | `uv run python manage.py makemigrations` / `migrate` |
| Tạo OWNER | `uv run python manage.py create_owner --username chu` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check . && uv run ruff format --check .` |
| Kiểu | `uv run mypy .` |
| Luật import | `uv run lint-imports` |
| Sinh OpenAPI | `uv run python manage.py export_openapi_schema --api config.api.api_v1 --output openapi/v1.json --indent 2` (và `api_public`) |

Makefile ở gốc repo gói các lệnh này (van-hanh.md). CI job backend chạy thêm `mypy`, `lint-imports` và kiểm OpenAPI (mục 3.4) bên cạnh các bước van-hanh.md đã liệt kê.

### 7.4 Cấu hình

Một file `config/settings.py` đọc biến môi trường bằng `os.environ` (vài dòng helper `env_bool`, `env_list`), không thêm django-environ. Biến backend:

| Biến | Ví dụ | Ghi chú |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | (bí mật) | bắt buộc khi `DEBUG=0` |
| `DJANGO_DEBUG` | `0` | |
| `DJANGO_ALLOWED_HOSTS` | `quevanyen.vn,backend` | có tên service compose vì Astro gọi `http://backend:8000` |
| `SITE_ORIGIN` | `https://quevanyen.vn` | cho `CSRF_TRUSTED_ORIGINS` |
| `DATABASE_URL` hoặc `POSTGRES_*` | | thống nhất với van-hanh.md |
| `TRUSTED_PROXY_CIDRS` | `172.28.0.0/24` | mục 5.1 |
| `IP_HASH_SALT` | (bí mật) | mục 5.1 |
| `MEDIA_ROOT`, `MEDIA_PRIVATE_ROOT` | `/srv/media`, `/srv/private` | |
| `ERROR_WEBHOOK_URL` | | 5xx về kênh đội (mục 11) |

Log JSON một dòng bằng formatter tự viết trong `core/logging.py` (trường `ts, level, logger, msg, request_id, user_id`, khớp van-hanh.md). Không log cookie, mật khẩu, IP gốc, số điện thoại người mua.

## 8. Luồng mẫu end-to-end cho khung code

Mục tiêu: chứng minh đủ các tầng chạy với nhau trước khi làm nghiệp vụ thật. Luồng:

1. OWNER đăng nhập: `GET /api/v1/auth/csrf` → `POST /api/v1/auth/login` → `GET /api/v1/auth/me`.
2. Tạo sản phẩm: `POST /api/v1/products` (status DRAFT) → `PATCH /api/v1/products/{id}` `{status: "PUBLISHED"}`. Mỗi bước ghi audit_log.
3. `GET /api/public/products/{slug}` trả DTO công khai. Sản phẩm DRAFT hoặc slug sai trả 404 `NOT_FOUND`.
4. Astro render `/san-pham/<slug>` từ DTO đó (phía frontend, xem frontend-seo.md).

Khung chỉ dựng phần mô hình cần cho luồng: `goods_type`, `product`, `slug_redirect` (chưa cần certificate; BR-14 làm ở GĐ3 cùng màn chứng nhận). operations để trống (chỉ `apps.py`, `models/__init__.py`) để import-linter có đủ lớp.

File backend cần có:

| File | Nội dung |
| --- | --- |
| `backend/pyproject.toml`, `uv.lock`, `.python-version` | phụ thuộc mục 0, cấu hình ruff, mypy, pytest, import-linter |
| `backend/manage.py`, `config/settings.py`, `config/urls.py`, `config/api.py`, `config/wsgi.py` | hai NinjaAPI, `/api/health` |
| `core/models.py` | TimeStampedModel, AuditLog, Setting, CodeCounter, ThrottleHit |
| `core/errors.py`, `core/handlers.py`, `core/audit.py`, `core/codes.py`, `core/clientip.py`, `core/throttle.py`, `core/pagination.py`, `core/roles.py`, `core/permissions.py`, `core/timeutil.py`, `core/logging.py` | hạ tầng mục 2–6 |
| `core/tests/test_role_matrix.py` | ma trận vai × route của mục 4.3 (khung chỉ có route auth và products) |
| `accounts/models.py`, `accounts/services.py`, `accounts/api.py`, `accounts/management/commands/create_owner.py` | đăng nhập, khoá 15 phút |
| `catalog/models/goods.py`, `catalog/models/product.py` | GoodsType, Product, SlugRedirect |
| `catalog/services/products.py` | `create_product`, `update_product` (đổi slug thì thêm slug_redirect) |
| `catalog/api/products.py`, `catalog/api/schemas/products.py` | `ProductIn`, `ProductPatch`, `ProductOut` |
| `catalog/migrations/0001_initial.py`, `0002_seed_goods_type.py` | |
| `operations/apps.py`, `operations/models/__init__.py` | app rỗng |
| `website/api/public.py`, `website/services.py`, `website/api/schemas/public.py` | `PublicProductOut`, `GET /products`, `GET /products/{slug}` |
| `openapi/v1.json`, `openapi/public.json` | sinh ra, commit |
| `conftest.py` | fixture `owner`, `workshop`, `owner_client`, `workshop_client` |
| `core/tests/test_br20_code_counter.py` | hai giao dịch song song không trùng số, rollback không thủng số |
| `core/tests/test_client_ip.py` | tin header chỉ khi REMOTE_ADDR trong dải; REMOTE_ADDR trong dải mà thiếu header hoặc mọi IP đều thuộc dải → `client_ip is None` |
| `accounts/tests/test_login.py` | đăng nhập, sai 5 lần thì 429, phiên 12 giờ |
| `catalog/tests/test_products_api.py` | WORKSHOP tạo sản phẩm hoặc sửa `featured_rank` bị 403, OWNER được, có audit_log; `featured_rank = 0` → 400 |
| `website/tests/test_br17_public_product_dto.py` | tập khoá DTO đúng danh sách cho phép, DRAFT trả 404 |
| `website/tests/test_public_products_featured.py` | `?featured=1`: lọc, thứ tự theo `featured_rank`, `limit` (mục 8) |
| `core/tests/test_schemas.py` | `require_http_url`, `require_media_path` (kể cả `%2e%2e` mã hoá một và hai lần) |
| `tests/integration/test_sample_flow.py` | chạy trọn bước 1–3 qua HTTP |

Chữ ký service mẫu:

```python
@transaction.atomic
def create_product(*, data: ProductCreate, actor: User) -> Product: ...

@transaction.atomic
def update_product(*, product_id: int, data: ProductUpdate, actor: User) -> Product: ...
```

`ProductCreate`, `ProductUpdate` là dataclass trong `catalog/services/products.py`; api chuyển từ schema Ninja sang dataclass để services không phụ thuộc Ninja.

DTO công khai: chỉ gồm các trường trang sản phẩm ở mục 8.2 cần, không có trường nội bộ như `recipe_code`, `requires_retention_sample`, `serial_tracked`, `status`. Tên trường theo frontend-seo.md mục 11 (G5) để trang, JSON-LD và feed Merchant đọc chung:

```python
class PublicProductOut(Schema):
    slug: str                      # slug hiện hành; gọi bằng slug cũ thì vẫn 200 với slug mới ở đây, Astro so với slug trên URL rồi tự 301
    sku: str; name: str
    spec: str                      # = product.size_label ("10 ml")
    unit: str
    retail_price: int | None       # VND
    availability: Literal["in_stock", "out_of_stock"]
    short_description: str | None  # = short_desc
    story_html: str | None         # story_md đã render và làm sạch ở backend
    usage_html: str | None
    images: list[ImageRef]
    og_image: str | None           # URL bản JPEG 1200×630 của ảnh đầu (mục 6.5)
    buy_links: list[BuyLink]
    seo_title: str | None; seo_description: str | None
    updated_at: datetime
    origin: PublicOrigin | None    # khối "Nguồn gốc" mục 8.2; khung để None, làm ở GĐ3
```

- `availability`: `serial_tracked = false` thì luôn `in_stock`; ngược lại `in_stock` khi có ít nhất một serial `IN_STOCK` thuộc lô `ACTIVE` của sản phẩm (một câu `EXISTS`, dùng index `serial(product_lot_id)`).
- **Backend là nơi duy nhất render Markdown lấy từ DB** (`story_md`, `usage_md`, `site_page.body_md`). Frontend không render lại, chỉ đưa `*_html` vào `set:html` (frontend-seo.md bỏ `marked`). Một hàm duy nhất:

  ```python
  # core/markdown.py
  ALLOWED_TAGS = {"p", "br", "ul", "ol", "li", "strong", "em", "a", "h2", "h3", "blockquote"}
  ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}
  URL_SCHEMES = {"http", "https", "mailto", "tel"}

  def render_public_markdown(src: str | None) -> str | None:
      """markdown.markdown(src) rồi nh3.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES,
      url_schemes=URL_SCHEMES, link_rel="nofollow noopener noreferrer", strip_comments=True)."""
  ```

  Không cho `<img>` trong nội dung Markdown: ảnh sản phẩm đi qua `images` (đã qua `store_image`). `nh3` bỏ `href` có scheme ngoài `URL_SCHEMES` (`javascript:`, `data:`, `vbscript:`) và bỏ mọi thuộc tính `on*`.
- URL trong DTO không đi qua nh3 nên validate ở schema:

  ```python
  # core/schemas.py
  SafeHttpUrl = Annotated[str, AfterValidator(require_http_url)]   # urlsplit: scheme ∈ {"http","https"}, có netloc; sai → 400 VALIDATION_ERROR
  SafeMediaPath = Annotated[str, AfterValidator(require_media_path)]  # xem require_media_path dưới

  def require_media_path(value: str) -> str:
      """Giải mã %XX lặp tới khi chuỗi không đổi (tối đa 5 vòng, còn đổi thì coi là sai),
      rồi mới kiểm trên chuỗi đã giải mã: bắt đầu bằng "/media/", không chứa "..", "//", "\\",
      không có ký tự điều khiển. Sai → ValueError (400 VALIDATION_ERROR). Trả lại `value` gốc."""
      s = value
      for _ in range(5):
          t = urllib.parse.unquote(s)
          if t == s:
              break
          s = t
      else:
          raise ValueError("media path encoded too deep")
      ...

  class ImageRef(Schema):
      url: SafeMediaPath       # bản WebP lớn nhất, "/media/img/<key>-<w>.webp"
      alt: str
      key: str                 # "3f/3fa9…" (2 ký tự đầu / sha256)
      w: int; h: int           # kích thước bản lớn nhất, để đặt width/height chống CLS
      widths: list[int]        # các bề rộng có thật, trong [480, 960, 1440]
  class BuyLink(Schema):
      channel: Literal["shopee", "tiktok", "zalo", "other"]; url: SafeHttpUrl
  ```

  Validate lúc **ghi** (schema vào của `api_v1`, PATCH sản phẩm) trả 400. Lúc **đọc**, service dựng `PublicProductOut` gọi cùng hai hàm `require_*` để lọc: phần tử sai bị bỏ khỏi danh sách và ghi log WARNING `unsafe_url_dropped`, không raise, để dữ liệu cũ hoặc sửa tay trong DB không lọt ra và cũng không làm trang 500. `og_image` dùng `SafeMediaPath | None`.
- Test bắt buộc trong `core/tests/test_markdown.py` và `website/tests/test_br17_public_product_dto.py`:
  - `[x](javascript:alert(1))` → `<a>` không còn `href`.
  - `<img src=x onerror=alert(1)>` và `<a href="#" onclick="...">` → không còn `img`, không còn `onerror`/`onclick`.
  - `<script>`, `<iframe>`, `<style>` thô trong Markdown → bị bỏ.
  - `buy_links[].url = "javascript:alert(1)"` hoặc `"//evil.com"` → PATCH trả 400; dòng đã nằm trong DB thì DTO công khai bỏ link đó, không trả 500.
  - `ImageRef` có `url = "https://evil.com/a.webp"`, `"/media/../x"`, `"/media/%2e%2e/x"`, `"/media/%252e%252e/x"` (mã hoá hai lần) hoặc `"/media/a%2f%2fb"` → 400 (`core/tests/test_schemas.py`).
- **Sản phẩm nổi bật (sếp chọn tự sắp, #773 câu 6).** Thêm cột vào `catalog.Product` (bảng `product`, TK mục 4), nằm luôn trong `0001_initial.py` vì khung chưa có dữ liệu:

  ```python
  # catalog/models/product.py
  featured_rank = models.PositiveSmallIntegerField(null=True, blank=True)  # null = không nổi bật; 1 đứng đầu

  class Meta:
      constraints = [
          models.CheckConstraint(
              condition=Q(featured_rank__isnull=True) | Q(featured_rank__gt=0),
              name="product_featured_rank_gt_0",
          ),
      ]
  ```

  Không đặt UNIQUE: hai sản phẩm trùng hạng vẫn hợp lệ, sắp phụ theo `updated_at` giảm dần rồi `id`, nên sếp đổi chỗ hai sản phẩm không vướng ràng buộc giữa chừng. Không cần index (vài chục sản phẩm).

  API quản lý: `ProductIn`, `ProductPatch` có `featured_rank: int | None = Field(None, ge=1, le=999)`; `ProductOut` trả `featured_rank`; dataclass `ProductCreate`, `ProductUpdate` thêm `featured_rank: int | None`. Route tạo/sửa sản phẩm đã là `OWNER_ONLY` (mục 4.3) nên chỉ OWNER đổi được trường này; PATCH gửi `featured_rank: null` là bỏ nổi bật. Đổi giá trị ghi audit_log như mọi trường khác của `update_product`. `PublicProductOut` **không** có `featured_rank`.
- `GET /api/public/products` nhận:

  ```python
  def list_products(request, goods_type: str | None = None, featured: bool = False,
                    limit: int = Query(50, ge=1, le=100)) -> list[PublicProductOut]: ...
  ```

  Mặc định: sản phẩm PUBLISHED, sắp `updated_at` giảm dần. `?featured=1`: thêm điều kiện `featured_rank IS NOT NULL`, sắp `featured_rank` tăng dần, rồi `updated_at` giảm dần, rồi `id`; vẫn cắt theo `limit` và vẫn lọc `goods_type` nếu có. Trang chủ gọi `?featured=1&limit=6`; danh sách rỗng (sếp chưa chọn) thì frontend tự gọi lại `?limit=6` để trang chủ không trống.
- Test khi dựng khung (`website/tests/test_public_products_featured.py`, `catalog/tests/test_products_api.py`):
  - `?featured=1` chỉ trả sản phẩm có `featured_rank`, không trả sản phẩm DRAFT dù có hạng.
  - Thứ tự: hạng 1, 2, 3 ra đúng thứ tự dù `updated_at` ngược lại; hai sản phẩm cùng hạng thì cái mới cập nhật đứng trước; `limit=2` cắt đúng 2.
  - Không có `featured` thì thứ tự vẫn theo `updated_at` như cũ.
  - WORKSHOP `PATCH /api/v1/products/{id}` `{featured_rank: 1}` → 403, DB không đổi; OWNER gửi `0` → 400 `VALIDATION_ERROR`; ghi thẳng `0` vào DB → `IntegrityError` (CHECK).
- `GET /api/public/pages` trả `[{slug, title, updated_at}]` của trang PUBLISHED, dùng cho sitemap.
- Slug cũ (TK 8, AC-19): `GET /api/public/products/{slug}` tìm `product.slug` trước; không thấy thì tra `slug_redirect(old_slug)` (bảng TK mục 4, thuộc catalog) và trả **200** với `PublicProductOut` của sản phẩm đích, `slug` là slug hiện hành. Không thấy cả hai, hoặc sản phẩm không PUBLISHED → 404. Django không tự chuyển hướng: Astro so `slug` trong DTO với slug trên URL, khác thì 301 sang `/san-pham/<slug mới>` (frontend-seo.md 6.5). `update_product` đổi slug thì thêm dòng `slug_redirect(old_slug=<slug cũ>)`, xoá dòng có `old_slug` bằng slug mới của chính sản phẩm đó (đổi tên rồi đổi lại), và trả 409 `SLUG_TAKEN` nếu slug mới trùng `product.slug` hoặc `old_slug` của sản phẩm khác. Test: `website/tests/test_public_slug_redirect.py`.

Nghiệm thu khung (phần backend): `uv run pytest`, `ruff`, `mypy`, `lint-imports` đều xanh; `docker compose up` rồi chạy tay bước 1–3 bằng `curl` ra đúng kết quả.

## 9. Bổ sung và lệch so với thiết kế chi tiết

Các điểm dưới đây cần sếp biết khi duyệt; không điểm nào đổi nghiệp vụ.

| # | Điểm | Lý do |
| --- | --- | --- |
| 1 | Thêm bảng kỹ thuật `throttle_hit` (core) | Throttle dùng chung cho 3 worker mà không thêm Redis (mục 5.2) |
| 2 | Thêm `REVEAL`, `EXPORT`, `ANONYMIZE`, `DELETE_LINE` vào CHECK của `audit_log.action` | Mục 9 yêu cầu ghi audit_log khi xem đầy đủ, xuất CSV, xoá thông tin người mua, bỏ dòng lệnh DRAFT; enum mục 4 chưa có các giá trị này |
| 3 | Thêm 429 vào danh sách mã HTTP (`RATE_LIMITED`, `LOGIN_LOCKED`) | Mục 9 có giới hạn tần suất và khoá đăng nhập nhưng chưa nêu mã trả về |
| 4 | Lỗi kiểm dữ liệu trả 400, không dùng 422 mặc định của Ninja | Theo mục 9 |
| 5 | Ngưỡng 60/phút cho `/api/public/trace`, 300/phút cho products và pages | Tránh 429 với Googlebot/AdsBot trên trang SSR (mục 5.2) |
| 6 | Thêm `GET /api/v1/auth/csrf`, `POST /api/v1/images`, `GET /api/health` | Cần cho CSRF, upload ảnh, healthcheck; mục 9 chưa có |
| 7 | Phần tử ảnh jsonb có thêm `key, w, h, widths` ngoài `url, alt` | Dựng srcset AVIF/WebP và chống CLS (mục 6.5) |
| 8 | "Phiếu đang lập" của WORKSHOP = phiếu của chính họ, SAVED, lập hôm nay giờ VN | Làm rõ ngoại lệ ẩn giá ở mục 2 (mục 4.3) |
| 9 | Số cân, gram trả dạng chuỗi thập phân trong JSON | Giữ đủ chính xác `numeric` (mục 3.1) |
| 10 | Khoá đăng nhập theo cặp tài khoản + IP (5 lần sai / 15 phút), thêm khoá theo IP (20 lần / 15 phút) | Mục 9 chỉ ghi "khoá 15 phút sau 5 lần sai". Khoá theo tài khoản thì người ngoài sai 5 lần là khoá được OWNER (mục 4.1). Cái giá: kẻ dò mật khẩu đổi IP liên tục thì mỗi IP vẫn được thử 5 lần; argon2 và quy mô 5 người dùng làm việc này chậm và ít lợi |
| 11 | DTO sản phẩm công khai trả `story_html`/`usage_html` đã render, thêm `availability`, `og_image`, `updated_at` | Cho JSON-LD `Offer`, feed Merchant và sitemap (frontend-seo.md G5) |
| 12 | Thêm cột `product.featured_rank` (smallint, null = không nổi bật, CHECK > 0) và `GET /api/public/products?featured=1` | Sếp đã chọn tự sắp sản phẩm nổi bật (#773 câu 6); mục 4 chưa có cột này (mục 8) |

## 10. Rủi ro

- **Khoá và deadlock**: sai thứ tự khoá giữa hai service sẽ treo máy quét ở giờ cao điểm. Giảm bằng quy tắc cha trước con sau (mục 6.2) và test song song cho BR-07, BR-12, BR-20.
- **FK vòng trong operations**: Django tự xử lý, nhưng tách operations thành hai app về sau sẽ phải sửa migration bằng tay. Đây là chỗ khó quay lui nhất; vì vậy đã gộp từ đầu (#671 c).
- **Data migration seed**: sửa công thức trong seed sau khi đã chạy production không có tác dụng (migration không chạy lại). Sau go-live, đổi danh mục qua API/màn hình, không qua migration.
- **Lộ dữ liệu ở API công khai**: chỉ chặn được nếu DTO dựng tay từng trường. Không bao giờ `PublicXxxOut.from_orm(model)` với model có trường nội bộ mà không qua whitelist; test BR-17 so tập khoá.
- **Contract IP với Caddy/Astro**: nếu Caddy đổi sang nối thêm mà tin header khách gửi lên (bật `trusted_proxies`), khách có thể giả IP để lách throttle. Astro lỡ nối thêm IP của Caddy thì vẫn đúng nhờ duyệt từ phải sang trái (mục 5.1). Test `test_client_ip.py` giữ phía Django; phía Caddy/Astro cần một smoke test sau deploy.
- **Ảnh xử lý đồng bộ**: ảnh rất lớn có thể giữ worker vài giây; 3 worker thì các request khác vẫn chạy. Nếu thành vấn đề thì mới cân nhắc hàng đợi.

## 11. Thứ tự làm và chỗ không chạm cùng lúc

1. `config/`, `core/` (errors, handlers, audit, codes, clientip, throttle, pagination, permissions) và `accounts/`: một người làm, vì mọi app khác phụ thuộc. Xong mới mở việc song song.
2. Luồng mẫu mục 8 (catalog product + website public), cùng lúc frontend dựng trang `/san-pham/<slug>` dựa trên `openapi/public.json`.
3. Sau khung: catalog (PH1) → operations nhóm receiving/sales (GĐ1) → production/labels/trace (GĐ2) → website đầy đủ (GĐ3), theo lộ trình.

Chỗ hai task không được sửa cùng lúc:

- `core/` và `config/api.py`: file dùng chung, mỗi lúc một task giữ.
- `migrations/` của cùng một app: hai nhánh cùng tạo migration sẽ trùng số; mỗi app mỗi lúc một task thêm model.
- `backend/openapi/*.json`: sinh tự động, ai đổi API thì sinh lại trong cùng PR; hai PR cùng đổi thì rebase rồi sinh lại, không sửa tay.
- `pyproject.toml`, `uv.lock`: thêm thư viện là việc riêng, báo Lead.
