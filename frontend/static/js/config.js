// Central runtime configuration for the frontend.
//
// Resolution order:
//   1. window.__API_ROOT__  - set this in a page's <head> BEFORE other scripts load
//      if the frontend and backend are on different domains (e.g. separate
//      Render/Railway services). Example:
//        <script>window.__API_ROOT__ = "https://your-backend.onrender.com";</script>
//   2. Same-origin default  - works when nginx (see frontend/Dockerfile + nginx.conf)
//      reverse-proxies /api/v1/* to the backend container, so the browser can
//      just call the page's own origin.
//   3. Local-file fallback  - if you open an .html file directly (file://) during
//      development with no server in front, we fall back to the backend running
//      on localhost:8000.
export const API_ROOT =
    window.__API_ROOT__ ||
    (window.location.protocol === "file:"
        ? "http://127.0.0.1:8000"
        : window.location.origin);
