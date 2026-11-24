#!/usr/bin/env node
import { spawn } from "node:child_process";
const input = process.argv[2];
if (!input) { console.error("Usage: npm run probe -- <input>"); process.exit(2); }
const p = spawn("ffprobe", ["-v","error","-show_format","-show_streams","-of","json",input], {stdio:"inherit"});
p.on("error", e => { console.error("Could not start ffprobe. Install FFmpeg (includes ffprobe).",e.message); process.exit(1); });
p.on("exit", c => process.exit(c ?? 1));
