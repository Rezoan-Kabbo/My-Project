package com.example.typetutor;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class Server {
    public static Map<SocketWrapper,String> clientMap = new HashMap<>();
    public static int i=1;
    public static boolean gameStarted = false;
    public static final int REQUIRED_PLAYERS = 2;
    public static int idx;

    public static void broadcastStart() {
        for (SocketWrapper wrapper : clientMap.keySet()) {
            try {
                wrapper.write("START");  //  send START signal
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
public static void main(String[] args) throws IOException {
        Random rand = new Random();
        idx= rand.nextInt(2);
    ServerSocket server = new ServerSocket(5050);  // IPv4 Address: 192.168.0.103
    System.out.println("Server started...");
    while (true) {
        Socket socket = server.accept();
        System.out.println("New client connected");

        ClientHandler handler = new ClientHandler(socket);
        handler.start(); // Start the thread
//        if (Server.clientMap.size() >= Server.REQUIRED_PLAYERS && !Server.gameStarted) {
//            Server.gameStarted = true;
//            Server.broadcastStart(); //  send "START" to all
//        }
    }
}
}
