#!/usr/bin/env npx tsx
/**
 * Cursor orchestrator — delegates to pipeline_runner.py;
 * optionally invokes @cursor/sdk when CURSOR_API_KEY is set and --invoke-sdk is passed.
 */

import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "../..");
const RUNNER = join(ROOT, "scripts", "pipeline_runner.py");
const PYTHON = process.env.PYTHON ?? "python3";

function parseArgs(argv: string[]): { runnerArgs: string[]; invokeSdk: boolean; syncSkills: boolean } {
  const runnerArgs: string[] = ["--platform", "cursor"];
  let invokeSdk = false;
  let syncSkills = false;

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--invoke-sdk") {
      invokeSdk = true;
      continue;
    }
    if (a === "--sync-skills") {
      syncSkills = true;
      continue;
    }
    // --auto is handled by pipeline_runner.py (cursor agent -p)
    runnerArgs.push(a);
  }

  return { runnerArgs, invokeSdk, syncSkills };
}

async function invokeCursorSdk(promptPath: string): Promise<void> {
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey) {
    console.warn("CURSOR_API_KEY not set — skip SDK invoke. Use prompt file manually.");
    return;
  }

  let Agent: typeof import("@cursor/sdk").Agent;
  try {
    ({ Agent } = await import("@cursor/sdk"));
  } catch {
    console.warn("@cursor/sdk not installed. Run: npm install @cursor/sdk");
    return;
  }

  const prompt = readFileSync(promptPath, "utf-8");
  console.log(`Invoking Cursor SDK for prompt: ${promptPath}`);

  const result = await Agent.prompt(prompt, {
    apiKey,
    model: { id: process.env.CURSOR_MODEL ?? "composer-2.5" },
    local: { cwd: ROOT },
  });

  console.log("SDK status:", result.status);
  if (result.result) {
    console.log(result.result.slice(0, 500) + (result.result.length > 500 ? "..." : ""));
  }
}

function main(): void {
  const { runnerArgs, invokeSdk, syncSkills } = parseArgs(process.argv.slice(2));

  if (syncSkills) {
    spawnSync("bash", [join(ROOT, "scripts", "sync-skills.sh")], {
      stdio: "inherit",
      cwd: ROOT,
    });
  }

  const run = spawnSync(PYTHON, [RUNNER, ...runnerArgs], {
    stdio: "inherit",
    cwd: ROOT,
  });

  if (run.status !== 0) {
    process.exit(run.status ?? 1);
  }

  if (invokeSdk) {
    const promptsDir = join(ROOT, "workspace", "artifacts", "prompts");
    if (!existsSync(promptsDir)) {
      console.warn("No prompts directory — run pipeline first.");
      return;
    }
    const files = readdirSync(promptsDir).filter((f) => f.endsWith(".md")).sort();
    if (files[0]) {
      void invokeCursorSdk(join(promptsDir, files[0]));
    }
  }
}

main();
