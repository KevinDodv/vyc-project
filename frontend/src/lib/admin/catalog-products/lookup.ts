/** Phần thuần của việc nạp dữ liệu cho form: gom các trang danh sách và tra đồi theo id. */

import type { Plot } from "./certificate";

/** Cỡ trang lớn nhất API cho phép. */
export const PAGE_SIZE = 200;
const MAX_PAGES = 50;

/** Gom mọi trang của một danh sách; `fetchPage` trả null khi lỗi thì cả kết quả là null. */
export async function collectPages<T>(
  fetchPage: (page: number) => Promise<{ items: T[]; total: number } | null>,
): Promise<T[] | null> {
  const all: T[] = [];
  for (let page = 1; page <= MAX_PAGES; page++) {
    const got = await fetchPage(page);
    if (got === null) return null;
    all.push(...got.items);
    if (got.items.length === 0 || all.length >= got.total) break;
  }
  return all;
}

export type PlotLookup = {
  /** Đồi cần tra, theo id. */
  found: Map<number, Plot>;
  /** Mọi đồi của những người bán đã hỏi, theo id người bán. */
  bySupplier: Map<number, Plot[]>;
};

const BATCH = 8;

/** API chưa có «lấy đồi theo id» nên phải hỏi lần lượt đồi của từng người bán, dừng khi đủ.
 *  Người bán đang có đồi dùng được hỏi trước; người bán chỉ còn đồi ngừng dùng hỏi sau.
 *  Cả một lượt đều lỗi thì thôi, để trang không treo khi API đang hỏng. */
export async function findPlots(
  suppliers: ReadonlyArray<{ id: number; plots_count: number }>,
  plotIds: ReadonlyArray<number | null>,
  fetchPlots: (supplierId: number) => Promise<Plot[] | null>,
): Promise<PlotLookup> {
  const wanted = new Set(plotIds.filter((id): id is number => id !== null));
  const found = new Map<number, Plot>();
  const bySupplier = new Map<number, Plot[]>();
  const ordered = [...suppliers].sort(
    (a, b) => Number(b.plots_count > 0) - Number(a.plots_count > 0),
  );
  for (let i = 0; i < ordered.length && found.size < wanted.size; i += BATCH) {
    const batch = ordered.slice(i, i + BATCH);
    const results = await Promise.all(batch.map((s) => fetchPlots(s.id)));
    results.forEach((plots, index) => {
      const supplier = batch[index];
      if (!plots || !supplier) return;
      bySupplier.set(supplier.id, plots);
      for (const plot of plots) if (wanted.has(plot.id)) found.set(plot.id, plot);
    });
    if (results.every((r) => r === null)) break;
  }
  return { found, bySupplier };
}
