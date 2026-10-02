package com.example.typetutor;

public class Client {
    public Client(String serverAddress, int serverPort) {
        try {
            SocketWrapper socketWrapper = new SocketWrapper(serverAddress, serverPort);
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
