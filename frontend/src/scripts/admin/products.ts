import { ApiRequestError, api } from "./api";
import { LOGIN_PATH } from "./next";
import { type ProductResult, readProductForm, STATUS_LABEL } from "./product-form";

const form = document.querySelector<HTMLFormElement>("#product-form");
const errorBox = document.querySelector<HTMLElement>("#product-error");
const resultBox = document.querySelector<HTMLElement>("#product-result");
const resultName = document.querySelector<HTMLElement>("#product-result-name");
const resultStatus = document.querySelector<HTMLElement>("#product-result-status");
const resultLink = document.querySelector<HTMLElement>("#product-result-link");
const resultHref = document.querySelector<HTMLAnchorElement>("#product-result-href");
const publishButton = document.querySelector<HTMLButtonElement>("#product-publish");

let current: ProductResult | null = null;

function showError(message: string): void {
  if (!errorBox) return;
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function handleError(error: unknown): void {
  if (error instanceof ApiRequestError) {
    if (error.status === 401) {
      window.location.assign(LOGIN_PATH);
      return;
    }
    showError(error.message);
    return;
  }
  showError("Không kết nối được máy chủ, bạn thử lại sau ít phút");
}

function render(product: ProductResult): void {
  current = product;
  if (!resultBox || !resultName || !resultStatus) return;
  resultBox.hidden = false;
  resultName.textContent = product.name;
  resultStatus.textContent = STATUS_LABEL[product.status] ?? product.status;
  const published = product.status === "PUBLISHED";
  if (publishButton) publishButton.hidden = published;
  if (resultLink && resultHref) {
    resultLink.hidden = !published;
    const href = `/san-pham/${encodeURIComponent(product.slug)}`;
    resultHref.href = href;
    resultHref.textContent = href;
  }
}

if (form) {
  const submit = form.querySelector<HTMLButtonElement>("button[type=submit]");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (errorBox) errorBox.hidden = true;
    const body = readProductForm(new FormData(form));
    if (typeof body === "string") {
      showError(body);
      return;
    }
    if (submit) submit.disabled = true;
    try {
      render(await api.post<ProductResult>("/products", body));
    } catch (error) {
      handleError(error);
    } finally {
      if (submit) submit.disabled = false;
    }
  });
}

publishButton?.addEventListener("click", async () => {
  if (!current) return;
  if (errorBox) errorBox.hidden = true;
  publishButton.disabled = true;
  try {
    render(await api.patch<ProductResult>(`/products/${current.id}`, { status: "PUBLISHED" }));
  } catch (error) {
    handleError(error);
  } finally {
    publishButton.disabled = false;
  }
});
