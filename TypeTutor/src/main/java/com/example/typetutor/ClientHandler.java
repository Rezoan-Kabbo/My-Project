package com.example.typetutor;

import java.io.IOException;
import java.net.Socket;

public class ClientHandler extends Thread {
    private SocketWrapper socketWrapper;
    public ClientHandler(Socket socket) throws IOException {
        this.socketWrapper = new SocketWrapper(socket);
        String playerName = "Player" + Server.i++;
        Server.clientMap.put(socketWrapper, playerName);
    }

    @Override
    public void run() {
        try {
            while (true) {
                String msg= (String) socketWrapper.read();
                if (msg.equals("GET_CLIENT_COUNT")) {
                    socketWrapper.write("CLIENT_COUNT:" + Server.clientMap.size());
                } else if (msg.equals("DISCONNECT")) {
                    System.out.println("Disconnecting " + Server.clientMap.get(socketWrapper));
                    Server.clientMap.remove(socketWrapper);
                    socketWrapper.closeConnection();
                    break; // exit thread
                }
                else if (msg.equals("PARAGRAPH NO.")) {
                    // socketWrapper.write(Server.idx);
                    socketWrapper.write(1);
                }
                else if (msg.startsWith("Progress:")) {
                    int progress = Integer.parseInt(msg.split(":")[1]);
                    System.out.println("Received progress from client: " + progress);
                    // Broadcast to all other clients except the sender
                    for (SocketWrapper sw : Server.clientMap.keySet()) {
                        if (sw != this.socketWrapper) {
                            System.out.println("Sending OPPONENT_PROGRESS: " + progress + " to " + Server.clientMap.get(sw));
                            sw.write("OPPONENT_PROGRESS:" + progress);
                        }
                    }
                }
                else if (msg.startsWith("WPM:")) {
                    int wpm= Integer.parseInt(msg.split(":")[1]);
                    System.out.println("Received progress from client: " + wpm);
                    // Broadcast to all other clients except the sender
                    for (SocketWrapper sw : Server.clientMap.keySet()) {
                        if (sw != this.socketWrapper) {
                            System.out.println("Sending OPPONENT_WPM: " + wpm + " to " + Server.clientMap.get(sw));
                            sw.write("OPPONENT_WPM:" + wpm);
                        }
                    }
                }
                else if (msg.startsWith("Accuracy:")) {
                    float accuracy= Float.parseFloat(msg.split(":")[1]);
                    System.out.println("Received accuracy: " + accuracy);
                    for (SocketWrapper sw : Server.clientMap.keySet()) {
                        if (sw != this.socketWrapper) {
                            System.out.println("Sending OPPONENT_ACCURACY: " + accuracy);
                            sw.write("OPPONENT_ACCURACY:" + accuracy);
                        }
                    }
                }
                // Start the game when enough players are connected
            }
        } catch (Exception e) {
            System.out.println("Client disconnected unexpectedly.");
            Server.clientMap.remove(socketWrapper);
            try {
                socketWrapper.closeConnection();
            } catch (IOException ioException) {
                ioException.printStackTrace();
            }
        }
    }
}

