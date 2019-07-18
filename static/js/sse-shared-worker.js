const workerConnections = []
let sharedEventSource = false

onconnect = function(e) {
  const port = e.ports[0]
  workerConnections.push(port)
  port.start()

  if (!sharedEventSource) {
    sharedEventSource = new EventSource("/sse")
    sharedEventSource.onmessage = function(message) {
      workerConnections.forEach(function(connection) {
        connection.postMessage(message.data)
      })
    }
  }
}
