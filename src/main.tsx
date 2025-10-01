
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

const rootEl = document.getElementById("root") || document.createElement("div");
if (!document.getElementById("root")) {
  rootEl.id = "root";
  document.body.appendChild(rootEl);
}

createRoot(rootEl).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
