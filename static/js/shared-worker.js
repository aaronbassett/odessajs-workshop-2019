const workerConnections = []
let sharedWebSocket = false

onconnect = function(e) {
  const port = e.ports[0]
  workerConnections.push(port)
  port.start()

  if (!sharedWebSocket) {
    sharedWebSocket = new WebSocket("wss://nexmo-odessajs.ngrok.io/")

    sharedWebSocket.onmessage = function(e) {
      workerConnections.forEach(function(connection) {
        let data = JSON.parse(e.data)
        connection.postMessage(data)
      })
    }

    setInterval(function() {
      console.log('Keeping alive')
      sharedWebSocket.send("Keep Alive")
    }, 5000)
  } else {
    sharedWebSocket.send("Ping")
  }
}
