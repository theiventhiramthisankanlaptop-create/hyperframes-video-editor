#!/usr/bin/env node
import { spawn } from "node:child_process";
import { access } from "node:fs/promises";
import { constants } from "node:fs";

const [input, start, duration, output] = process.argv.slice(2);
if (!input || !start || !duration || !output) {
  console.error("Usage: npm run cut -- <input> <start> <duration> <output>");
  console.error('Example: npm run cut -- footage.mp4 00:00:05 12 clips/clip-01.mp4');
  process.exit(2);
}
try { await access(input, constants.R_OK); } catch {
  console.error(`Cannot read input file: ${input}`);
  process.exit(1);
}
if (!/^\d{2}:\d{2}:\d{2}(\.\d+)?$/.test(start) && !/^\d+(\.\d+)?$/.test(start)) {
  console.error("Start must be seconds or HH:MM:SS[.ms]."); process.exit(2);
}
if (!/^\d+(\.\d+)?$/.test(duration)) {
  console.error("Duration must be a positive number of seconds."); process.exit(2);
}
const args = ["-hide_banner","-y","-ss",start,"-i",input,"-t",duration,"-map","0:v:0?","-map","0:a:0?","-c:v","libx264","-preset","medium","-crf","18","-c:a","aac","-b:a","192k","-movflags","+faststart",output];
const child = spawn("ffmpeg", args, { stdio: "inherit" });
child.on("error", e => { console.error("Could not start FFmpeg. Install FFmpeg and ensure it is on PATH.", e.message); process.exit(1); });
child.on("exit", code => process.exit(code ?? 1));
