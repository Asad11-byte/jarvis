import { useEffect } from "react";

export default function VoiceWidget() {
  useEffect(() => {
    // Prevent adding the widget twice
    if (document.getElementById("livekit-widget")) return;

    const script = document.createElement("script");
    script.id = "livekit-widget";
    script.src = "https://cloud.livekit.io/embed-popup.js";

    script.setAttribute("data-lk-agent", "CA_csCtFDXkYXSc");
    script.setAttribute("data-lk-color", "#121b44");
    script.setAttribute("data-lk-theme", "dark");

    document.body.appendChild(script);
  }, []);

  return null;
}