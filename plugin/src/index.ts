type HookInput = { sessionID?: string; tool?: string; [key: string]: unknown };
type EventEnvelope = { event: unknown };
type PluginHooks = {
  "tool.execute.before"?: (input: HookInput) => Promise<void>;
  "tool.execute.after"?: (input: HookInput) => Promise<void>;
  event?: (input: EventEnvelope) => Promise<void>;
};

type LooseRecord = Record<string, unknown>;

const daemon = process.env.OPENCODE_LIVE_VOICE_URL ?? "http://127.0.0.1:8765/v1/events";

function record(value: unknown): LooseRecord | undefined {
  return value && typeof value === "object" ? (value as LooseRecord) : undefined;
}

async function emit(body: Record<string, unknown>): Promise<void> {
  try {
    await fetch(daemon, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(300),
    });
  } catch {
    // Voice integration must never block or fail OpenCode.
  }
}

export async function OpenCodeLiveEvents(): Promise<PluginHooks> {
  return {
    "tool.execute.before": async (input) => {
      await emit({
        event: "tool_started",
        session_id: input.sessionID,
        message: String(input.tool ?? "tool"),
        metadata: { tool: input.tool },
      });
    },
    "tool.execute.after": async (input) => {
      await emit({
        event: "tool_finished",
        session_id: input.sessionID,
        message: String(input.tool ?? "tool"),
        metadata: { tool: input.tool },
      });
    },
    event: async ({ event }) => {
      const e = record(event);
      const type = e?.type;
      const props = record(e?.properties);
      const sessionID = typeof props?.sessionID === "string" ? props.sessionID : undefined;
      if (type === "session.status") {
        const status = record(props?.status);
        await emit({ event: "status", session_id: sessionID, message: String(status?.type ?? "") });
      }
      if (type === "todo.updated") {
        await emit({ event: "todo", session_id: sessionID, message: "todo updated" });
      }
      if (type === "message.part.updated") {
        // Do not forward raw code/assistant content by default.
        await emit({ event: "message_delta", session_id: sessionID, message: "assistant output updated" });
      }
    },
  };
}

export default OpenCodeLiveEvents;
