/** Ảnh của form sản phẩm: tải lên qua POST /api/v1/images, thêm, gỡ, đổi thứ tự. Phần xử lý mảng là
 *  hàm thuần; phần DOM dựng mọi dòng ảnh từ `template[data-image-template]` của `_ProductForm.astro`.
 *  Ảnh tải xong mới nằm trong form, sản phẩm chỉ đổi khi bấm «Lưu» (alt bắt buộc nhập trước). */

import { ApiRequestError, api } from "../../../scripts/admin/api";
import type { components } from "../../api/v1";
import { GENERIC_ERROR } from "../form";
import type { ProductImage } from "./product";

/** Thân trả về của POST /images: `ProductImage` chưa có `alt`. */
export type UploadedImage = components["schemas"]["ImageOut"];

/** Ba giới hạn khớp backend (`ProductIn.images`, `core.images`). */
export const MAX_IMAGES = 20;
export const MAX_IMAGE_BYTES = 10 * 1024 * 1024;
export const ACCEPTED_IMAGE_TYPES: readonly string[] = ["image/jpeg", "image/png", "image/webp"];

const TOO_LARGE = "Ảnh quá 10 MB, hãy giảm dung lượng rồi tải lại";
const WRONG_TYPE = "Chỉ nhận ảnh JPEG, PNG hoặc WebP";
const LIMIT_REACHED = `Mỗi sản phẩm tối đa ${MAX_IMAGES} ảnh, hãy gỡ bớt rồi tải thêm`;

/** Chặn sớm file chắc chắn bị từ chối để khỏi tải lên vô ích; backend vẫn là nơi quyết định.
 *  Trình duyệt không đoán được loại file (`type` rỗng) thì để backend kiểm. */
export function checkImageFile(file: { type: string; size: number }): string | null {
  if (file.type && !ACCEPTED_IMAGE_TYPES.includes(file.type)) return WRONG_TYPE;
  if (file.size > MAX_IMAGE_BYTES) return TOO_LARGE;
  return null;
}

export type AddResult =
  | { ok: true; images: ProductImage[]; added: ProductImage }
  | { ok: false; message: string };

/** Thêm ảnh vừa tải vào cuối danh sách với alt trống. Cùng nội dung file thì backend trả cùng `key`. */
export function addImage(images: readonly ProductImage[], uploaded: UploadedImage): AddResult {
  if (images.some((image) => image.key === uploaded.key)) {
    return { ok: false, message: "Ảnh này đã có trong danh sách" };
  }
  if (images.length >= MAX_IMAGES) return { ok: false, message: LIMIT_REACHED };
  const { url, key, w, h, widths } = uploaded;
  const added: ProductImage = { url, alt: "", key, w, h, widths };
  return { ok: true, images: [...images, added], added };
}

/** Đổi chỗ phần tử `index` với hàng xóm phía trước (-1) hoặc sau (1). Ra ngoài danh sách thì giữ nguyên. */
export function moveItem<T>(items: readonly T[], index: number, delta: -1 | 1): T[] {
  const next = [...items];
  const item = next[index];
  const other = next[index + delta];
  if (item === undefined || other === undefined) return next;
  next[index] = other;
  next[index + delta] = item;
  return next;
}

/** `message` của API đã là tiếng Việt (IMAGE_TOO_LARGE, IMAGE_INVALID…). 413 do proxy trả, không có JSON. */
export function uploadErrorMessage(error: unknown): string {
  if (!(error instanceof ApiRequestError)) return GENERIC_ERROR;
  return error.status === 413 ? TOO_LARGE : error.message;
}

export type UploadDeps = {
  upload: (file: File) => Promise<UploadedImage>;
  /** Danh sách đang có trên form, đọc lại mỗi lần vì người dùng gỡ được ảnh trong lúc đang tải. */
  current: () => ProductImage[];
  added: (image: ProductImage) => void;
  progress?: (position: number, total: number) => void;
};

/** Tải lần lượt từng file (backend xử lý ảnh tốn bộ nhớ). File lỗi không chặn file sau; trả danh sách lỗi
 *  kèm tên file. */
export async function uploadImages(files: readonly File[], deps: UploadDeps): Promise<string[]> {
  const errors: string[] = [];
  for (const [index, file] of files.entries()) {
    const rejected = deps.current().length >= MAX_IMAGES ? LIMIT_REACHED : checkImageFile(file);
    if (rejected) {
      errors.push(`${file.name}: ${rejected}`);
      continue;
    }
    deps.progress?.(index + 1, files.length);
    try {
      const result = addImage(deps.current(), await deps.upload(file));
      if (result.ok) deps.added(result.added);
      else errors.push(`${file.name}: ${result.message}`);
    } catch (error) {
      errors.push(`${file.name}: ${uploadErrorMessage(error)}`);
    }
  }
  return errors;
}

function sendFile(file: File): Promise<UploadedImage> {
  const body = new FormData();
  body.append("file", file);
  return api.post<UploadedImage>("/images", body);
}

/** Đọc các dòng ảnh: `data-image` (JSON của ảnh) cộng với ô alt đang sửa. */
export function readImageRows(form: ParentNode): ProductImage[] {
  const images: ProductImage[] = [];
  for (const row of Array.from(form.querySelectorAll<HTMLElement>("[data-image-row]"))) {
    try {
      const image = JSON.parse(row.dataset.image ?? "") as ProductImage;
      const alt = row.querySelector<HTMLInputElement>("input[data-image-alt]")?.value ?? "";
      images.push({ ...image, alt });
    } catch {
      // Dòng ảnh hỏng không thể gửi lại nguyên vẹn: bỏ qua thay vì gửi dữ liệu thiếu.
    }
  }
  return images;
}

export function bindProductImages(
  form: HTMLFormElement,
  upload: UploadDeps["upload"] = sendFile,
): void {
  const list = form.querySelector<HTMLElement>("[data-images]");
  const template = form.querySelector<HTMLTemplateElement>("template[data-image-template]");
  if (!list || !template) return;
  const empty = form.querySelector<HTMLElement>("[data-images-empty]");
  const input = form.querySelector<HTMLInputElement>("input[data-image-file]");
  const status = form.querySelector<HTMLElement>("[data-image-upload-status]");
  const errorBox = form.querySelector<HTMLElement>("[data-image-upload-error]");
  const rows = () => Array.from(list.querySelectorAll<HTMLElement>("[data-image-row]"));

  /** Đánh số lại nhãn theo thứ tự hiện tại và khoá nút không đi tiếp được. */
  const renumber = (): void => {
    const all = rows();
    all.forEach((row, index) => {
      const n = index + 1;
      const title = row.querySelector<HTMLElement>("[data-image-title]");
      if (title) title.textContent = `Mô tả ảnh ${n} (alt)`;
      const alt = row.querySelector<HTMLInputElement>("input[data-image-alt]");
      if (alt) alt.dataset.label = `Mô tả ảnh ${n}`;
      const up = row.querySelector<HTMLButtonElement>("button[data-image-up]");
      const down = row.querySelector<HTMLButtonElement>("button[data-image-down]");
      if (up) up.disabled = index === 0;
      if (down) down.disabled = index === all.length - 1;
      up?.setAttribute("aria-label", `Chuyển ảnh ${n} lên`);
      down?.setAttribute("aria-label", `Chuyển ảnh ${n} xuống`);
      row.querySelector("[data-image-remove]")?.setAttribute("aria-label", `Gỡ ảnh ${n}`);
    });
    if (empty) empty.hidden = all.length > 0;
  };

  const append = (image: ProductImage): void => {
    const fragment = template.content.cloneNode(true) as DocumentFragment;
    const row = fragment.querySelector<HTMLElement>("[data-image-row]");
    if (!row) return;
    row.dataset.image = JSON.stringify(image);
    const thumb = row.querySelector<HTMLImageElement>("img[data-image-thumb]");
    if (thumb) thumb.src = image.url;
    const alt = row.querySelector<HTMLInputElement>("input[data-image-alt]");
    if (alt) alt.value = image.alt;
    list.append(row);
    renumber();
  };

  try {
    const initial = JSON.parse(list.dataset.initialImages ?? "[]") as ProductImage[];
    for (const image of initial) append(image);
  } catch {
    // Trang render sai dữ liệu: để danh sách trống, PATCH một phần không đụng ảnh nếu không đổi gì.
  }
  renumber();

  list.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    const button = target?.closest<HTMLButtonElement>("button");
    const row = button?.closest<HTMLElement>("[data-image-row]");
    if (!button || !row) return;
    if (button.hasAttribute("data-image-remove")) {
      row.remove();
      renumber();
      input?.focus();
    } else {
      const delta = button.hasAttribute("data-image-up") ? -1 : 1;
      list.append(...moveItem(rows(), rows().indexOf(row), delta));
      renumber();
      // Dời dòng làm mất focus; nút vừa bấm bị khoá (đã tới đầu/cuối) thì sang nút còn lại.
      const next = button.disabled
        ? row.querySelector<HTMLButtonElement>("button:not([disabled])")
        : button;
      next?.focus();
    }
    // Lỗi ảnh ghi theo số thứ tự cũ, không còn đúng sau khi gỡ hoặc đổi chỗ.
    const slot = form.querySelector<HTMLElement>('[data-error-for="images"]');
    if (slot) slot.hidden = true;
  });

  input?.addEventListener("change", async () => {
    const files = Array.from(input.files ?? []);
    if (files.length === 0) return;
    // Khoá «Lưu» trong lúc tải để không lưu thiếu ảnh.
    const save = form.querySelector<HTMLButtonElement>('button[data-action="save"]');
    input.disabled = true;
    if (save) save.disabled = true;
    if (errorBox) errorBox.hidden = true;
    let firstNew: HTMLElement | undefined;
    const errors = await uploadImages(files, {
      upload,
      current: () => readImageRows(list),
      added: (image) => {
        append(image);
        firstNew ??= rows().at(-1);
      },
      progress: (position, total) => {
        if (status) status.textContent = `Đang tải ảnh ${position}/${total}…`;
      },
    });
    input.value = "";
    input.disabled = false;
    if (save) save.disabled = false;
    if (status) {
      status.textContent = firstNew ? "Đã tải ảnh lên. Nhập mô tả (alt) rồi bấm «Lưu»." : "";
    }
    if (errorBox && errors.length > 0) {
      errorBox.textContent = errors.join("\n");
      errorBox.hidden = false;
    }
    firstNew?.querySelector<HTMLInputElement>("input[data-image-alt]")?.focus();
  });
}
