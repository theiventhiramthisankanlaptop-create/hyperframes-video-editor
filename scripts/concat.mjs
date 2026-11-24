#!/usr/bin/env node
import { spawn } from "node:child_process";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve, basename, join } from "node:path";

const files = process.argv.slice(2);
if (files.length < 2) {
  console.error("Usage: npm run concat -- clip1.mp4 clip2.mp4 [clip3.mp4 ...] output.mp4");
  process.exit(2);
}
const output = resolve(files.pop());
const inputs = files.map(resolve);
const dir = await mkdtemp(join(tmpdir(), "video-concat-"));
const list = join(dir, "inputs.txt");
const quote = p => "file '" + p.replaceAll("'", "'\\''") + "'";
try {
  await writeFile(list, inputs.map(quote).join("\n") + "\n");
  const args = ["-hide_banner","-y","-f","concat","-safe","0","-i",list,"-c:v","libx264","-preset","medium","-crf","18","-c:a","aac","-b:a","192k","-movflags","+faststart",output];
  const code = await new Promise((resolveCode, reject) => {
    const p = spawn("ffmpeg", args, {stdio:"inherit"});
    p.on("error", reject); p.on("exit", c => resolveCode(c ?? 1));
  });
  process.exitCode = code;
} catch (e) {
  console.error("Concat failed. Check FFmpeg installation and input paths.", e.message);
  process.exitCode = 1;
} finally { await rm(dir, {recursive:true,force:true}); }
