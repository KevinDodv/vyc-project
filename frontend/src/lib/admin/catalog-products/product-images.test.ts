import { describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "../../../scripts/admin/api";
import { GENERIC_ERROR } from "../form";
import type { ProductImage } from "./product";
import {
  addImage,
  checkImageFile,
  MAX_IMAGE_BYTES,
  MAX_IMAGES,
  moveItem,
  type UploadedImage,
  uploadErrorMessage,
  uploadImages,
} from "./product-images";

const uploaded = (key: string): UploadedImage => ({
  url: `/media/img/${key}-960.webp`,
  key,
  w: 960,
  h: 720,
  widths: [480, 960],
});
const image = (key: string): ProductImage => ({ ...uploaded(key), alt: `Ảnh ${key}` });
const file = (name: string, type = "image/jpeg", size = 10) =>
  ({ name, type, size }) as unknown as File;

describe("checkImageFile", () => {
  it("nhận JPEG, PNG, WebP tới đúng 10 MB", () => {
    for (const type of ["image/jpeg", "image/png", "image/webp"]) {
      expect(checkImageFile({ type, size: MAX_IMAGE_BYTES })).toBeNull();
    }
  });
  it("quá 10 MB thì báo tiếng Việt", () => {
    expect(checkImageFile({ type: "image/png", size: MAX_IMAGE_BYTES + 1 })).toContain("10 MB");
  });
  it("sai loại thì báo tiếng Việt", () => {
    expect(checkImageFile({ type: "application/pdf", size: 1 })).toContain("JPEG, PNG hoặc WebP");
  });
  it("trình duyệt không biết loại thì để backend kiểm", () => {
    expect(checkImageFile({ type: "", size: 1 })).toBeNull();
  });
});

describe("addImage", () => {
  it("thêm vào cuối với alt trống, không sửa mảng cũ", () => {
    const before = [image("a")];
    const result = addImage(before, uploaded("b"));
    expect(result.ok && result.images.map((i) => i.key)).toEqual(["a", "b"]);
    expect(result.ok && result.added).toEqual({ ...uploaded("b"), alt: "" });
    expect(before).toHaveLength(1);
  });
  it("không thêm ảnh trùng key", () => {
    expect(addImage([image("a")], uploaded("a"))).toMatchObject({ ok: false });
  });
  it(`không quá ${MAX_IMAGES} ảnh`, () => {
    const full = Array.from({ length: MAX_IMAGES }, (_, i) => image(`k${i}`));
    expect(addImage(full, uploaded("moi"))).toMatchObject({ ok: false });
  });
});

describe("moveItem", () => {
  it("chuyển lên và xuống", () => {
    expect(moveItem(["a", "b", "c"], 1, -1)).toEqual(["b", "a", "c"]);
    expect(moveItem(["a", "b", "c"], 1, 1)).toEqual(["a", "c", "b"]);
  });
  it("ở đầu, cuối hoặc ngoài danh sách thì giữ nguyên", () => {
    expect(moveItem(["a", "b"], 0, -1)).toEqual(["a", "b"]);
    expect(moveItem(["a", "b"], 1, 1)).toEqual(["a", "b"]);
    expect(moveItem(["a", "b"], -1, 1)).toEqual(["a", "b"]);
  });
});

describe("uploadErrorMessage", () => {
  it.each(["IMAGE_TOO_LARGE", "IMAGE_INVALID"])("%s giữ nguyên message của API", (code) => {
    expect(uploadErrorMessage(new ApiRequestError(400, code, "Thông báo API"))).toBe(
      "Thông báo API",
    );
  });
  it("413 từ proxy thành lỗi quá dung lượng", () => {
    expect(uploadErrorMessage(new ApiRequestError(413, "HTTP_413", "bận"))).toContain("10 MB");
  });
  it("lỗi mạng thành thông báo chung", () => {
    expect(uploadErrorMessage(new TypeError("fetch failed"))).toBe(GENERIC_ERROR);
  });
});

describe("uploadImages", () => {
  function run(files: File[], upload: (f: File) => Promise<UploadedImage>, start = 0) {
    let images = Array.from({ length: start }, (_, i) => image(`cu${i}`));
    const spy = vi.fn(upload);
    const done = uploadImages(files, {
      upload: spy,
      current: () => images,
      added: (added) => {
        images = [...images, added];
      },
    });
    return { done, spy, keys: () => images.map((i) => i.key) };
  }

  it("tải lần lượt, file lỗi không chặn file sau và lỗi kèm tên file", async () => {
    const r = run(
      [file("a.jpg"), file("b.pdf", "application/pdf"), file("c.jpg"), file("d.jpg")],
      async (f) => {
        if (f.name === "c.jpg") {
          throw new ApiRequestError(400, "IMAGE_INVALID", "File đã hỏng");
        }
        return uploaded(f.name);
      },
    );
    const errors = await r.done;
    expect(r.keys()).toEqual(["a.jpg", "d.jpg"]);
    expect(r.spy).toHaveBeenCalledTimes(3);
    expect(errors).toEqual(["b.pdf: Chỉ nhận ảnh JPEG, PNG hoặc WebP", "c.jpg: File đã hỏng"]);
  });

  it("đủ số ảnh thì không tải thêm", async () => {
    const r = run([file("a.jpg"), file("b.jpg")], async (f) => uploaded(f.name), MAX_IMAGES - 1);
    const errors = await r.done;
    expect(r.spy).toHaveBeenCalledTimes(1);
    expect(r.keys()).toHaveLength(MAX_IMAGES);
    expect(errors).toHaveLength(1);
    expect(errors[0]).toContain("b.jpg");
  });
});
