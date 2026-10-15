"use strict";

// Pruebas de comportamiento sin navegador ni paquetes: DOM y storage sintéticos.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

const script = fs.readFileSync(path.join(__dirname, "../assets/site.js"), "utf8");
const key = "erni.ai-engineer-roadmap.v0.4.checklist";
const ids = ["roadmap", "datacamp", "proyecto1", "proyecto2", "cloudquest", "certificacion"];

function element(id) {
  return {
    id, checked: false, hidden: true, textContent: "", events: {},
    addEventListener(name, callback) { this.events[name] = callback; },
  };
}

function page({ saved = new Map(), blocked = "", confirm = true, checklist = true } = {}) {
  const boxes = checklist ? ids.map((id) => element(`check-${id}`)) : [];
  const elements = Object.fromEntries(["checklist-status", "reset-progress"].map((id) => [id, element(id)]));
  const events = {};
  const tabs = {
    scrollLeft: 0, width: 288,
    getBoundingClientRect() { return { left: 0, right: this.width }; },
    querySelector() { return { getBoundingClientRect: () => ({ left: 640 - this.scrollLeft, right: 840 - this.scrollLeft }) }; },
  };
  const window = {
    scrollY: 700,
    confirm: () => confirm,
    addEventListener(name, callback) { events[name] = callback; },
    cancelAnimationFrame() {},
    requestAnimationFrame(callback) { callback(); return 1; },
    get localStorage() {
      if (blocked === "getter") throw new Error("Storage unavailable");
      return {
        getItem(name) {
          if (blocked === "read") throw new Error("Read unavailable");
          return saved.get(name) ?? null;
        },
        setItem(name, value) {
          if (blocked === "write") throw new Error("Quota exceeded");
          saved.set(name, value);
        },
      };
    },
  };
  vm.runInNewContext(script, {
    window,
    document: {
      querySelector: () => tabs,
      querySelectorAll: () => boxes,
      getElementById: (id) => checklist ? elements[id] : null,
    },
  });
  return { boxes, elements, saved, tabs, window, events };
}

test("checkbox changes survive reload and store only known booleans", () => {
  const first = page();
  first.boxes[4].checked = true;
  first.boxes[4].events.change();
  const restored = page({ saved: first.saved });
  assert.equal(restored.boxes[4].checked, true);
  assert.match(restored.elements["checklist-status"].textContent, /1 de 6/);
  const data = JSON.parse(first.saved.get(key));
  assert.deepEqual(Object.keys(data), ids.map((id) => `check-${id}`));
  assert.equal(Object.values(data).every((value) => typeof value === "boolean"), true);
  assert.equal(first.saved.size, 1);
});

for (const blocked of ["getter", "read", "write"]) {
  test(`storage ${blocked} failure leaves usable memory-only checkboxes`, () => {
    const current = page({ blocked });
    current.boxes[0].checked = true;
    current.boxes[0].events.change();
    assert.match(current.elements["checklist-status"].textContent, /1 de 6/);
    assert.match(current.elements["checklist-status"].textContent, /solo en esta visita/);
    assert.equal(current.saved.size, 0);
  });
}

for (const invalid of ["not json", "null", "[]", '{"check-roadmap":"true"}', JSON.stringify(Object.fromEntries(ids.map((id) => [`unexpected-${id}`, false])))]) {
  test(`invalid local payload falls back without reflecting or restoring it: ${invalid.slice(0, 22)}`, () => {
    const current = page({ saved: new Map([[key, invalid]]) });
    assert.equal(current.boxes.some((box) => box.checked), false);
    assert.match(current.elements["checklist-status"].textContent, /datos no son válidos/);
    assert.equal(current.saved.get(key), invalid);
  });
}

test("reset requires confirmation and persists the cleared state", () => {
  const current = page();
  current.boxes[0].checked = true;
  current.boxes[0].events.change();
  const cancelled = page({ saved: current.saved, confirm: false });
  cancelled.elements["reset-progress"].events.click();
  assert.equal(cancelled.boxes[0].checked, true);
  current.elements["reset-progress"].events.click();
  assert.equal(page({ saved: current.saved }).boxes.some((box) => box.checked), false);
});

test("explicit reset repairs incompatible local state", () => {
  const current = page({ saved: new Map([[key, "invalid"]]) });
  current.elements["reset-progress"].events.click();
  assert.match(current.elements["checklist-status"].textContent, /Guardado local/);
  assert.equal(Object.values(JSON.parse(current.saved.get(key))).every((value) => value === false), true);
});

test("active tab is visible on entry and resize without changing vertical position", () => {
  const current = page({ checklist: false });
  assert.equal(current.tabs.scrollLeft, 552);
  current.tabs.width = 250;
  current.events.resize();
  assert.equal(current.tabs.scrollLeft, 590);
  assert.equal(current.window.scrollY, 700);
  assert.equal(current.saved.size, 0);
});

test("status text is a personal reminder and the reset needs no mentor wording", () => {
  const current = page();
  assert.match(current.elements["checklist-status"].textContent, /recordatorio personal/);
  assert.doesNotMatch(current.elements["checklist-status"].textContent, /mentor/i);
  assert.equal(current.elements["reset-progress"].hidden, false);
});

test("pages without a checklist do not touch storage", () => {
  assert.equal(page({ checklist: false }).saved.size, 0);
});
