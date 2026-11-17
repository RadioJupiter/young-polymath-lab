/* Offline read-aloud using the browser's speechSynthesis only. No network, no accounts.
   Lesson text is always narrated in English (en-US). Only short vocabulary clips
   (buttons with data-say and data-lang) may be voiced in Spanish or Latin. */
(function () {
  function supported() {
    return typeof window !== "undefined" && "speechSynthesis" in window && typeof SpeechSynthesisUtterance !== "undefined";
  }

  function loadVoices() {
    try { return window.speechSynthesis.getVoices() || []; } catch (e) { return []; }
  }

  /* Short vocabulary clips only. Lesson narration always uses en-US. */
  function resolveClipLang(code) {
    if (!code) return { request: "en-US", label: "English" };
    var c = String(code).toLowerCase();
    if (c === "la" || c.indexOf("la-") === 0) {
      return { request: "it-IT", fallback: ["it-IT", "it"], label: "Latin (Italian voice, an approximation)" };
    }
    if (c.indexOf("es") === 0) {
      return { request: "es-MX", fallback: ["es-MX", "es-US", "es-ES", "es"], label: "Spanish" };
    }
    if (c.indexOf("it") === 0) return { request: "it-IT", fallback: ["it-IT", "it"], label: "Italian" };
    return { request: "en-US", fallback: ["en-US", "en"], label: "English" };
  }

  function pickVoice(spec) {
    var voices = loadVoices();
    if (!voices.length) return null;
    var wanted = [spec.request].concat(spec.fallback || []);
    var i, j, lang;
    for (i = 0; i < wanted.length; i++) {
      var tag = wanted[i].toLowerCase().replace("_", "-");
      for (j = 0; j < voices.length; j++) {
        lang = (voices[j].lang || "").toLowerCase().replace("_", "-");
        if (lang === tag) return voices[j];
      }
    }
    for (i = 0; i < wanted.length; i++) {
      var p = wanted[i].toLowerCase().split("-")[0];
      for (j = 0; j < voices.length; j++) {
        lang = (voices[j].lang || "").toLowerCase().replace("_", "-");
        if (lang === p || lang.indexOf(p + "-") === 0) return voices[j];
      }
    }
    return null;
  }

  function visibleText(root) {
    if (!root) return "";
    if (root.getAttribute && root.getAttribute("data-say")) return root.getAttribute("data-say");
    var clone = root.cloneNode(true);
    var drop = clone.querySelectorAll("button, .listen, .teach-tools, .listen-note, .no-speak, script, style, summary, .word-clip");
    for (var i = 0; i < drop.length; i++) drop[i].parentNode && drop[i].parentNode.removeChild(drop[i]);
    return (clone.innerText || clone.textContent || "").replace(/\s+/g, " ").trim();
  }

  var currentBtn = null;

  function setIdle(btn) {
    if (!btn) return;
    btn.removeAttribute("aria-pressed");
    if (btn.dataset.label) btn.textContent = btn.dataset.label;
  }

  function stop() {
    try { window.speechSynthesis.cancel(); } catch (e) {}
    setIdle(currentBtn);
    currentBtn = null;
  }

  function speak(text, spec, btn) {
    if (!text) return;
    stop();
    if (!supported()) {
      announce(btn, "Listening is not available in this browser. Read the lesson on the page.");
      return;
    }
    var u = new SpeechSynthesisUtterance(text);
    u.lang = spec.request;
    u.rate = 0.92;
    u.pitch = 1;
    var voice = pickVoice(spec);
    if (voice) {
      u.voice = voice;
      u.lang = voice.lang || spec.request;
    }
    u.onend = function () { setIdle(btn); if (currentBtn === btn) currentBtn = null; };
    u.onerror = function () {
      setIdle(btn);
      if (currentBtn === btn) currentBtn = null;
      announce(btn, "This browser could not play a voice. You can still read the lesson on the page.");
    };
    currentBtn = btn;
    if (btn) {
      btn.setAttribute("aria-pressed", "true");
      btn.textContent = "Stop";
    }
    window.speechSynthesis.speak(u);
  }

  function announce(btn, msg) {
    var host = btn && (btn.closest("[data-listen], .teach-tools, td, p, li, .word-clip") || btn.parentNode);
    if (!host) return;
    var note = host.querySelector(".listen-note");
    if (!note) {
      note = document.createElement("span");
      note.className = "listen-note";
      host.appendChild(note);
    }
    note.textContent = msg;
  }

  function makeButton(label) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "listen";
    b.dataset.label = label || "Listen";
    b.textContent = b.dataset.label;
    b.setAttribute("aria-label", b.dataset.label);
    return b;
  }

  function enhance() {
    var ok = supported();
    document.querySelectorAll("[data-listen]").forEach(function (box) {
      if (box.querySelector(":scope > .teach-tools")) return;
      var tools = document.createElement("div");
      tools.className = "teach-tools";
      var btn = makeButton("Listen");
      /* Block narration is always English, even inside a language lesson. */
      btn.setAttribute("data-lang", "en-US");
      tools.appendChild(btn);
      var note = document.createElement("span");
      note.className = "listen-note";
      if (!ok) {
        note.textContent = "Listening is not available in this browser. Read the lesson on the page.";
        btn.disabled = true;
      }
      tools.appendChild(note);
      box.insertBefore(tools, box.firstChild);
    });
    document.querySelectorAll("table.wordlist[data-voice]").forEach(function (table) {
      var clip = table.getAttribute("data-voice");
      table.querySelectorAll("tbody tr").forEach(function (tr) {
        var cell = tr.querySelector("th,td");
        if (!cell || cell.querySelector("button.listen")) return;
        var word = (cell.getAttribute("data-say") || "").trim();
        if (!word) {
          /* Use the first text node / residual text after any existing buttons. */
          var copy = cell.cloneNode(true);
          copy.querySelectorAll("button, .listen-note").forEach(function (n) { n.remove(); });
          word = (copy.textContent || "").replace(/\s+/g, " ").trim();
        }
        if (!word) return;
        var btn = makeButton("Hear word");
        btn.className = "listen listen-inline";
        btn.setAttribute("data-say", word);
        btn.setAttribute("data-lang", clip);
        cell.insertBefore(btn, cell.firstChild);
        if (!ok) btn.disabled = true;
      });
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("button.listen");
    if (!btn) return;
    e.preventDefault();
    if (btn.disabled) return;
    if (currentBtn === btn) { stop(); return; }
    var clipText = btn.getAttribute("data-say");
    var spec;
    if (clipText) {
      spec = resolveClipLang(btn.getAttribute("data-lang"));
      speak(clipText, spec, btn);
      return;
    }
    /* Read the surrounding explanation in English. */
    var box = btn.closest("[data-listen]");
    speak(visibleText(box || btn.parentNode), { request: "en-US", fallback: ["en-US", "en"], label: "English" }, btn);
  });

  if (supported()) {
    loadVoices();
    if (typeof window.speechSynthesis.onvoiceschanged !== "undefined") {
      window.speechSynthesis.addEventListener("voiceschanged", function () { loadVoices(); });
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhance);
  } else {
    enhance();
  }
})();
