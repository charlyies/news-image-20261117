// Entry program for the make.fun bounty "news-image-20261117".
//
// Copies the pre-built ./entry.png into $MAKEFUN_OUTPUT_DIR/entry.png
// (default /output). Node 22, standard library only. Written without
// TypeScript-only syntax so it also passes a plain `node --check`.
//
// Before copying, the PNG is validated by hand:
//   * the 8-byte PNG signature,
//   * the IHDR chunk (width / height / bit depth / colour type),
//   * the size caps: at most 1 MiB and at most 1024x1024 pixels.
// Any mismatch is a hard failure (non-zero exit, no file written).

import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const MAX_BYTES = 1024 * 1024;
const MAX_WIDTH = 1024;
const MAX_HEIGHT = 1024;

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message) {
  console.error(`error: ${message}`);
  process.exit(1);
}

function checkPng(bytes) {
  if (bytes.length < 33) {
    fail(`entry.png is only ${bytes.length} bytes, too short to be a PNG`);
  }
  if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail("entry.png does not start with the PNG signature");
  }
  // First chunk must be IHDR: 4-byte length, 4-byte type, then width/height.
  const chunkType = bytes.subarray(12, 16).toString("latin1");
  if (chunkType !== "IHDR") {
    fail(`first PNG chunk is ${chunkType}, expected IHDR`);
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  const bitDepth = bytes[24];
  const colourType = bytes[25];
  if (width === 0 || height === 0) {
    fail(`IHDR dimensions are ${width}x${height}`);
  }
  if (width > MAX_WIDTH || height > MAX_HEIGHT) {
    fail(`image is ${width}x${height}, over the ${MAX_WIDTH}x${MAX_HEIGHT} cap`);
  }
  if (bitDepth !== 8) {
    fail(`unsupported bit depth ${bitDepth}, expected 8`);
  }
  if (colourType !== 2 && colourType !== 6) {
    fail(`unsupported colour type ${colourType}, expected 2 (RGB) or 6 (RGBA)`);
  }
  return { width, height };
}

function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");
  if (!existsSync(source)) {
    fail(`entry.png not found next to main.ts (${source})`);
  }

  const bytes = readFileSync(source);
  if (bytes.length > MAX_BYTES) {
    fail(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);
  }
  const { width, height } = checkPng(bytes);

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");
  // Copy via an explicit write so the output is byte-identical to the source.
  writeFileSync(target, bytes);
  const written = statSync(target).size;
  if (written !== bytes.length) {
    fail(`wrote ${written} bytes but the source is ${bytes.length} bytes`);
  }
  // Sanity: the file on disk must be the same buffer we validated.
  const again = readFileSync(target);
  if (!again.equals(bytes)) {
    fail("output file differs from the validated source");
  }
  console.log(`wrote ${target} (${width}x${height}, ${written} bytes)`);
}

main();
