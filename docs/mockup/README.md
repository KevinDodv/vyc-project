# Mockup giao diện

- `goc/mockup-goc.html`: bản sếp gửi (tin #337), **không sửa**.
- `ban-chinh.html`: **bản chính**, **80 màn** (chép đè từ `de-xuat/ban-xem-truoc.html`; Lead duyệt theo uỷ quyền của sếp #804, ngày 21/11/2026). Mở thẳng bằng trình duyệt. Sau này sửa thì sửa ở `de-xuat/`, ghép lại rồi chép đè.
- `de-xuat/man/<cụm>/<STT>-<key>.html`: mỗi màn một file (giữ `<!--APPCSS-->`); `de-xuat/man/app.css` là CSS chung; mỗi cụm có `_ds.json` liệt kê `{stt,key,title,group,kind}`.
  Cụm: `a-nhap-xuat-kho` (02–14), `b-san-xuat` (15–18, 23, 24, 26), `c-quan-ly-in-qr` (còn lại).
- `_tools/vo.html`: vỏ (HTML/JS ngoài JSON), chỗ dữ liệu là `@@DATA@@`.
- `de-xuat/ban-xem-truoc.html`: bản ghép, mở thẳng bằng trình duyệt.

## Lệnh (cần Node)

```
node docs/mockup/_tools/mockup.mjs tach   # đọc bản gốc -> ghi lại man/, app.css, vo.html (ghi đè de-xuat/man!)
node docs/mockup/_tools/mockup.mjs ghep   # man/ + vo.html -> de-xuat/ban-xem-truoc.html, rồi so với bản gốc
```

`ghep` in `OK: dữ liệu giống bản gốc` khi chưa có màn nào bị sửa/thêm; sau khi sửa thì in "KHÁC" (bình thường).

Thêm màn mới: tạo file `<STT>-<key>.html` trong cụm, thêm vào `_ds.json` của cụm với trường `"sau": "<key màn đứng trước>"`; `ghep` chèn đúng chỗ. Màn cũ giữ đúng thứ tự gốc theo `stt`.
