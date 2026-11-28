/** Màn địa bàn (task #93): cây Tỉnh › Xã › Thôn, bộ lọc, trường form. Kiểu theo lib/api/v1.d.ts. */

import type { components } from "../../api/v1";
import type { FieldDef, FieldOption, StatusFilter } from "../catalog";
import { formatIsoDate, matchesQuery } from "./text";

export type AreaNode = components["schemas"]["AreaNode"];

export type AreaLevel = "PROVINCE" | "COMMUNE" | "VILLAGE";

export const LEVEL_LABEL: Record<AreaLevel, string> = {
  PROVINCE: "Tỉnh",
  COMMUNE: "Xã",
  VILLAGE: "Thôn",
};

/** Cấp của địa bàn cha: xã thuộc tỉnh, thôn thuộc xã, tỉnh không có cha. */
export const PARENT_LEVEL: Record<AreaLevel, AreaLevel | null> = {
  PROVINCE: null,
  COMMUNE: "PROVINCE",
  VILLAGE: "COMMUNE",
};

export function isAreaLevel(value: unknown): value is AreaLevel {
  return value === "PROVINCE" || value === "COMMUNE" || value === "VILLAGE";
}

export function levelLabel(level: string): string {
  return isAreaLevel(level) ? LEVEL_LABEL[level] : level;
}

export type AreaRow = {
  id: number;
  status: "ACTIVE" | "INACTIVE";
  code: string;
  name: string;
  level: string;
  levelLabel: string;
  depth: number;
  former_name: string | null;
  valid_from: string;
};

const INDENT = "    ";

/** Tên hiện ở danh sách: thụt vào theo cấp để thấy cây (CatalogList chỉ nhận chuỗi). */
export function treeLabel(row: Pick<AreaRow, "name" | "depth">): string {
  return row.depth === 0 ? row.name : `${INDENT.repeat(row.depth - 1)}└ ${row.name}`;
}

export function formatValidFrom(value: unknown): string {
  return typeof value === "string" ? formatIsoDate(value) : "";
}

function asStatus(value: string): "ACTIVE" | "INACTIVE" {
  return value === "INACTIVE" ? "INACTIVE" : "ACTIVE";
}

/** Cây → danh sách phẳng theo thứ tự duyệt sâu. Có từ khoá hoặc lọc tình trạng thì giữ dòng khớp
 *  và mọi cấp trên của nó (để còn thấy đường đi trong cây). */
export function flattenAreaTree(
  nodes: readonly AreaNode[],
  filter: { q?: string; status?: StatusFilter } = {},
): AreaRow[] {
  const q = filter.q ?? "";
  const status = filter.status ?? "";
  const filtering = q !== "" || status !== "";

  const visit = (node: AreaNode, depth: number): AreaRow[] => {
    const children = (node.children ?? []).flatMap((c) => visit(c, depth + 1));
    const self =
      matchesQuery(q, node.name, node.code, node.former_name) &&
      (status === "" || node.status === status);
    if (filtering && !self && children.length === 0) return [];
    return [
      {
        id: node.id,
        status: asStatus(node.status),
        code: node.code,
        name: node.name,
        level: node.level,
        levelLabel: levelLabel(node.level),
        depth,
        former_name: node.former_name,
        valid_from: node.valid_from,
      },
      ...children,
    ];
  };
  return nodes.flatMap((root) => visit(root, 0));
}

/** Cây → mọi nút, để tra theo id hoặc lập danh sách chọn cha. */
export function allAreas(nodes: readonly AreaNode[]): AreaNode[] {
  const out: AreaNode[] = [];
  const walk = (list: readonly AreaNode[]) => {
    for (const n of list) {
      out.push(n);
      walk(n.children ?? []);
    }
  };
  walk(nodes);
  return out;
}

export function findArea(nodes: readonly AreaNode[], id: number): AreaNode | null {
  return allAreas(nodes).find((n) => n.id === id) ?? null;
}

/** Nhãn có đường đi: «Lào Cai › Phong Dụ Hạ». */
export function areaPathLabel(nodes: readonly AreaNode[], area: AreaNode): string {
  const byId = new Map(allAreas(nodes).map((n) => [n.id, n]));
  const names: string[] = [];
  const seen = new Set<number>();
  let cur: AreaNode | undefined = area;
  while (cur && !seen.has(cur.id)) {
    seen.add(cur.id);
    names.push(cur.name);
    cur = cur.parent_id === null ? undefined : byId.get(cur.parent_id);
  }
  return names.reverse().join(" › ");
}

/** Danh sách chọn cha. `level` là cấp của địa bàn đang sửa; null (trang tạo) thì gộp tỉnh và xã,
 *  `area-parent.ts` ẩn bớt khi người dùng chọn cấp. Chỉ lấy nút đang dùng, trừ `keepId` (cha hiện tại). */
export function parentOptions(
  tree: readonly AreaNode[],
  level: AreaLevel | null,
  keepId?: number | null,
): FieldOption[] {
  const parentLevel = level === null ? null : PARENT_LEVEL[level];
  const wanted: AreaLevel[] =
    level === null ? ["PROVINCE", "COMMUNE"] : parentLevel ? [parentLevel] : [];
  return allAreas(tree)
    .filter((a) => wanted.includes(a.level as AreaLevel))
    .filter((a) => a.status === "ACTIVE" || a.id === keepId)
    .map((a) => ({ value: a.id, label: `${levelLabel(a.level)}: ${areaPathLabel(tree, a)}` }));
}

/** Id → cấp, cho script lọc ô «Thuộc» theo cấp đang chọn. */
export function parentLevelMap(tree: readonly AreaNode[]): Record<string, string> {
  return Object.fromEntries(
    allAreas(tree)
      .filter((a) => a.level !== "VILLAGE")
      .map((a) => [String(a.id), a.level]),
  );
}

export const LEVEL_OPTIONS: FieldOption[] = (Object.keys(LEVEL_LABEL) as AreaLevel[]).map((v) => ({
  value: v,
  label: LEVEL_LABEL[v],
}));

export function createFields(tree: readonly AreaNode[]): FieldDef[] {
  return [
    { name: "level", label: "Cấp", type: "select", required: true, options: LEVEL_OPTIONS },
    {
      name: "code",
      label: "Mã",
      required: true,
      mono: true,
      maxlength: 40,
      hint: "Chữ, số, gạch nối; không đổi được sau khi tạo",
    },
    { name: "name", label: "Tên", required: true, maxlength: 200 },
    {
      name: "parent_id",
      label: "Thuộc",
      type: "select",
      options: parentOptions(tree, null),
      hint: "Xã chọn Tỉnh, Thôn chọn Xã; Tỉnh để trống",
    },
    { name: "former_name", label: "Địa danh cũ", maxlength: 200, wide: true },
  ];
}

export function editFields(tree: readonly AreaNode[], area: AreaNode): FieldDef[] {
  const level = isAreaLevel(area.level) ? area.level : null;
  const fields: FieldDef[] = [
    { name: "level_label", label: "Cấp", value: levelLabel(area.level), readonly: true },
    { name: "code", label: "Mã", value: area.code, readonly: true, mono: true },
    { name: "name", label: "Tên", value: area.name, required: true, maxlength: 200 },
  ];
  if (level && PARENT_LEVEL[level]) {
    fields.push({
      name: "parent_id",
      label: "Thuộc",
      type: "select",
      value: area.parent_id,
      options: parentOptions(tree, level, area.parent_id).filter((o) => o.value !== area.id),
      required: true,
    });
  }
  fields.push({
    name: "former_name",
    label: "Địa danh cũ",
    value: area.former_name,
    maxlength: 200,
    wide: true,
  });
  return fields;
}
