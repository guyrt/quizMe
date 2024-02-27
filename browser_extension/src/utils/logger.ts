const shouldLog = true

export function log(message: any) {
  if (!shouldLog) {
    return
  }
  const t = new Date().toISOString()
  console.log(`[${t}] ${message}`)
}
