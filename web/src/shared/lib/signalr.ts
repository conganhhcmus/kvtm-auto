import * as signalR from '@microsoft/signalr'

// --- Screen Hub (/hubs/screen) ---

let screenConnection: signalR.HubConnection | null = null

export function getScreenConnection(): signalR.HubConnection {
  if (!screenConnection) {
    screenConnection = new signalR.HubConnectionBuilder()
      .withUrl('/hubs/screen')
      .withAutomaticReconnect()
      .build()
  }
  return screenConnection
}

export async function startScreenConnection(): Promise<void> {
  await ensureConnected(getScreenConnection())
}

// --- Log Hub (/hubs/logs) ---

let logConnection: signalR.HubConnection | null = null

export function getLogConnection(): signalR.HubConnection {
  if (!logConnection) {
    logConnection = new signalR.HubConnectionBuilder()
      .withUrl('/hubs/logs')
      .withAutomaticReconnect()
      .build()
  }
  return logConnection
}

export async function startLogConnection(): Promise<void> {
  await ensureConnected(getLogConnection())
}

// --- Shared helper ---

async function ensureConnected(conn: signalR.HubConnection): Promise<void> {
  if (conn.state === signalR.HubConnectionState.Connected) return
  if (conn.state === signalR.HubConnectionState.Disconnected) {
    await conn.start()
    return
  }
  // Connecting, Reconnecting, or Disconnecting — wait up to 10 s
  const deadline = Date.now() + 10_000
  while ((conn.state as signalR.HubConnectionState) !== signalR.HubConnectionState.Connected) {
    if (Date.now() > deadline) throw new Error('SignalR connection timed out')
    await new Promise((resolve) => setTimeout(resolve, 100))
  }
}
