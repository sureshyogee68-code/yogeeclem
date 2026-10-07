// Render ssito-motion.html frame by frame and encode an MP4 (1920x1080, 30 fps).
// Usage: node render.mjs [fps] [out.mp4]
import { createRequire } from 'node:module';
import { spawn, execSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const dir = path.dirname(fileURLToPath(import.meta.url));
// Use a local `playwright` if installed, otherwise the globally installed one.
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require(path.join(execSync('npm root -g').toString().trim(), 'playwright')); }
const { chromium } = pw;
const STILLS = process.argv[2] === 'stills' ? process.argv[3].split(',').map(Number) : null;
const FPS = STILLS ? 30 : +(process.argv[2] || 30);
const OUT = process.argv[3] || path.join(dir, 'ssito-production-motion.mp4');
const AUDIO = path.join(dir, 'audio', 'soundtrack.wav');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(dir, 'ssito-motion.html')).href + '?render');
await page.evaluate(() => document.fonts.ready);
const duration = await page.evaluate(() => window.DURATION);
const frames = Math.round(duration * FPS);
if (STILLS) {
  fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
  for (const t of STILLS) {
    await page.evaluate(t => window.renderAt(t), t);
    await page.screenshot({ path: path.join(dir, 'stills', `t${String(t).padStart(5, '0')}.png`) });
  }
  await browser.close();
  process.exit(0);
}

const args = ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-'];
if (fs.existsSync(AUDIO)) args.push('-i', AUDIO, '-c:a', 'aac', '-b:a', '192k', '-shortest');
args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });

for (let i = 0; i < frames; i++) {
  await page.evaluate(t => window.renderAt(t), i / FPS);
  const buf = await page.screenshot({ type: 'png' });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % FPS === 0) process.stdout.write(`\rframe ${i}/${frames}`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log(`\nDone → ${OUT}`);
