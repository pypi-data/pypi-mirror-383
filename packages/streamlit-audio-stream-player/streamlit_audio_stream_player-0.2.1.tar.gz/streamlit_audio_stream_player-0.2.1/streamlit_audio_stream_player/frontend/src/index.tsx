import React from "react"
import { createRoot } from "react-dom/client"
import BarVisualizerComponent from "./BarVisualizerComponent"

const container = document.getElementById("root")
if (container) {
  const root = createRoot(container)
  root.render(
    <React.StrictMode>
      <BarVisualizerComponent />
    </React.StrictMode>
  )
}

