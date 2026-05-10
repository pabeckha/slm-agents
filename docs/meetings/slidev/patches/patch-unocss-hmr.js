/**
 * Patches @unocss/vite to disable the HMR update loop.
 *
 * Problem: UnoCSS v66 + Slidev v52 creates an infinite HMR cycle on dev
 * server start. The large safelist (~660 utility classes) from Slidev's
 * internal components causes continuous CSS regeneration:
 *   1. UnoCSS extracts tokens from modules during transform
 *   2. New tokens trigger onInvalidate -> invalidate() -> sendUpdate()
 *   3. Browser receives CSS update, sends "unocss:hmr" back to server
 *   4. Server regenerates CSS, hash changes, sends another update
 *   5. Repeat forever (100+ cycles observed)
 *
 * Fix: remove the sendUpdate() calls from both the invalidate timer and
 * the websocket HMR handler. CSS is still generated correctly on initial
 * load; only the post-load HMR feedback loop is broken.
 *
 * Side effect: editing slides won't hot-reload UnoCSS utility classes.
 * This is irrelevant here since the theme uses plain CSS, not utilities.
 */

const fs = require('fs');
const path = require('path');

const target = path.join(
  __dirname, '..', 'node_modules', '@unocss', 'vite', 'dist', 'index.mjs'
);

const original = fs.readFileSync(target, 'utf8');
let code = original;

// Patch 1: remove sendUpdate from invalidate timer
code = code.replace(
  /invalidateTimer = setTimeout\(\(\) => \{\s*lastServedHash\.clear\(\);\s*sendUpdate\(ids\);\s*\}/,
  'invalidateTimer = setTimeout(() => {\n\t\t\tlastServedHash.clear();\n\t\t}'
);

// Patch 2: remove sendUpdate from websocket HMR handler
code = code.replace(
  /if \(lastServedHash\.get\(layer\) !== preHash\) sendUpdate\(entries\);/,
  '// sendUpdate removed to prevent HMR loop'
);

if (code === original) {
  console.error('Patch failed: no regex matched. @unocss/vite may have changed its internals.');
  process.exit(1);
}

fs.writeFileSync(target, code, 'utf8');
console.log('Patched @unocss/vite HMR loop');
