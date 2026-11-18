/**
 * news-image-20261117 — entry program.
 *
 * Copies the pre-rendered front-page image (entry.png, built at authoring
 * time with PIL and real Noto fonts) into the grader's output directory.
 *
 * The output must be byte-identical on every run, so this program does no
 * rendering, no timestamps and no randomness: it only reads the bundled PNG,
 * validates it against the competition limits, and writes an exact copy.
 *
 * Node 22, standard library only. No network access. The code uses no
 * TypeScript-only syntax, so it also passes a plain `node --check`.
 */
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1_048_576; // 1 MiB, the competition cap
const MAX_SIDE = 1024; // widest / tallest allowed side, in pixels

// The PNG file signature: 89 50 4E 47 0D 0A 1A 0A.
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message) {
  console.error(`news-image-20261117: ERROR: ${message}`);
  process.exit(1);
}

/** Read the 13-byte IHDR chunk and return [width, height] in pixels. */
function readPngDimensions(bytes) {
  if (bytes.length < 33) {
    fail(`entry.png is only ${bytes.length} bytes, too short to hold a PNG header`);
  }
  if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail("entry.png does not start with the PNG signature — not a PNG file");
  }
  const chunkType = bytes.toString("latin1", 12, 16);
  if (chunkType !== "IHDR") {
    fail(`first PNG chunk is ${JSON.stringify(chunkType)}, expected "IHDR"`);
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  // A well-formed PNG ends with a 12-byte IEND chunk (length 0 + "IEND" + CRC).
  if (bytes.toString("latin1", bytes.length - 8, bytes.length - 4) !== "IEND") {
    fail("entry.png does not end with an IEND chunk — file looks truncated");
  }
  return [width, height];
}

function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = resolve(here, "entry.png");

  let info;
  try {
    info = statSync(source);
  } catch {
    fail(`cannot find bundled image at ${source}`);
  }
  if (!info.isFile()) {
    fail(`bundled image at ${source} is not a regular file`);
  }
  if (info.size > MAX_BYTES) {
    fail(`entry.png is ${info.size} bytes, over the ${MAX_BYTES} byte cap`);
  }
  if (info.size === 0) {
    fail("entry.png is empty");
  }

  const bytes = readFileSync(source);
  const [width, height] = readPngDimensions(bytes);
  if (width === 0 || height === 0) {
    fail(`entry.png has an impossible size of ${width}x${height}`);
  }
  if (width > MAX_SIDE || height > MAX_SIDE) {
    fail(`entry.png is ${width}x${height}, over the ${MAX_SIDE}x${MAX_SIDE} cap`);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  const target = join(outDir, "entry.png");
  mkdirSync(outDir, { recursive: true });
  copyFileSync(source, target);

  // Re-read what we just wrote and confirm it matches the source byte for byte.
  const written = readFileSync(target);
  if (!written.equals(bytes)) {
    fail("written output does not match the bundled entry.png");
  }

  console.log(
    `news-image-20261117: wrote ${target} (${width}x${height}, ${written.length} bytes)`,
  );
}

main();
