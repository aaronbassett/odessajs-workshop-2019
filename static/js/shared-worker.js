const workerConnections = []
let sharedWebSocket = false

function createSharedWebSocket() {
  sharedWebSocket = new WebSocket("wss://nexmo-odessajs.ngrok.io/")

  sharedWebSocket.onmessage = function(e) {
    workerConnections.forEach(function(connection) {
      let data = JSON.parse(e.data)
      connection.postMessage(data)
    })
  }

  console.log('Shared WebSocket opened')
}

onconnect = function(e) {
  const port = e.ports[0]
  workerConnections.push(port)
  port.start()

  if (!sharedWebSocket) {
    createSharedWebSocket()

    sharedWebSocket.onclose = function(e) {
      console.log('Shared WebSocket closed')
      createSharedWebSocket()
    }

  } else {
    sharedWebSocket.send("Ping")
  }
}
