import type { APIRoute } from "astro";

export const prerender = false;

/** Healthcheck của compose: 200 "ok", không gọi API, no-store. */
export const GET: APIRoute = () =>
  new Response("ok", { headers: { "Content-Type": "text/plain", "Cache-Control": "no-store" } });
